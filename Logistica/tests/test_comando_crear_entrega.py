from datetime import datetime
from unittest.mock import MagicMock, patch

from aplicacion.comandos.crear_entrega import CrearEntrega, CrearEntregaHandler


def build_handler(cliente=None):
    repo = MagicMock()
    servicio = MagicMock()
    servicio.obtener_cliente_por_id.return_value = cliente

    with patch('aplicacion.comandos.crear_entrega.RepositorioEntregaSQLite', return_value=repo), \
            patch('aplicacion.comandos.crear_entrega.ServicioUsuarios', return_value=servicio), \
            patch('aplicacion.comandos.crear_entrega.calcular_dia_habil_siguiente', side_effect=lambda fecha: fecha):
        handler = CrearEntregaHandler()
    return handler, repo, servicio


def test_crear_entrega_exitoso():
    cliente = {'direccion': 'Calle 123'}
    handler, repo, servicio = build_handler(cliente)

    comando = CrearEntrega(
        pedido_id='pedido-1',
        cliente_id='cliente-1',
        vendedor_id='vendedor-1',
        items=[{'producto_id': 'p1', 'cantidad': 2}],
        total=100.0
    )

    resultado = handler.handle(comando)

    assert resultado['success'] is True
    assert repo.crear.called
    servicio.obtener_cliente_por_id.assert_called_once_with('cliente-1')


def test_crear_entrega_sin_ids():
    handler, repo, servicio = build_handler()

    comando = CrearEntrega(
        pedido_id='',
        cliente_id='',
        vendedor_id='vendedor-1',
        items=[],
        total=0
    )

    resultado = handler.handle(comando)

    assert resultado['success'] is False
    assert 'obligatorios' in resultado['error']
    repo.crear.assert_not_called()


def test_crear_entrega_cliente_no_encontrado():
    handler, repo, servicio = build_handler(cliente=None)

    comando = CrearEntrega(
        pedido_id='pedido-1',
        cliente_id='cliente-1',
        vendedor_id='vendedor-1',
        items=[],
        total=0
    )

    resultado = handler.handle(comando)

    assert resultado['success'] is False
    assert 'no encontrado' in resultado['error']
    repo.crear.assert_not_called()


def test_crear_entrega_cliente_sin_direccion():
    handler, repo, servicio = build_handler(cliente={'direccion': ''})

    comando = CrearEntrega(
        pedido_id='pedido-1',
        cliente_id='cliente-1',
        vendedor_id='vendedor-1',
        items=[],
        total=0
    )

    resultado = handler.handle(comando)

    assert resultado['success'] is False
    assert 'no tiene dirección' in resultado['error']
    repo.crear.assert_not_called()


def test_crear_entrega_excepcion():
    handler, repo, servicio = build_handler(cliente={'direccion': 'Calle 123'})
    repo.crear.side_effect = RuntimeError('fallo')

    comando = CrearEntrega(
        pedido_id='pedido-1',
        cliente_id='cliente-1',
        vendedor_id='vendedor-1',
        items=[],
        total=0
    )

    resultado = handler.handle(comando)

    assert resultado['success'] is False
    assert 'Error interno' in resultado['error']

