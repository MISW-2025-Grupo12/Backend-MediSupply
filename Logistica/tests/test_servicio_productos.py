import pytest
import sys
import os
from unittest.mock import Mock, patch
import requests

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from infraestructura.servicio_productos import ServicioProductos
from .conftest import get_service_url

class TestServicioProductos:
    def setup_method(self):
        self.servicio = ServicioProductos()

    @patch('infraestructura.servicio_productos.requests.get')
    def test_obtener_producto_por_id_exitoso(self, mock_get):
        # Mock de respuesta exitosa
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": "prod-1",
            "nombre": "Producto Test",
            "precio": 100.0
        }
        mock_get.return_value = mock_response
        
        resultado = self.servicio.obtener_producto_por_id("prod-1")
        
        assert resultado is not None
        assert resultado["id"] == "prod-1"
        assert resultado["nombre"] == "Producto Test"
        mock_get.assert_called_once_with(get_service_url('productos_service') + "/prod-1", timeout=5)

    @patch('infraestructura.servicio_productos.requests.get')
    def test_obtener_producto_por_id_no_encontrado(self, mock_get):
        # Mock de respuesta 404
        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response
        
        resultado = self.servicio.obtener_producto_por_id("prod-inexistente")
        
        assert resultado is None
        mock_get.assert_called_once_with(get_service_url('productos_service') + "/prod-inexistente", timeout=5)

    @patch('infraestructura.servicio_productos.requests.get')
    def test_obtener_producto_por_id_error_servidor(self, mock_get):
        # Mock de error del servidor
        mock_response = Mock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response
        
        resultado = self.servicio.obtener_producto_por_id("prod-1")
        
        assert resultado is None
        mock_get.assert_called_once_with(get_service_url('productos_service') + "/prod-1", timeout=5)

    @patch('infraestructura.servicio_productos.requests.get')
    def test_obtener_producto_por_id_excepcion(self, mock_get):
        # Mock de excepción
        mock_get.side_effect = requests.exceptions.ConnectionError("Error de conexión")
        
        resultado = self.servicio.obtener_producto_por_id("prod-1")
        
        assert resultado is None

    @patch('infraestructura.servicio_productos.requests.get')
    def test_buscar_productos_exitoso(self, mock_get):
        # Mock de respuesta exitosa
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {"id": "prod-1", "nombre": "Producto 1"},
            {"id": "prod-2", "nombre": "Producto 2"}
        ]
        mock_get.return_value = mock_response
        
        resultado = self.servicio.buscar_productos("test", 10)
        
        assert len(resultado) == 2
        assert resultado[0]["id"] == "prod-1"
        mock_get.assert_called_once_with(
            get_service_url('productos_service'),
            params={'q': 'test', 'limite': 10},
            timeout=5
        )

    @patch('infraestructura.servicio_productos.requests.get')
    def test_buscar_productos_error_servidor(self, mock_get):
        # Mock de error del servidor
        mock_response = Mock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response
        
        resultado = self.servicio.buscar_productos("test")
        
        assert resultado == []
        mock_get.assert_called_once_with(
            get_service_url('productos_service'),
            params={'q': 'test', 'limite': 50},
            timeout=5
        )

    @patch('infraestructura.servicio_productos.requests.get')
    def test_buscar_productos_excepcion(self, mock_get):
        # Mock de excepción
        mock_get.side_effect = requests.exceptions.Timeout("Timeout")
        
        resultado = self.servicio.buscar_productos("test")
        
        assert resultado == []

    @patch('infraestructura.servicio_productos.requests.get')
    def test_obtener_todos_productos_exitoso(self, mock_get):
        # Mock de respuesta exitosa
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {"id": "prod-1", "nombre": "Producto 1"},
            {"id": "prod-2", "nombre": "Producto 2"}
        ]
        mock_get.return_value = mock_response
        
        resultado = self.servicio.obtener_todos_productos()
        
        assert len(resultado) == 2
        assert resultado[0]["id"] == "prod-1"
        mock_get.assert_called_once_with(get_service_url('productos_service'), params={'page': 1, 'page_size': 100}, timeout=5)

    @patch('infraestructura.servicio_productos.requests.get')
    def test_obtener_todos_productos_error_servidor(self, mock_get):
        # Mock de error del servidor
        mock_response = Mock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response
        
        resultado = self.servicio.obtener_todos_productos()
        
        assert resultado == []
        mock_get.assert_called_once_with(get_service_url('productos_service'), params={'page': 1, 'page_size': 100}, timeout=5)

    @patch('infraestructura.servicio_productos.requests.get')
    def test_obtener_todos_productos_excepcion(self, mock_get):
        # Mock de excepción
        mock_get.side_effect = Exception("Error general")
        
        resultado = self.servicio.obtener_todos_productos()
        
        assert resultado == []

    def test_configuracion_base_url(self):
        with patch.dict(os.environ, {'PRODUCTOS_SERVICE_URL': 'http://test:8080'}):
            servicio = ServicioProductos()
            assert servicio.base_url == 'http://test:8080'
