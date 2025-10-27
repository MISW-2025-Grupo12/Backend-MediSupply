import pytest
import json
import uuid
from unittest.mock import patch, Mock
from .conftest import get_usuarios_url

class TestAPICliente:
    """Test para la API de clientes usando SQLite"""
    
    def test_crear_cliente_exitoso(self, client):
        """Test crear cliente exitoso"""
        # Arrange
        cliente_data = {
            'nombre': 'Juan Pérez',
            'email': 'juan@email.com',
            'identificacion': '1234567890',
            'telefono': '1234567890',
            'direccion': 'Calle 123 #45-67'
        }
        
        # Mock del comando
        with patch('aplicacion.comandos.crear_cliente.CrearClienteHandler.handle') as mock_ejecutar:
            mock_cliente = Mock()
            mock_cliente.id = str(uuid.uuid4())
            mock_cliente.nombre = 'Juan Pérez'
            mock_cliente.email = 'juan@email.com'
            mock_cliente.identificacion = '1234567890'
            mock_cliente.telefono = '1234567890'
            mock_cliente.direccion = 'Calle 123 #45-67'
            mock_cliente.estado = 'ACTIVO'
            mock_ejecutar.return_value = mock_cliente
            
            # Act
            response = client.post(get_usuarios_url('clientes'), 
                                 data=json.dumps(cliente_data),
                                 content_type='application/json')
            
            # Assert
            assert response.status_code == 201
            assert response.mimetype == 'application/json'
            
            response_data = json.loads(response.data.decode())
            assert response_data['nombre'] == 'Juan Pérez'
            assert response_data['email'] == 'juan@email.com'
            assert response_data['identificacion'] == '1234567890'
            assert response_data['telefono'] == '1234567890'
            assert response_data['direccion'] == 'Calle 123 #45-67'
    
    def test_crear_cliente_sin_json(self, client):
        """Test crear cliente sin JSON"""
        # Act
        response = client.post(get_usuarios_url('clientes'))
        
        # Assert
    
        assert response.status_code == 500
        assert response.mimetype == 'application/json'
        
        response_data = json.loads(response.data.decode())
        assert 'error' in response_data
    
    def test_crear_cliente_json_invalido(self, client):
        """Test crear cliente con JSON inválido"""
        # Act
        response = client.post(get_usuarios_url('clientes'),
                             data='invalid json',
                             content_type='application/json')
        
        # Assert
        assert response.status_code == 500
        response_data = json.loads(response.data.decode())
        assert 'error' in response_data
    
    def test_crear_cliente_error_interno(self, client):
        """Test crear cliente con error interno"""
        # Arrange
        cliente_data = {
            'nombre': 'Juan Pérez',
            'email': 'juan@email.com',
            'telefono': '1234567890',
            'direccion': 'Calle 123 #45-67'
        }
        
        with patch('aplicacion.comandos.crear_cliente.CrearClienteHandler.handle') as mock_ejecutar:
            mock_ejecutar.side_effect = Exception("Error interno")
            
            # Act
            response = client.post(get_usuarios_url('clientes'),
                                 data=json.dumps(cliente_data),
                                 content_type='application/json')
            
            # Assert
            assert response.status_code == 500
            response_data = json.loads(response.data.decode())
            assert 'error' in response_data
            assert 'Error interno del servidor' in response_data['error']
    
    def test_obtener_clientes_exitoso(self, client):
        """Test obtener clientes exitoso"""
        # Arrange
        with patch('aplicacion.consultas.obtener_clientes.ObtenerClientesHandler.handle') as mock_ejecutar:
            mock_clientes = [
                Mock(id=str(uuid.uuid4()), nombre='Juan Pérez',
                     email='juan@email.com', identificacion='1234567890', telefono='1234567890', direccion='Calle 123 #45-67', estado='ACTIVO'),
                Mock(id=str(uuid.uuid4()), nombre='María García',
                     email='maria@email.com', identificacion='0987654321', telefono='0987654321', direccion='Avenida 456 #78-90', estado='ACTIVO')
            ]
            mock_ejecutar.return_value = mock_clientes
            
            # Act
            response = client.get(get_usuarios_url('clientes'))
            
            # Assert
            assert response.status_code == 200
            assert response.mimetype == 'application/json'
            
            response_data = json.loads(response.data.decode())
            assert len(response_data) == 2
            assert response_data[0]['nombre'] == 'Juan Pérez'
            assert response_data[1]['nombre'] == 'María García'
    
    def test_obtener_clientes_lista_vacia(self, client):
        """Test obtener clientes con lista vacía"""
        # Arrange
        with patch('aplicacion.consultas.obtener_clientes.ObtenerClientesHandler.handle') as mock_ejecutar:
            mock_ejecutar.return_value = []
            
            # Act
            response = client.get(get_usuarios_url('clientes'))
            
            # Assert
            assert response.status_code == 200
            response_data = json.loads(response.data.decode())
            assert response_data == []
    
    def test_obtener_clientes_error(self, client):
        """Test obtener clientes con error"""
        # Arrange
        with patch('aplicacion.consultas.obtener_clientes.ObtenerClientesHandler.handle') as mock_ejecutar:
            mock_ejecutar.side_effect = Exception("Error de base de datos")
            
            # Act
            response = client.get(get_usuarios_url('clientes'))
            
            # Assert
            assert response.status_code == 500
            response_data = json.loads(response.data.decode())
            assert 'error' in response_data
            assert 'Error interno del servidor' in response_data['error']
    
    def test_obtener_cliente_por_id_exitoso(self, client):
        """Test obtener cliente por ID exitoso"""
        # Arrange
        cliente_id = str(uuid.uuid4())
        with patch('aplicacion.consultas.obtener_cliente_por_id.ObtenerClientePorIdHandler.handle') as mock_ejecutar:
            mock_cliente = Mock()
            mock_cliente.id = cliente_id
            mock_cliente.nombre = 'Juan Pérez'
            mock_cliente.email = 'juan@email.com'
            mock_cliente.identificacion = '1234567890'
            mock_cliente.telefono = '1234567890'
            mock_cliente.direccion = 'Calle 123 #45-67'
            mock_cliente.estado = 'ACTIVO'
            mock_ejecutar.return_value = mock_cliente
            
            # Act
            response = client.get(f"{get_usuarios_url('clientes')}/{cliente_id}")
            
            # Assert
            assert response.status_code == 200
            assert response.mimetype == 'application/json'
            
            response_data = json.loads(response.data.decode())
            assert response_data['id'] == cliente_id
            assert response_data['nombre'] == 'Juan Pérez'
            assert response_data['email'] == 'juan@email.com'
            assert response_data['identificacion'] == '1234567890'
            assert response_data['telefono'] == '1234567890'
            assert response_data['direccion'] == 'Calle 123 #45-67'
    
    def test_obtener_cliente_por_id_no_encontrado(self, client):
        """Test obtener cliente por ID no encontrado"""
        # Arrange
        cliente_id = str(uuid.uuid4())
        with patch('aplicacion.consultas.obtener_cliente_por_id.ObtenerClientePorIdHandler.handle') as mock_ejecutar:
            mock_ejecutar.return_value = None
            
            # Act
            response = client.get(f"{get_usuarios_url('clientes')}/{cliente_id}")
            
            # Assert
            assert response.status_code == 404
            assert response.mimetype == 'application/json'
            
            response_data = json.loads(response.data.decode())
            assert 'error' in response_data
            assert 'Cliente no encontrado' in response_data['error']
    
    def test_obtener_cliente_por_id_error(self, client):
        """Test obtener cliente por ID con error"""
        # Arrange
        cliente_id = str(uuid.uuid4())
        with patch('aplicacion.consultas.obtener_cliente_por_id.ObtenerClientePorIdHandler.handle') as mock_ejecutar:
            mock_ejecutar.side_effect = Exception("Error de base de datos")
            
            # Act
            response = client.get(f"{get_usuarios_url('clientes')}/{cliente_id}")
            
            # Assert
            assert response.status_code == 500
            response_data = json.loads(response.data.decode())
            assert 'error' in response_data
            assert 'Error interno del servidor' in response_data['error']
    
    def test_modificar_estado_cliente_exitoso(self, client):
        """Test modificar estado del cliente exitoso"""
        # Arrange
        cliente_id = str(uuid.uuid4())
        estado_data = {'estado': 'INACTIVO'}
        
        with patch('aplicacion.comandos.modificar_estado_cliente.ModificarEstadoClienteHandler.handle') as mock_ejecutar:
            mock_cliente = Mock()
            mock_cliente.id = cliente_id
            mock_cliente.nombre = 'Juan Pérez'
            mock_cliente.email = 'juan@email.com'
            mock_cliente.identificacion = '1234567890'
            mock_cliente.telefono = '1234567890'
            mock_cliente.direccion = 'Calle 123 #45-67'
            mock_cliente.estado = 'INACTIVO'
            mock_ejecutar.return_value = mock_cliente
            
            # Act
            response = client.put(f"{get_usuarios_url('clientes')}/{cliente_id}/estado",
                                data=json.dumps(estado_data),
                                content_type='application/json')
            
            # Assert
            assert response.status_code == 200
            assert response.mimetype == 'application/json'
            
            response_data = json.loads(response.data.decode())
            assert response_data['id'] == cliente_id
            assert response_data['nombre'] == 'Juan Pérez'
            assert response_data['email'] == 'juan@email.com'
            assert response_data['identificacion'] == '1234567890'
            assert response_data['telefono'] == '1234567890'
            assert response_data['direccion'] == 'Calle 123 #45-67'
            assert response_data['estado'] == 'INACTIVO'
    
    def test_modificar_estado_cliente_sin_estado(self, client):
        """Test modificar estado del cliente sin campo estado"""
        # Arrange
        cliente_id = str(uuid.uuid4())
        estado_data = {'otro_campo': 'valor'}
        
        # Act
        response = client.put(f"{get_usuarios_url('clientes')}/{cliente_id}/estado",
                             data=json.dumps(estado_data),
                             content_type='application/json')
        
        # Assert
        assert response.status_code == 400
        assert response.mimetype == 'application/json'
        
        response_data = json.loads(response.data.decode())
        assert 'error' in response_data
        assert 'Se requiere el campo "estado"' in response_data['error']
    
    def test_modificar_estado_cliente_estado_invalido(self, client):
        """Test modificar estado del cliente con estado inválido"""
        # Arrange
        cliente_id = str(uuid.uuid4())
        estado_data = {'estado': 'ESTADO_INEXISTENTE'}
        
        with patch('aplicacion.comandos.modificar_estado_cliente.ModificarEstadoClienteHandler.handle') as mock_ejecutar:
            mock_ejecutar.side_effect = ValueError("El estado 'ESTADO_INEXISTENTE' no es válido")
            
            # Act
            response = client.put(f"{get_usuarios_url('clientes')}/{cliente_id}/estado",
                                data=json.dumps(estado_data),
                                content_type='application/json')
            
            # Assert
            assert response.status_code == 400
            assert response.mimetype == 'application/json'
            
            response_data = json.loads(response.data.decode())
            assert 'error' in response_data
            assert 'El estado' in response_data['error']
    
    def test_modificar_estado_cliente_no_encontrado(self, client):
        """Test modificar estado del cliente no encontrado"""
        # Arrange
        cliente_id = str(uuid.uuid4())
        estado_data = {'estado': 'INACTIVO'}
        
        with patch('aplicacion.comandos.modificar_estado_cliente.ModificarEstadoClienteHandler.handle') as mock_ejecutar:
            mock_ejecutar.side_effect = ValueError(f"Cliente con ID {cliente_id} no encontrado")
            
            # Act
            response = client.put(f"{get_usuarios_url('clientes')}/{cliente_id}/estado",
                                data=json.dumps(estado_data),
                                content_type='application/json')
            
            # Assert
            assert response.status_code == 400
            assert response.mimetype == 'application/json'
            
            response_data = json.loads(response.data.decode())
            assert 'error' in response_data
            assert 'Cliente con ID' in response_data['error']
    
    def test_modificar_estado_cliente_error_interno(self, client):
        """Test modificar estado del cliente con error interno"""
        # Arrange
        cliente_id = str(uuid.uuid4())
        estado_data = {'estado': 'INACTIVO'}
        
        with patch('aplicacion.comandos.modificar_estado_cliente.ModificarEstadoClienteHandler.handle') as mock_ejecutar:
            mock_ejecutar.side_effect = Exception("Error de base de datos")
            
            # Act
            response = client.put(f"{get_usuarios_url('clientes')}/{cliente_id}/estado",
                                data=json.dumps(estado_data),
                                content_type='application/json')
            
            # Assert
            assert response.status_code == 500
            assert response.mimetype == 'application/json'
            
            response_data = json.loads(response.data.decode())
            assert 'error' in response_data
            assert 'Error interno del servidor' in response_data['error']
