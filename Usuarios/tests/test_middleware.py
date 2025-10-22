"""
Tests para el middleware de autenticación y autorización
"""
import pytest
import json
import uuid
from flask import Flask
from unittest.mock import patch, Mock
from api.middleware import require_auth, require_role, get_current_user
from config.jwt_config import generar_token
from infraestructura.repositorios import RepositorioUsuario
from infraestructura.modelos import UsuarioModel
from config.db import db


class TestMiddleware:
    """Tests para el middleware de autenticación"""
    
    @pytest.fixture(autouse=True)
    def setup(self, app_context):
        """Setup para cada test"""
        with app_context.app_context():
            # Limpiar tabla de usuarios antes de cada test
            UsuarioModel.query.delete()
            db.session.commit()
    
    @pytest.fixture
    def test_app(self, app):
        """Fixture con app de Flask para tests"""
        return app
    
    # ==================== @require_auth ====================
    
    def test_require_auth_con_token_valido(self, client, app_context):
        """Test require_auth con token válido"""
        with app_context.app_context():
            # Arrange - Crear usuario
            repositorio = RepositorioUsuario()
            usuario = repositorio.crear(
                email="test@example.com",
                password="password123",
                tipo_usuario="vendedor",
                identificacion="1234567890",
                entidad_id=str(uuid.uuid4())
            )
            
            # Generar token
            token = generar_token(usuario.id, usuario.tipo_usuario, usuario.email)
            
            # Crear endpoint protegido de prueba
            from api import create_app
            app = create_app()
            
            @app.route('/test-auth')
            @require_auth
            def test_endpoint():
                return json.dumps({'mensaje': 'Acceso permitido'}), 200
            
            test_client = app.test_client()
            
            # Act
            response = test_client.get(
                '/test-auth',
                headers={'Authorization': f'Bearer {token}'}
            )
            
            # Assert
            assert response.status_code == 200
            response_data = json.loads(response.data.decode())
            assert response_data['mensaje'] == 'Acceso permitido'
    
    def test_require_auth_sin_token(self, client, app_context):
        """Test require_auth sin token"""
        with app_context.app_context():
            # Crear endpoint protegido de prueba
            from api import create_app
            app = create_app()
            
            @app.route('/test-auth-sin-token')
            @require_auth
            def test_endpoint():
                return json.dumps({'mensaje': 'Acceso permitido'}), 200
            
            test_client = app.test_client()
            
            # Act
            response = test_client.get('/test-auth-sin-token')
            
            # Assert
            assert response.status_code == 401
            response_data = json.loads(response.data.decode())
            assert 'error' in response_data
    
    def test_require_auth_con_token_invalido(self, client, app_context):
        """Test require_auth con token inválido"""
        with app_context.app_context():
            # Crear endpoint protegido de prueba
            from api import create_app
            app = create_app()
            
            @app.route('/test-auth-invalido')
            @require_auth
            def test_endpoint():
                return json.dumps({'mensaje': 'Acceso permitido'}), 200
            
            test_client = app.test_client()
            
            # Act
            response = test_client.get(
                '/test-auth-invalido',
                headers={'Authorization': 'Bearer token_invalido_123'}
            )
            
            # Assert
            assert response.status_code == 401
            response_data = json.loads(response.data.decode())
            assert 'error' in response_data
    
    def test_require_auth_con_header_malformado(self, client, app_context):
        """Test require_auth con header Authorization malformado"""
        with app_context.app_context():
            # Crear endpoint protegido de prueba
            from api import create_app
            app = create_app()
            
            @app.route('/test-auth-malformado')
            @require_auth
            def test_endpoint():
                return json.dumps({'mensaje': 'Acceso permitido'}), 200
            
            test_client = app.test_client()
            
            # Act - Header sin "Bearer "
            response = test_client.get(
                '/test-auth-malformado',
                headers={'Authorization': 'token_sin_bearer'}
            )
            
            # Assert
            assert response.status_code == 401
            response_data = json.loads(response.data.decode())
            assert 'error' in response_data
    
    # ==================== @require_role ====================
    
    def test_require_role_con_rol_correcto(self, client, app_context):
        """Test require_role con rol correcto"""
        with app_context.app_context():
            # Arrange - Crear usuario vendedor
            repositorio = RepositorioUsuario()
            usuario = repositorio.crear(
                email="vendedor@example.com",
                password="password123",
                tipo_usuario="vendedor",
                identificacion="1234567890",
                entidad_id=str(uuid.uuid4())
            )
            
            # Generar token
            token = generar_token(usuario.id, "vendedor", usuario.email)
            
            # Crear endpoint protegido de prueba
            from api import create_app
            app = create_app()
            
            @app.route('/test-role-vendedor')
            @require_auth
            @require_role('vendedor')
            def test_endpoint():
                return json.dumps({'mensaje': 'Acceso permitido para vendedor'}), 200
            
            test_client = app.test_client()
            
            # Act
            response = test_client.get(
                '/test-role-vendedor',
                headers={'Authorization': f'Bearer {token}'}
            )
            
            # Assert
            assert response.status_code == 200
            response_data = json.loads(response.data.decode())
            assert response_data['mensaje'] == 'Acceso permitido para vendedor'
    
    def test_require_role_con_rol_incorrecto(self, client, app_context):
        """Test require_role con rol incorrecto"""
        with app_context.app_context():
            # Arrange - Crear usuario cliente
            repositorio = RepositorioUsuario()
            usuario = repositorio.crear(
                email="cliente@example.com",
                password="password123",
                tipo_usuario="cliente",
                identificacion="1234567890",
                entidad_id=str(uuid.uuid4())
            )
            
            # Generar token de cliente
            token = generar_token(usuario.id, "cliente", usuario.email)
            
            # Crear endpoint que requiere vendedor
            from api import create_app
            app = create_app()
            
            @app.route('/test-role-vendedor-solo')
            @require_auth
            @require_role('vendedor')
            def test_endpoint():
                return json.dumps({'mensaje': 'Acceso permitido'}), 200
            
            test_client = app.test_client()
            
            # Act
            response = test_client.get(
                '/test-role-vendedor-solo',
                headers={'Authorization': f'Bearer {token}'}
            )
            
            # Assert
            assert response.status_code == 403
            response_data = json.loads(response.data.decode())
            assert 'error' in response_data
    
    def test_require_role_multiples_roles(self, client, app_context):
        """Test require_role con múltiples roles permitidos"""
        with app_context.app_context():
            # Arrange - Crear usuario cliente
            repositorio = RepositorioUsuario()
            usuario = repositorio.crear(
                email="cliente@example.com",
                password="password123",
                tipo_usuario="cliente",
                identificacion="1234567890",
                entidad_id=str(uuid.uuid4())
            )
            
            # Generar token
            token = generar_token(usuario.id, "cliente", usuario.email)
            
            # Crear endpoint que acepta vendedor o cliente
            from api import create_app
            app = create_app()
            
            @app.route('/test-role-multiple')
            @require_auth
            @require_role('vendedor', 'cliente')
            def test_endpoint():
                return json.dumps({'mensaje': 'Acceso permitido'}), 200
            
            test_client = app.test_client()
            
            # Act
            response = test_client.get(
                '/test-role-multiple',
                headers={'Authorization': f'Bearer {token}'}
            )
            
            # Assert
            assert response.status_code == 200
            response_data = json.loads(response.data.decode())
            assert response_data['mensaje'] == 'Acceso permitido'
    
    def test_require_role_proveedor(self, client, app_context):
        """Test require_role específico para proveedor"""
        with app_context.app_context():
            # Arrange - Crear usuario proveedor
            repositorio = RepositorioUsuario()
            usuario = repositorio.crear(
                email="proveedor@example.com",
                password="password123",
                tipo_usuario="proveedor",
                identificacion="1234567890",
                entidad_id=str(uuid.uuid4())
            )
            
            # Generar token
            token = generar_token(usuario.id, "proveedor", usuario.email)
            
            # Crear endpoint que requiere proveedor
            from api import create_app
            app = create_app()
            
            @app.route('/test-role-proveedor')
            @require_auth
            @require_role('proveedor')
            def test_endpoint():
                return json.dumps({'mensaje': 'Acceso permitido para proveedor'}), 200
            
            test_client = app.test_client()
            
            # Act
            response = test_client.get(
                '/test-role-proveedor',
                headers={'Authorization': f'Bearer {token}'}
            )
            
            # Assert
            assert response.status_code == 200
    
    # ==================== get_current_user ====================
    
    def test_get_current_user_con_token_valido(self, client, app_context):
        """Test get_current_user con token válido"""
        with app_context.app_context():
            # Arrange - Crear usuario
            repositorio = RepositorioUsuario()
            usuario = repositorio.crear(
                email="test@example.com",
                password="password123",
                tipo_usuario="vendedor",
                identificacion="1234567890",
                entidad_id=str(uuid.uuid4())
            )
            
            # Generar token
            token = generar_token(usuario.id, usuario.tipo_usuario, usuario.email)
            
            # Crear endpoint que usa get_current_user
            from api import create_app
            from flask import request
            app = create_app()
            
            @app.route('/test-current-user')
            @require_auth
            def test_endpoint():
                user = get_current_user()
                return json.dumps({
                    'usuario_id': user['usuario_id'],
                    'email': user['email'],
                    'tipo_usuario': user['tipo_usuario']
                }), 200
            
            test_client = app.test_client()
            
            # Act
            response = test_client.get(
                '/test-current-user',
                headers={'Authorization': f'Bearer {token}'}
            )
            
            # Assert
            assert response.status_code == 200
            response_data = json.loads(response.data.decode())
            assert response_data['usuario_id'] == usuario.id
            assert response_data['email'] == usuario.email
            assert response_data['tipo_usuario'] == "vendedor"
    
    def test_get_current_user_sin_token(self, client, app_context):
        """Test get_current_user sin token"""
        with app_context.app_context():
            # Crear endpoint que usa get_current_user
            from api import create_app
            from flask import request
            app = create_app()
            
            @app.route('/test-current-user-sin-token')
            def test_endpoint():
                user = get_current_user()
                return json.dumps({'user': user}), 200
            
            test_client = app.test_client()
            
            # Act
            response = test_client.get('/test-current-user-sin-token')
            
            # Assert
            assert response.status_code == 200
            response_data = json.loads(response.data.decode())
            assert response_data['user'] is None

