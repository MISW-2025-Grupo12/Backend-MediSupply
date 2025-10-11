import pytest
import json
import uuid
from unittest.mock import patch, Mock
from .test_config import app, client

class TestAPIProveedor:
    """Test para la API de proveedores usando SQLite"""
    
    def test_crear_proveedor_exitoso(self, client):
        """Test crear proveedor exitoso"""
        # Arrange
        proveedor_data = {
            'nombre': 'Farmacia Central',
            'email': 'contacto@farmacia.com',
            'direccion': 'Calle 123 #45-67'
        }
        
        # Mock del comando
        with patch('src.aplicacion.comandos.crear_proveedor.ejecutar_comando') as mock_ejecutar:
            mock_proveedor = Mock()
            mock_proveedor.id = str(uuid.uuid4())
            mock_proveedor.nombre = 'Farmacia Central'
            mock_proveedor.email = 'contacto@farmacia.com'
            mock_proveedor.direccion = 'Calle 123 #45-67'
            mock_ejecutar.return_value = mock_proveedor
            
            # Act
            response = client.post('/api/proveedores', 
                                 data=json.dumps(proveedor_data),
                                 content_type='application/json')
            
            # Assert
            assert response.status_code == 201
            assert response.mimetype == 'application/json'
            
            response_data = json.loads(response.data.decode())
            assert response_data['nombre'] == 'Farmacia Central'
            assert response_data['email'] == 'contacto@farmacia.com'
            assert response_data['direccion'] == 'Calle 123 #45-67'
    
    def test_crear_proveedor_sin_json(self, client):
        """Test crear proveedor sin JSON"""
        # Act
        response = client.post('/api/proveedores')
        
        # Assert
        assert response.status_code == 400
        assert response.mimetype == 'application/json'
        
        response_data = json.loads(response.data.decode())
        assert 'error' in response_data
        assert 'Se requiere un JSON válido' in response_data['error']
    
    def test_crear_proveedor_json_invalido(self, client):
        """Test crear proveedor con JSON inválido"""
        # Act
        response = client.post('/api/proveedores',
                             data='invalid json',
                             content_type='application/json')
        
        # Assert
        assert response.status_code == 400
        response_data = json.loads(response.data.decode())
        assert 'error' in response_data
    
    def test_crear_proveedor_error_validacion(self, client):
        """Test crear proveedor con error de validación"""
        # Arrange
        proveedor_data = {
            'nombre': 'Farmacia Central',
            'email': 'contacto@farmacia.com',
            'direccion': 'Calle 123 #45-67'
        }
        
        with patch('src.aplicacion.comandos.crear_proveedor.ejecutar_comando') as mock_ejecutar:
            mock_ejecutar.side_effect = ValueError("Error de validación")
            
            # Act
            response = client.post('/api/proveedores',
                                 data=json.dumps(proveedor_data),
                                 content_type='application/json')
            
            # Assert
            assert response.status_code == 400
            response_data = json.loads(response.data.decode())
            assert 'error' in response_data
            assert 'Error de validación' in response_data['error']
    
    def test_crear_proveedor_error_interno(self, client):
        """Test crear proveedor con error interno"""
        # Arrange
        proveedor_data = {
            'nombre': 'Farmacia Central',
            'email': 'contacto@farmacia.com',
            'direccion': 'Calle 123 #45-67'
        }
        
        with patch('src.aplicacion.comandos.crear_proveedor.ejecutar_comando') as mock_ejecutar:
            mock_ejecutar.side_effect = Exception("Error interno")
            
            # Act
            response = client.post('/api/proveedores',
                                 data=json.dumps(proveedor_data),
                                 content_type='application/json')
            
            # Assert
            assert response.status_code == 500
            response_data = json.loads(response.data.decode())
            assert 'error' in response_data
            assert 'Error interno del servidor' in response_data['error']
    
    def test_obtener_proveedores_exitoso(self, client):
        """Test obtener proveedores exitoso"""
        # Arrange
        with patch('src.aplicacion.consultas.obtener_proveedores.ejecutar_consulta') as mock_ejecutar:
            mock_proveedores = [
                Mock(id=str(uuid.uuid4()), nombre='Farmacia Central', 
                     email='contacto@farmacia.com', direccion='Calle 123 #45-67'),
                Mock(id=str(uuid.uuid4()), nombre='Farmacia Norte', 
                     email='norte@farmacia.com', direccion='Avenida 456 #78-90')
            ]
            mock_ejecutar.return_value = mock_proveedores
            
            # Act
            response = client.get('/api/proveedores')
            
            # Assert
            assert response.status_code == 200
            assert response.mimetype == 'application/json'
            
            response_data = json.loads(response.data.decode())
            assert len(response_data) == 2
            assert response_data[0]['nombre'] == 'Farmacia Central'
            assert response_data[1]['nombre'] == 'Farmacia Norte'
    
    def test_obtener_proveedores_lista_vacia(self, client):
        """Test obtener proveedores con lista vacía"""
        # Arrange
        with patch('src.aplicacion.consultas.obtener_proveedores.ejecutar_consulta') as mock_ejecutar:
            mock_ejecutar.return_value = []
            
            # Act
            response = client.get('/api/proveedores')
            
            # Assert
            assert response.status_code == 200
            response_data = json.loads(response.data.decode())
            assert response_data == []
    
    def test_obtener_proveedores_error(self, client):
        """Test obtener proveedores con error"""
        # Arrange
        with patch('src.aplicacion.consultas.obtener_proveedores.ejecutar_consulta') as mock_ejecutar:
            mock_ejecutar.side_effect = Exception("Error de base de datos")
            
            # Act
            response = client.get('/api/proveedores')
            
            # Assert
            assert response.status_code == 500
            response_data = json.loads(response.data.decode())
            assert 'error' in response_data
            assert 'Error interno del servidor' in response_data['error']
    
    def test_obtener_proveedor_por_id_exitoso(self, client):
        """Test obtener proveedor por ID exitoso"""
        # Arrange
        proveedor_id = str(uuid.uuid4())
        with patch('src.aplicacion.consultas.obtener_proveedor_por_id.ejecutar_consulta') as mock_ejecutar:
            mock_proveedor = Mock()
            mock_proveedor.id = proveedor_id
            mock_proveedor.nombre = 'Farmacia Central'
            mock_proveedor.email = 'contacto@farmacia.com'
            mock_proveedor.direccion = 'Calle 123 #45-67'
            mock_ejecutar.return_value = mock_proveedor
            
            # Act
            response = client.get(f'/api/proveedores/{proveedor_id}')
            
            # Assert
            assert response.status_code == 200
            assert response.mimetype == 'application/json'
            
            response_data = json.loads(response.data.decode())
            assert response_data['id'] == proveedor_id
            assert response_data['nombre'] == 'Farmacia Central'
            assert response_data['email'] == 'contacto@farmacia.com'
            assert response_data['direccion'] == 'Calle 123 #45-67'
    
    def test_obtener_proveedor_por_id_no_encontrado(self, client):
        """Test obtener proveedor por ID no encontrado"""
        # Arrange
        proveedor_id = str(uuid.uuid4())
        with patch('src.aplicacion.consultas.obtener_proveedor_por_id.ejecutar_consulta') as mock_ejecutar:
            mock_ejecutar.return_value = None
            
            # Act
            response = client.get(f'/api/proveedores/{proveedor_id}')
            
            # Assert
            assert response.status_code == 404
            assert response.mimetype == 'application/json'
            
            response_data = json.loads(response.data.decode())
            assert 'error' in response_data
            assert 'Proveedor no encontrado' in response_data['error']
    
    def test_obtener_proveedor_por_id_error(self, client):
        """Test obtener proveedor por ID con error"""
        # Arrange
        proveedor_id = str(uuid.uuid4())
        with patch('src.aplicacion.consultas.obtener_proveedor_por_id.ejecutar_consulta') as mock_ejecutar:
            mock_ejecutar.side_effect = Exception("Error de base de datos")
            
            # Act
            response = client.get(f'/api/proveedores/{proveedor_id}')
            
            # Assert
            assert response.status_code == 500
            response_data = json.loads(response.data.decode())
            assert 'error' in response_data
            assert 'Error interno del servidor' in response_data['error']
