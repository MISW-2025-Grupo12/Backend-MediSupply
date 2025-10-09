import pytest
import sys
import os
import json
from unittest.mock import Mock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from api import create_app
from aplicacion.dto import ProveedorDTO


class TestAPIProveedor:
    
    def setup_method(self):
        """Setup para cada test"""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
    
    def test_crear_proveedor_exitoso(self):
        """Test crear proveedor exitoso via API"""
        # Arrange
        proveedor_data = {
            "nombre": "Farmacia Central",
            "email": "contacto@farmacia.com",
            "direccion": "Calle 123 #45-67"
        }
        
        with patch('aplicacion.comandos.crear_proveedor.CrearProveedorHandler') as mock_handler_class:
            mock_handler = Mock()
            mock_handler_class.return_value = mock_handler
            
            # Mock del resultado
            mock_resultado = ProveedorDTO(
                id="123e4567-e89b-12d3-a456-426614174000",
                nombre="Farmacia Central",
                email="contacto@farmacia.com",
                direccion="Calle 123 #45-67"
            )
            mock_handler.handle.return_value = mock_resultado
            
            # Act
            response = self.client.post('/api/proveedores/', 
                                      data=json.dumps(proveedor_data),
                                      content_type='application/json')
            
            # Assert
            assert response.status_code == 201
            data = json.loads(response.data)
            assert data['nombre'] == "Farmacia Central"
            assert data['email'] == "contacto@farmacia.com"
    
    def test_crear_proveedor_datos_invalidos(self):
        """Test crear proveedor con datos inválidos"""
        # Arrange
        proveedor_data = {
            "nombre": "",  # Nombre vacío
            "email": "contacto@farmacia.com",
            "direccion": "Calle 123 #45-67"
        }
        
        with patch('aplicacion.comandos.crear_proveedor.CrearProveedorHandler') as mock_handler_class:
            mock_handler = Mock()
            mock_handler_class.return_value = mock_handler
            mock_handler.handle.side_effect = ValueError("El nombre no puede estar vacío")
            
            # Act
            response = self.client.post('/api/proveedores/', 
                                      data=json.dumps(proveedor_data),
                                      content_type='application/json')
            
            # Assert
            assert response.status_code == 400
            data = json.loads(response.data)
            assert 'error' in data
    
    def test_obtener_proveedores_exitoso(self):
        """Test obtener todos los proveedores via API"""
        # Arrange
        with patch('aplicacion.consultas.obtener_proveedores.ObtenerProveedoresHandler') as mock_handler_class:
            mock_handler = Mock()
            mock_handler_class.return_value = mock_handler
            
            # Mock del resultado
            mock_proveedores = [
                ProveedorDTO(
                    id="123e4567-e89b-12d3-a456-426614174000",
                    nombre="Farmacia Central",
                    email="contacto@farmacia.com",
                    direccion="Calle 123 #45-67"
                ),
                ProveedorDTO(
                    id="456e7890-e89b-12d3-a456-426614174001",
                    nombre="Farmacia Norte",
                    email="norte@farmacia.com",
                    direccion="Calle 456 #78-90"
                )
            ]
            mock_handler.handle.return_value = mock_proveedores
            
            # Act
            response = self.client.get('/api/proveedores/')
            
            # Assert
            assert response.status_code == 200
            data = json.loads(response.data)
            assert len(data) == 2
            assert data[0]['nombre'] == "Farmacia Central"
            assert data[1]['nombre'] == "Farmacia Norte"
    
    def test_obtener_proveedores_vacio(self):
        """Test obtener proveedores cuando no hay proveedores"""
        # Arrange
        with patch('aplicacion.consultas.obtener_proveedores.ObtenerProveedoresHandler') as mock_handler_class:
            mock_handler = Mock()
            mock_handler_class.return_value = mock_handler
            mock_handler.handle.return_value = []
            
            # Act
            response = self.client.get('/api/proveedores/')
            
            # Assert
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data == []
    
    def test_obtener_proveedor_por_id_exitoso(self):
        """Test obtener proveedor por ID via API"""
        # Arrange
        proveedor_id = "123e4567-e89b-12d3-a456-426614174000"
        
        with patch('aplicacion.consultas.obtener_proveedor_por_id.ObtenerProveedorPorIdHandler') as mock_handler_class:
            mock_handler = Mock()
            mock_handler_class.return_value = mock_handler
            
            # Mock del resultado
            mock_proveedor = ProveedorDTO(
                id=proveedor_id,
                nombre="Farmacia Central",
                email="contacto@farmacia.com",
                direccion="Calle 123 #45-67"
            )
            mock_handler.handle.return_value = mock_proveedor
            
            # Act
            response = self.client.get(f'/api/proveedores/{proveedor_id}')
            
            # Assert
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['id'] == proveedor_id
            assert data['nombre'] == "Farmacia Central"
    
    def test_obtener_proveedor_por_id_no_encontrado(self):
        """Test obtener proveedor por ID cuando no existe"""
        # Arrange
        proveedor_id = "123e4567-e89b-12d3-a456-426614174000"
        
        with patch('aplicacion.consultas.obtener_proveedor_por_id.ObtenerProveedorPorIdHandler') as mock_handler_class:
            mock_handler = Mock()
            mock_handler_class.return_value = mock_handler
            mock_handler.handle.return_value = None
            
            # Act
            response = self.client.get(f'/api/proveedores/{proveedor_id}')
            
            # Assert
            assert response.status_code == 404
            data = json.loads(response.data)
            assert 'error' in data
