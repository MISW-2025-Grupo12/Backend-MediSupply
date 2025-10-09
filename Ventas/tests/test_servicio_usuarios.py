import pytest
import sys
import os
from unittest.mock import Mock, patch
import requests

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from infraestructura.servicio_usuarios import ServicioUsuarios


class TestServicioUsuarios:
    
    def setup_method(self):
        self.servicio = ServicioUsuarios()
    
    @patch('requests.get')
    def test_obtener_vendedor_por_id_exitoso(self, mock_get):
        vendedor_mock = {
            'id': 'vendedor123',
            'nombre': 'Juan Pérez',
            'email': 'juan.perez@empresa.com',
            'telefono': '3001234567',
            'direccion': 'Calle 123 #45-67'
        }
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = vendedor_mock
        mock_get.return_value = mock_response
        
        resultado = self.servicio.obtener_vendedor_por_id('vendedor123')
        
        assert resultado == vendedor_mock
        mock_get.assert_called_once_with('http://localhost:5001/api/vendedores/vendedor123', timeout=5)
    
    @patch('requests.get')
    def test_obtener_vendedor_por_id_no_existe(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response
        
        resultado = self.servicio.obtener_vendedor_por_id('vendedor123')
        
        assert resultado is None
        mock_get.assert_called_once_with('http://localhost:5001/api/vendedores/vendedor123', timeout=5)
    
    @patch('requests.get')
    def test_obtener_vendedor_por_id_error_servidor(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response
        
        resultado = self.servicio.obtener_vendedor_por_id('vendedor123')
        
        assert resultado is None
        mock_get.assert_called_once_with('http://localhost:5001/api/vendedores/vendedor123', timeout=5)
    
    @patch('requests.get')
    def test_obtener_vendedor_por_id_exception(self, mock_get):
        mock_get.side_effect = requests.RequestException("Error de conexión")
        
        resultado = self.servicio.obtener_vendedor_por_id('vendedor123')
        
        assert resultado is None
        mock_get.assert_called_once_with('http://localhost:5001/api/vendedores/vendedor123', timeout=5)
    
    @patch('requests.get')
    def test_obtener_cliente_por_id_exitoso(self, mock_get):
        cliente_mock = {
            'id': 'cliente456',
            'nombre': 'Hospital San Ignacio',
            'email': 'contacto@sanignacio.com',
            'telefono': '3115566778',
            'direccion': 'Cra 11 # 89 - 76'
        }
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = cliente_mock
        mock_get.return_value = mock_response
        
        resultado = self.servicio.obtener_cliente_por_id('cliente456')
        
        assert resultado == cliente_mock
        mock_get.assert_called_once_with('http://localhost:5001/api/clientes/cliente456', timeout=5)
    
    @patch('requests.get')
    def test_obtener_cliente_por_id_no_existe(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response
        
        resultado = self.servicio.obtener_cliente_por_id('cliente456')
        
        assert resultado is None
        mock_get.assert_called_once_with('http://localhost:5001/api/clientes/cliente456', timeout=5)
    
    @patch('requests.get')
    def test_obtener_cliente_por_id_error_servidor(self, mock_get):
        mock_response = Mock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response
        
        resultado = self.servicio.obtener_cliente_por_id('cliente456')
        
        assert resultado is None
        mock_get.assert_called_once_with('http://localhost:5001/api/clientes/cliente456', timeout=5)
    
    @patch('requests.get')
    def test_obtener_cliente_por_id_exception(self, mock_get):
        mock_get.side_effect = requests.RequestException("Error de conexión")
        
        resultado = self.servicio.obtener_cliente_por_id('cliente456')
        
        assert resultado is None
        mock_get.assert_called_once_with('http://localhost:5001/api/clientes/cliente456', timeout=5)
