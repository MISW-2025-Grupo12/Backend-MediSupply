from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

import pytest

from aplicacion.comandos.crear_ruta import CrearRuta, CrearRutaHandler
from aplicacion.dto import EntregaDTO, RutaDTO


def build_entrega(entrega_id, fecha, estado='confirmado'):
    pedido = {'estado': estado}
    return EntregaDTO(
        id=entrega_id,
        direccion='Calle 1',
        fecha_entrega=fecha,
        pedido=pedido
    )


@pytest.fixture
def handler_mocks():
    repo_rutas = MagicMock()
    repo_rutas.entrega_ya_asignada.return_value = False
    repo_rutas.crear.return_value = RutaDTO()

    repo_entregas = MagicMock()
    repo_entregas.obtener_todos.return_value = []

    mapeador = MagicMock()
    mapeador.entidad_a_dto.return_value = RutaDTO()

    with patch('aplicacion.comandos.crear_ruta.RepositorioRutaSQLite', return_value=repo_rutas), \
            patch('aplicacion.comandos.crear_ruta.RepositorioEntregaSQLite', return_value=repo_entregas), \
            patch('aplicacion.comandos.crear_ruta.MapeadorRuta', return_value=mapeador):
        handler = CrearRutaHandler()
        yield handler, repo_rutas, repo_entregas, mapeador


def test_crear_ruta_exitoso(handler_mocks):
    handler, repo_rutas, repo_entregas, mapeador = handler_mocks

    fecha = datetime.now().replace(microsecond=0) + timedelta(days=1)
    repo_entregas.obtener_todos.return_value = [
        build_entrega('e1', fecha, estado='confirmado'),
        build_entrega('e2', fecha, estado='confirmado')
    ]

    comando = CrearRuta(
        fecha_ruta=fecha.date(),
        repartidor_id='repartidor-1',
        entregas=['e1', 'e2']
    )

    handler.handle(comando)

    assert repo_rutas.entrega_ya_asignada.call_count == 2
    assert repo_rutas.crear.called
    assert mapeador.entidad_a_dto.called


def test_crear_ruta_entrega_no_encontrada(handler_mocks):
    handler, repo_rutas, repo_entregas, _ = handler_mocks

    repo_entregas.obtener_todos.return_value = []

    comando = CrearRuta(
        fecha_ruta=datetime(2025, 11, 10).date(),
        repartidor_id='repartidor-1',
        entregas=['desconocida']
    )

    with pytest.raises(ValueError):
        handler.handle(comando)


def test_crear_ruta_entrega_con_estado_invalido(handler_mocks):
    handler, repo_rutas, repo_entregas, _ = handler_mocks

    fecha = datetime(2025, 11, 10, 10, 0, 0)
    repo_entregas.obtener_todos.return_value = [
        build_entrega('e1', fecha, estado='en_proceso')
    ]

    comando = CrearRuta(
        fecha_ruta=fecha.date(),
        repartidor_id='repartidor-1',
        entregas=['e1']
    )

    with pytest.raises(ValueError):
        handler.handle(comando)


def test_crear_ruta_entrega_fecha_distinta(handler_mocks):
    handler, repo_rutas, repo_entregas, _ = handler_mocks

    repo_entregas.obtener_todos.return_value = [
        build_entrega('e1', datetime(2025, 11, 11, 9, 0, 0))
    ]

    comando = CrearRuta(
        fecha_ruta=datetime(2025, 11, 10).date(),
        repartidor_id='repartidor-1',
        entregas=['e1']
    )

    with pytest.raises(ValueError):
        handler.handle(comando)


def test_crear_ruta_entrega_ya_asignada(handler_mocks):
    handler, repo_rutas, repo_entregas, _ = handler_mocks

    fecha = datetime(2025, 11, 10, 9, 0, 0)
    repo_entregas.obtener_todos.return_value = [
        build_entrega('e1', fecha)
    ]
    repo_rutas.entrega_ya_asignada.return_value = True

    comando = CrearRuta(
        fecha_ruta=fecha.date(),
        repartidor_id='repartidor-1',
        entregas=['e1']
    )

    with pytest.raises(ValueError):
        handler.handle(comando)

