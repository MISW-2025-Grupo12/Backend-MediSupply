"""
Tests para la API de autenticación
"""
import pytest
import json
import uuid
from unittest.mock import patch, Mock
from infraestructura.modelos import UsuarioModel, VendedorModel, ClienteModel, ProveedorModel
from config.db import db
from dominio.excepciones import (
    EmailYaRegistradoError,
    IdentificacionYaRegistradaError,
    CredencialesInvalidasError,
    UsuarioInactivoError
)


class TestAPIAuth:
    """Tests para los endpoints de autenticación"""
    
    @pytest.fixture(autouse=True)
    def setup(self, app_context):
        """Setup para cada test"""
        with app_context.app_context():
            # Limpiar tablas antes de cada test
            UsuarioModel.query.delete()
            VendedorModel.query.delete()
            ClienteModel.query.delete()
            ProveedorModel.query.delete()
            db.session.commit()
    
    # ==================== REGISTRO VENDEDOR ====================
    
    def test_registro_vendedor_exitoso(self, client, app_context):
        """Test registro de vendedor exitoso"""
        with app_context.app_context():
            # Arrange
            vendedor_data = {
                'nombre': 'María García',
                'email': 'maria@example.com',
                'identificacion': '1234567890',
                'telefono': '3001234567',
                'direccion': 'Calle 123 #45-67',
                'password': 'Password123'
            }
            
            # Act
            response = client.post(
                '/usuarios/api/auth/registro-vendedor',
                data=json.dumps(vendedor_data),
                content_type='application/json'
            )
            
            # Assert
            assert response.status_code == 201
            response_data = json.loads(response.data.decode())
            assert 'mensaje' in response_data
            assert 'vendedor' in response_data
            assert response_data['vendedor']['email'] == vendedor_data['email']
            assert response_data['vendedor']['nombre'] == vendedor_data['nombre']
            assert 'password' not in response_data['vendedor']
    
    def test_registro_vendedor_email_duplicado(self, client, app_context):
        """Test registro de vendedor con email duplicado"""
        with app_context.app_context():
            # Arrange
            vendedor_data = {
                'nombre': 'María García',
                'email': 'maria@example.com',
                'identificacion': '1234567890',
                'telefono': '3001234567',
                'direccion': 'Calle 123 #45-67',
                'password': 'Password123'
            }
            
            # Crear primer vendedor
            client.post(
                '/usuarios/api/auth/registro-vendedor',
                data=json.dumps(vendedor_data),
                content_type='application/json'
            )
            
            # Intentar crear segundo vendedor con mismo email
            vendedor_data2 = vendedor_data.copy()
            vendedor_data2['identificacion'] = '0987654321'
            
            # Act
            response = client.post(
                '/usuarios/api/auth/registro-vendedor',
                data=json.dumps(vendedor_data2),
                content_type='application/json'
            )
            
            # Assert
            assert response.status_code == 409
            response_data = json.loads(response.data.decode())
            assert 'error' in response_data
    
    def test_registro_vendedor_identificacion_duplicada(self, client, app_context):
        """Test registro de vendedor con identificación duplicada"""
        with app_context.app_context():
            # Arrange
            vendedor_data = {
                'nombre': 'María García',
                'email': 'maria@example.com',
                'identificacion': '1234567890',
                'telefono': '3001234567',
                'direccion': 'Calle 123 #45-67',
                'password': 'Password123'
            }
            
            # Crear primer vendedor
            client.post(
                '/usuarios/api/auth/registro-vendedor',
                data=json.dumps(vendedor_data),
                content_type='application/json'
            )
            
            # Intentar crear segundo vendedor con misma identificación
            vendedor_data2 = vendedor_data.copy()
            vendedor_data2['email'] = 'otro@example.com'
            
            # Act
            response = client.post(
                '/usuarios/api/auth/registro-vendedor',
                data=json.dumps(vendedor_data2),
                content_type='application/json'
            )
            
            # Assert
            assert response.status_code == 409
            response_data = json.loads(response.data.decode())
            assert 'error' in response_data
    
    def test_registro_vendedor_sin_json(self, client):
        """Test registro de vendedor sin JSON"""
        # Act
        response = client.post('/usuarios/api/auth/registro-vendedor')
        
        # Assert
        # Flask devuelve 500 cuando no hay Content-Type: application/json
        assert response.status_code in [400, 500]
        response_data = json.loads(response.data.decode())
        assert 'error' in response_data
    
    def test_registro_vendedor_campos_faltantes(self, client):
        """Test registro de vendedor con campos faltantes"""
        # Arrange
        vendedor_data = {
            'nombre': 'María García'
            # Faltan email, identificacion, etc.
        }
        
        # Act
        response = client.post(
            '/usuarios/api/auth/registro-vendedor',
            data=json.dumps(vendedor_data),
            content_type='application/json'
        )
        
        # Assert
        assert response.status_code == 400
        response_data = json.loads(response.data.decode())
        assert 'error' in response_data
    
    # ==================== REGISTRO CLIENTE ====================
    
    def test_registro_cliente_exitoso(self, client, app_context):
        """Test registro de cliente exitoso"""
        with app_context.app_context():
            # Arrange
            cliente_data = {
                'nombre': 'Hospital San Ignacio',
                'email': 'contacto@sanignacio.com',
                'identificacion': '8601234567',
                'telefono': '3115566778',
                'direccion': 'Cra 11 # 89 - 76',
                'password': 'ClinicaPass456'
            }
            
            # Act
            response = client.post(
                '/usuarios/api/auth/registro-cliente',
                data=json.dumps(cliente_data),
                content_type='application/json'
            )
            
            # Assert
            assert response.status_code == 201
            response_data = json.loads(response.data.decode())
            assert 'mensaje' in response_data
            assert 'cliente' in response_data
            assert response_data['cliente']['email'] == cliente_data['email']
            assert response_data['cliente']['nombre'] == cliente_data['nombre']
    
    def test_registro_cliente_email_duplicado(self, client, app_context):
        """Test registro de cliente con email duplicado"""
        with app_context.app_context():
            # Arrange
            cliente_data = {
                'nombre': 'Hospital San Ignacio',
                'email': 'contacto@sanignacio.com',
                'identificacion': '8601234567',
                'telefono': '3115566778',
                'direccion': 'Cra 11 # 89 - 76',
                'password': 'ClinicaPass456'
            }
            
            # Crear primer cliente
            client.post(
                '/usuarios/api/auth/registro-cliente',
                data=json.dumps(cliente_data),
                content_type='application/json'
            )
            
            # Intentar crear segundo cliente con mismo email
            cliente_data2 = cliente_data.copy()
            cliente_data2['identificacion'] = '8609999999'
            
            # Act
            response = client.post(
                '/usuarios/api/auth/registro-cliente',
                data=json.dumps(cliente_data2),
                content_type='application/json'
            )
            
            # Assert
            assert response.status_code == 409
            response_data = json.loads(response.data.decode())
            assert 'error' in response_data
    
    # ==================== REGISTRO PROVEEDOR ====================
    
    def test_registro_proveedor_exitoso(self, client, app_context):
        """Test registro de proveedor exitoso"""
        with app_context.app_context():
            # Arrange
            proveedor_data = {
                'nombre': 'Pfizer Colombia',
                'email': 'contacto@pfizer.com.co',
                'identificacion': '9005678901',
                'telefono': '6017654321',
                'direccion': 'Carrera 9 #50-30, Bogotá',
                'password': 'PfizerPass789'
            }
            
            # Act
            response = client.post(
                '/usuarios/api/auth/registro-proveedor',
                data=json.dumps(proveedor_data),
                content_type='application/json'
            )
            
            # Assert
            assert response.status_code == 201
            response_data = json.loads(response.data.decode())
            assert 'mensaje' in response_data
            assert 'proveedor' in response_data
            assert response_data['proveedor']['email'] == proveedor_data['email']
            assert response_data['proveedor']['nombre'] == proveedor_data['nombre']
            assert response_data['proveedor']['telefono'] == proveedor_data['telefono']
    
    def test_registro_proveedor_identificacion_duplicada(self, client, app_context):
        """Test registro de proveedor con identificación duplicada"""
        with app_context.app_context():
            # Arrange
            proveedor_data = {
                'nombre': 'Pfizer Colombia',
                'email': 'contacto@pfizer.com.co',
                'identificacion': '9005678901',
                'telefono': '6017654321',
                'direccion': 'Carrera 9 #50-30, Bogotá',
                'password': 'PfizerPass789'
            }
            
            # Crear primer proveedor
            client.post(
                '/usuarios/api/auth/registro-proveedor',
                data=json.dumps(proveedor_data),
                content_type='application/json'
            )
            
            # Intentar crear segundo proveedor con misma identificación
            proveedor_data2 = proveedor_data.copy()
            proveedor_data2['email'] = 'otro@pfizer.com'
            
            # Act
            response = client.post(
                '/usuarios/api/auth/registro-proveedor',
                data=json.dumps(proveedor_data2),
                content_type='application/json'
            )
            
            # Assert
            assert response.status_code == 409
            response_data = json.loads(response.data.decode())
            assert 'error' in response_data
    
    # ==================== LOGIN ====================
    
    def test_login_exitoso(self, client, app_context):
        """Test login exitoso"""
        with app_context.app_context():
            # Arrange - Registrar un vendedor primero
            vendedor_data = {
                'nombre': 'María García',
                'email': 'maria@example.com',
                'identificacion': '1234567890',
                'telefono': '3001234567',
                'direccion': 'Calle 123 #45-67',
                'password': 'Password123'
            }
            
            client.post(
                '/usuarios/api/auth/registro-vendedor',
                data=json.dumps(vendedor_data),
                content_type='application/json'
            )
            
            # Act - Intentar login
            login_data = {
                'email': 'maria@example.com',
                'password': 'Password123'
            }
            
            response = client.post(
                '/usuarios/api/auth/login',
                data=json.dumps(login_data),
                content_type='application/json'
            )
            
            # Assert
            assert response.status_code == 200
            response_data = json.loads(response.data.decode())
            assert 'access_token' in response_data
            assert 'token_type' in response_data
            assert 'expires_in' in response_data
            assert 'user_info' in response_data
            assert response_data['token_type'] == 'Bearer'
            assert response_data['user_info']['email'] == 'maria@example.com'
            assert response_data['user_info']['tipo_usuario'] == 'VENDEDOR'
    
    def test_login_credenciales_invalidas(self, client, app_context):
        """Test login con credenciales inválidas"""
        with app_context.app_context():
            # Arrange - Registrar un vendedor
            vendedor_data = {
                'nombre': 'María García',
                'email': 'maria@example.com',
                'identificacion': '1234567890',
                'telefono': '3001234567',
                'direccion': 'Calle 123 #45-67',
                'password': 'Password123'
            }
            
            client.post(
                '/usuarios/api/auth/registro-vendedor',
                data=json.dumps(vendedor_data),
                content_type='application/json'
            )
            
            # Act - Intentar login con password incorrecta
            login_data = {
                'email': 'maria@example.com',
                'password': 'PasswordIncorrecto'
            }
            
            response = client.post(
                '/usuarios/api/auth/login',
                data=json.dumps(login_data),
                content_type='application/json'
            )
            
            # Assert
            assert response.status_code == 401
            response_data = json.loads(response.data.decode())
            assert 'error' in response_data
    
    def test_login_email_no_existe(self, client):
        """Test login con email no registrado"""
        # Arrange
        login_data = {
            'email': 'noexiste@example.com',
            'password': 'Password123'
        }
        
        # Act
        response = client.post(
            '/usuarios/api/auth/login',
            data=json.dumps(login_data),
            content_type='application/json'
        )
        
        # Assert
        assert response.status_code == 401
        response_data = json.loads(response.data.decode())
        assert 'error' in response_data
    
    def test_login_sin_email(self, client):
        """Test login sin email"""
        # Arrange
        login_data = {
            'password': 'Password123'
        }
        
        # Act
        response = client.post(
            '/usuarios/api/auth/login',
            data=json.dumps(login_data),
            content_type='application/json'
        )
        
        # Assert
        assert response.status_code == 400
        response_data = json.loads(response.data.decode())
        assert 'error' in response_data
    
    def test_login_sin_password(self, client):
        """Test login sin password"""
        # Arrange
        login_data = {
            'email': 'test@example.com'
        }
        
        # Act
        response = client.post(
            '/usuarios/api/auth/login',
            data=json.dumps(login_data),
            content_type='application/json'
        )
        
        # Assert
        assert response.status_code == 400
        response_data = json.loads(response.data.decode())
        assert 'error' in response_data
    
    def test_login_sin_json(self, client):
        """Test login sin JSON"""
        # Act
        response = client.post('/usuarios/api/auth/login')
        
        # Assert
        # Flask devuelve 500 cuando no hay Content-Type: application/json
        assert response.status_code in [400, 500]
        response_data = json.loads(response.data.decode())
        assert 'error' in response_data
    
    def test_login_diferentes_tipos_usuario(self, client, app_context):
        """Test login para diferentes tipos de usuario"""
        with app_context.app_context():
            # Arrange - Registrar vendedor
            vendedor_data = {
                'nombre': 'Vendedor Test',
                'email': 'vendedor@example.com',
                'identificacion': '1111111111',
                'telefono': '3001111111',
                'direccion': 'Calle 1',
                'password': 'Pass1234'
            }
            client.post('/usuarios/api/auth/registro-vendedor',
                       data=json.dumps(vendedor_data),
                       content_type='application/json')
            
            # Registrar cliente
            cliente_data = {
                'nombre': 'Cliente Test',
                'email': 'cliente@example.com',
                'identificacion': '2222222222',
                'telefono': '3002222222',
                'direccion': 'Calle 2',
                'password': 'Pass1234'
            }
            client.post('/usuarios/api/auth/registro-cliente',
                       data=json.dumps(cliente_data),
                       content_type='application/json')
            
            # Act & Assert - Login vendedor
            response_vendedor = client.post(
                '/usuarios/api/auth/login',
                data=json.dumps({'email': 'vendedor@example.com', 'password': 'Pass1234'}),
                content_type='application/json'
            )
            assert response_vendedor.status_code == 200
            data_vendedor = json.loads(response_vendedor.data.decode())
            assert data_vendedor['user_info']['tipo_usuario'] == 'VENDEDOR'
            
            # Act & Assert - Login cliente
            response_cliente = client.post(
                '/usuarios/api/auth/login',
                data=json.dumps({'email': 'cliente@example.com', 'password': 'Pass1234'}),
                content_type='application/json'
            )
            assert response_cliente.status_code == 200
            data_cliente = json.loads(response_cliente.data.decode())
            assert data_cliente['user_info']['tipo_usuario'] == 'CLIENTE'

