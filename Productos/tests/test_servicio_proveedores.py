import pytest
import sys
import os
from unittest.mock import Mock, patch
import requests

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from infraestructura.servicio_proveedores import ServicioProveedores
from .conftest import get_service_url


class TestServicioProveedores:
    
    def setup_method(self):
        """Setup para cada test"""
        self.servicio = ServicioProveedores()
    
    @patch('infraestructura.servicio_proveedores.requests.get')
    def test_obtener_proveedor_por_id_exitoso(self, mock_get):
        """Test obtener proveedor por ID exitoso"""
        # Arrange
        proveedor_id = "123e4567-e89b-12d3-a456-426614174000"
        proveedor_data = {
            'id': proveedor_id,
            'nombre': 'Farmacia Central',
            'email': 'contacto@farmacia.com',
            'direccion': 'Calle 123 #45-67'
        }
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = proveedor_data
        mock_get.return_value = mock_response
        
        # Act
        resultado = self.servicio.obtener_proveedor_por_id(proveedor_id)
        
        # Assert
        assert resultado == proveedor_data
        mock_get.assert_called_once_with(f"{get_service_url('usuarios_service')}/{proveedor_id}")
    
    @patch('infraestructura.servicio_proveedores.requests.get')
    def test_obtener_proveedor_por_id_no_encontrado(self, mock_get):
        """Test obtener proveedor por ID cuando no existe"""
        # Arrange
        proveedor_id = "123e4567-e89b-12d3-a456-426614174000"
        
        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response
        
        # Act
        resultado = self.servicio.obtener_proveedor_por_id(proveedor_id)
        
        # Assert
        assert resultado is None
        mock_get.assert_called_once_with(f"{get_service_url('usuarios_service')}/{proveedor_id}")
    
    @patch('infraestructura.servicio_proveedores.requests.get')
    def test_obtener_proveedor_por_id_error_servidor(self, mock_get):
        """Test obtener proveedor por ID con error de servidor"""
        # Arrange
        proveedor_id = "123e4567-e89b-12d3-a456-426614174000"
        
        mock_response = Mock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response
        
        # Act
        resultado = self.servicio.obtener_proveedor_por_id(proveedor_id)
        
        # Assert
        assert resultado is None
        mock_get.assert_called_once_with(f"{get_service_url('usuarios_service')}/{proveedor_id}")
    
    @patch('infraestructura.servicio_proveedores.requests.get')
    def test_obtener_proveedor_por_id_excepcion_requests(self, mock_get):
        """Test obtener proveedor por ID con excepción de requests"""
        # Arrange
        proveedor_id = "123e4567-e89b-12d3-a456-426614174000"
        mock_get.side_effect = requests.RequestException("Error de conexión")
        
        # Act
        resultado = self.servicio.obtener_proveedor_por_id(proveedor_id)
        
        # Assert
        assert resultado is None
        mock_get.assert_called_once_with(f"{get_service_url('usuarios_service')}/{proveedor_id}")
    
    @patch('infraestructura.servicio_proveedores.requests.get')
    def test_validar_proveedor_existe_exitoso(self, mock_get):
        """Test validar que proveedor existe exitosamente"""
        # Arrange
        proveedor_id = "123e4567-e89b-12d3-a456-426614174000"
        proveedor_data = {
            'id': proveedor_id,
            'nombre': 'Farmacia Central',
            'email': 'contacto@farmacia.com',
            'direccion': 'Calle 123 #45-67'
        }
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = proveedor_data
        mock_get.return_value = mock_response
        
        # Act
        resultado = self.servicio.validar_proveedor_existe(proveedor_id)
        
        # Assert
        assert resultado is True
        mock_get.assert_called_once_with(f"{get_service_url('usuarios_service')}/{proveedor_id}")
    
    @patch('infraestructura.servicio_proveedores.requests.get')
    def test_validar_proveedor_existe_no_existe(self, mock_get):
        """Test validar que proveedor no existe"""
        # Arrange
        proveedor_id = "123e4567-e89b-12d3-a456-426614174000"
        
        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response
        
        # Act
        resultado = self.servicio.validar_proveedor_existe(proveedor_id)
        
        # Assert
        assert resultado is False
        mock_get.assert_called_once_with(f"{get_service_url('usuarios_service')}/{proveedor_id}")
    
    @patch('infraestructura.servicio_proveedores.requests.get')
    def test_validar_proveedor_existe_error_servidor(self, mock_get):
        """Test validar proveedor con error de servidor"""
        # Arrange
        proveedor_id = "123e4567-e89b-12d3-a456-426614174000"
        
        mock_response = Mock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response
        
        # Act
        resultado = self.servicio.validar_proveedor_existe(proveedor_id)
        
        # Assert
        assert resultado is False
        mock_get.assert_called_once_with(f"{get_service_url('usuarios_service')}/{proveedor_id}")
    
    @patch('infraestructura.servicio_proveedores.requests.get')
    def test_validar_proveedor_existe_excepcion_requests(self, mock_get):
        """Test validar proveedor con excepción de requests"""
        # Arrange
        proveedor_id = "123e4567-e89b-12d3-a456-426614174000"
        mock_get.side_effect = requests.RequestException("Error de conexión")
        
        # Act
        resultado = self.servicio.validar_proveedor_existe(proveedor_id)
        
        # Assert
        assert resultado is False
        mock_get.assert_called_once_with(f"{get_service_url('usuarios_service')}/{proveedor_id}")
