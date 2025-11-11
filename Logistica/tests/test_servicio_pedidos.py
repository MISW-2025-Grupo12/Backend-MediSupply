from unittest.mock import MagicMock, patch

import pytest

from infraestructura.servicio_pedidos import ServicioPedidos


@pytest.fixture
def servicio():
    return ServicioPedidos()


def test_obtener_pedido_por_id_exitoso(servicio):
    response = MagicMock()
    response.status_code = 200
    response.json.return_value = {'id': 'pedido-1'}

    with patch('infraestructura.servicio_pedidos.requests.get', return_value=response) as mock_get:
        pedido = servicio.obtener_pedido_por_id('pedido-1')

    mock_get.assert_called_once()
    assert pedido == {'id': 'pedido-1'}


def test_obtener_pedido_por_id_no_encontrado(servicio):
    response = MagicMock()
    response.status_code = 404

    with patch('infraestructura.servicio_pedidos.requests.get', return_value=response):
        pedido = servicio.obtener_pedido_por_id('pedido-2')

    assert pedido is None


def test_obtener_pedido_por_id_error_servidor(servicio):
    response = MagicMock()
    response.status_code = 500

    with patch('infraestructura.servicio_pedidos.requests.get', return_value=response):
        pedido = servicio.obtener_pedido_por_id('pedido-3')

    assert pedido is None


def test_obtener_pedido_por_id_excepcion(servicio):
    with patch('infraestructura.servicio_pedidos.requests.get', side_effect=Exception('fallo')):
        pedido = servicio.obtener_pedido_por_id('pedido-4')

    assert pedido is None

