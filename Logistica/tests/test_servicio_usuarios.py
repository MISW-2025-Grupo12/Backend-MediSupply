from unittest.mock import MagicMock, patch

from infraestructura.servicio_usuarios import ServicioUsuarios


def build_response(status_code, payload=None, text=''):
    response = MagicMock()
    response.status_code = status_code
    response.text = text
    response.json.return_value = payload
    return response


def test_obtener_cliente_exitoso():
    servicio = ServicioUsuarios()
    response = build_response(200, {'id': 'cliente-1', 'nombre': 'Juan'})

    with patch('infraestructura.servicio_usuarios.requests.get', return_value=response) as mock_get:
        cliente = servicio.obtener_cliente_por_id('cliente-1')

    mock_get.assert_called_once()
    assert cliente['nombre'] == 'Juan'


def test_obtener_cliente_no_encontrado():
    servicio = ServicioUsuarios()
    response = build_response(404)

    with patch('infraestructura.servicio_usuarios.requests.get', return_value=response):
        cliente = servicio.obtener_cliente_por_id('cliente-2')

    assert cliente is None


def test_obtener_cliente_error_servidor():
    servicio = ServicioUsuarios()
    response = build_response(500, text='error')

    with patch('infraestructura.servicio_usuarios.requests.get', return_value=response):
        cliente = servicio.obtener_cliente_por_id('cliente-3')

    assert cliente is None


def test_obtener_cliente_excepcion():
    servicio = ServicioUsuarios()

    with patch('infraestructura.servicio_usuarios.requests.get', side_effect=Exception('fallo')):
        cliente = servicio.obtener_cliente_por_id('cliente-4')

    assert cliente is None

