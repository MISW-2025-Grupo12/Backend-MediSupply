import pytest
import json
import uuid
from unittest.mock import patch, Mock
from .conftest import get_usuarios_url

class TestAPIVendedor:
    """Test para la API de vendedores usando SQLite"""
    
    def test_crear_vendedor_exitoso(self, client):
        """Test crear vendedor exitoso"""
        # Arrange
        vendedor_data = {
            'nombre': 'Carlos López',
            'email': 'carlos@empresa.com',
            'identificacion': '1234567890',
            'telefono': '1234567890',
            'direccion': 'Calle 123 #45-67'
        }
        
        # Mock del comando
        with patch('aplicacion.comandos.crear_vendedor.CrearVendedorHandler.handle') as mock_ejecutar:
            vendedor_id = str(uuid.uuid4())
            mock_vendedor = Mock()
            mock_vendedor.id = vendedor_id
            mock_vendedor.nombre = 'Carlos López'
            mock_vendedor.email = 'carlos@empresa.com'
            mock_vendedor.identificacion = '1234567890'
            mock_vendedor.telefono = '1234567890'
            mock_vendedor.direccion = 'Calle 123 #45-67'
            mock_ejecutar.return_value = mock_vendedor
            
            # Act
            response = client.post(get_usuarios_url('vendedores'), 
                                 data=json.dumps(vendedor_data),
                                 content_type='application/json')
            
            # Assert
            assert response.status_code == 201
            assert response.mimetype == 'application/json'
            
            response_data = json.loads(response.data.decode())
            assert response_data['nombre'] == 'Carlos López'
            assert response_data['email'] == 'carlos@empresa.com'
            assert response_data['identificacion'] == '1234567890'
            assert response_data['telefono'] == '1234567890'
            assert response_data['direccion'] == 'Calle 123 #45-67'
    
    def test_crear_vendedor_sin_json(self, client):
        """Test crear vendedor sin JSON"""
        # Act
        response = client.post(get_usuarios_url('vendedores'))
        
        # Assert
        assert response.status_code == 500
        assert response.mimetype == 'application/json'
        
        response_data = json.loads(response.data.decode())
        assert 'error' in response_data
    
    def test_crear_vendedor_json_invalido(self, client):
        """Test crear vendedor con JSON inválido"""
        # Act
        response = client.post(get_usuarios_url('vendedores'),
                             data='invalid json',
                             content_type='application/json')
        
        # Assert
        assert response.status_code == 500
        response_data = json.loads(response.data.decode())
        assert 'error' in response_data
    
    def test_crear_vendedor_error_interno(self, client):
        """Test crear vendedor con error interno"""
        # Arrange
        vendedor_data = {
            'nombre': 'Carlos López',
            'email': 'carlos@empresa.com',
            'telefono': '1234567890',
            'direccion': 'Calle 123 #45-67'
        }
        
        with patch('aplicacion.comandos.crear_vendedor.CrearVendedorHandler.handle') as mock_ejecutar:
            mock_ejecutar.side_effect = Exception("Error interno")
            
            # Act
            response = client.post(get_usuarios_url('vendedores'),
                                 data=json.dumps(vendedor_data),
                                 content_type='application/json')
            
            # Assert
            assert response.status_code == 500
            response_data = json.loads(response.data.decode())
            assert 'error' in response_data
            assert 'Error interno del servidor' in response_data['error']
    
    def test_obtener_vendedores_exitoso(self, client):
        """Test obtener vendedores exitoso"""
        # Arrange
        with patch('aplicacion.consultas.obtener_vendedores.ObtenerVendedoresHandler.handle') as mock_ejecutar:
            mock_vendedores = [
                Mock(id=str(uuid.uuid4()), nombre='Carlos López', 
                     email='carlos@empresa.com', identificacion='1234567890', telefono='1234567890', direccion='Calle 123 #45-67'),
                Mock(id=str(uuid.uuid4()), nombre='Ana Martínez', 
                     email='ana@empresa.com', identificacion='0987654321', telefono='0987654321', direccion='Calle 456 #78-90')
            ]
            mock_ejecutar.return_value = mock_vendedores
            
            # Act
            response = client.get(get_usuarios_url('vendedores'))
            
            # Assert
            assert response.status_code == 200
            assert response.mimetype == 'application/json'
            
            response_data = json.loads(response.data.decode())
            assert len(response_data) == 2
            assert response_data[0]['nombre'] == 'Carlos López'
            assert response_data[1]['nombre'] == 'Ana Martínez'
    
    def test_obtener_vendedores_lista_vacia(self, client):
        """Test obtener vendedores con lista vacía"""
        # Arrange
        with patch('aplicacion.consultas.obtener_vendedores.ObtenerVendedoresHandler.handle') as mock_ejecutar:
            mock_ejecutar.return_value = []
            
            # Act
            response = client.get(get_usuarios_url('vendedores'))
            
            # Assert
            assert response.status_code == 200
            response_data = json.loads(response.data.decode())
            assert response_data == []
    
    def test_obtener_vendedores_error(self, client):
        """Test obtener vendedores con error"""
        # Arrange
        with patch('aplicacion.consultas.obtener_vendedores.ObtenerVendedoresHandler.handle') as mock_ejecutar:
            mock_ejecutar.side_effect = Exception("Error de base de datos")
            
            # Act
            response = client.get(get_usuarios_url('vendedores'))
            
            # Assert
            assert response.status_code == 500
            response_data = json.loads(response.data.decode())
            assert 'error' in response_data
            assert 'Error interno del servidor' in response_data['error']
    
    def test_obtener_vendedor_por_id_exitoso(self, client):
        """Test obtener vendedor por ID exitoso"""
        # Arrange
        vendedor_id = str(uuid.uuid4())
        with patch('aplicacion.consultas.obtener_vendedor_por_id.ObtenerVendedorPorIdHandler.handle') as mock_ejecutar:
            mock_vendedor = Mock()
            mock_vendedor.id = vendedor_id
            mock_vendedor.nombre = 'Carlos López'
            mock_vendedor.email = 'carlos@empresa.com'
            mock_vendedor.identificacion = '1234567890'
            mock_vendedor.telefono = '1234567890'
            mock_vendedor.direccion = 'Calle 123 #45-67'
            mock_ejecutar.return_value = mock_vendedor
            
            # Act
            response = client.get(f"{get_usuarios_url('vendedores')}/{vendedor_id}")
            
            # Assert
            assert response.status_code == 200
            assert response.mimetype == 'application/json'
            
            response_data = json.loads(response.data.decode())
            assert response_data['id'] == vendedor_id
            assert response_data['nombre'] == 'Carlos López'
            assert response_data['email'] == 'carlos@empresa.com'
            assert response_data['identificacion'] == '1234567890'
            assert response_data['telefono'] == '1234567890'
            assert response_data['direccion'] == 'Calle 123 #45-67'
    
    def test_obtener_vendedor_por_id_no_encontrado(self, client):
        """Test obtener vendedor por ID no encontrado"""
        # Arrange
        vendedor_id = str(uuid.uuid4())
        with patch('aplicacion.consultas.obtener_vendedor_por_id.ObtenerVendedorPorIdHandler.handle') as mock_ejecutar:
            mock_ejecutar.return_value = None
            
            # Act
            response = client.get(f"{get_usuarios_url('vendedores')}/{vendedor_id}")
            
            # Assert
            assert response.status_code == 404
            assert response.mimetype == 'application/json'
            
            response_data = json.loads(response.data.decode())
            assert 'error' in response_data
            assert 'Vendedor no encontrado' in response_data['error']
    
    def test_obtener_vendedor_por_id_error(self, client):
        """Test obtener vendedor por ID con error"""
        # Arrange
        vendedor_id = str(uuid.uuid4())
        with patch('aplicacion.consultas.obtener_vendedor_por_id.ObtenerVendedorPorIdHandler.handle') as mock_ejecutar:
            mock_ejecutar.side_effect = Exception("Error de base de datos")
            
            # Act
            response = client.get(f"{get_usuarios_url('vendedores')}/{vendedor_id}")
            
            # Assert
            assert response.status_code == 500
            response_data = json.loads(response.data.decode())
            assert 'error' in response_data
            assert 'Error interno del servidor' in response_data['error']