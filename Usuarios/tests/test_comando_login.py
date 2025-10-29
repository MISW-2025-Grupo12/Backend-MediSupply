"""
Tests para el comando Login

NOTA: El comando Login ahora solo VALIDA credenciales.
NO genera tokens JWT - eso es responsabilidad del Auth-Service.
"""
import pytest
import uuid
from unittest.mock import Mock, patch
from aplicacion.comandos.login import Login, LoginHandler
from aplicacion.dto import TokenDTO
from dominio.excepciones import CredencialesInvalidasError, UsuarioInactivoError
from infraestructura.repositorios import RepositorioUsuario
from infraestructura.modelos import UsuarioModel
from config.db import db


class TestComandoLogin:
    """Tests para el comando de login"""
    
    @pytest.fixture(autouse=True)
    def setup(self, app_context):
        """Setup para cada test"""
        with app_context.app_context():
            # Limpiar tabla de usuarios antes de cada test
            UsuarioModel.query.delete()
            db.session.commit()
    
    def test_login_exitoso(self, app_context):
        """Test validación de credenciales exitosa"""
        with app_context.app_context():
            # Arrange
            repositorio = RepositorioUsuario()
            email = "test@example.com"
            password = "password123"
            
            # Crear usuario
            usuario = repositorio.crear(
                email=email,
                password=password,
                tipo_usuario="vendedor",
                identificacion="1234567890",
                entidad_id=str(uuid.uuid4())
            )
            
            comando = Login(email=email, password=password)
            handler = LoginHandler(repositorio)
            
            # Act
            token_dto = handler.handle(comando)
            
            # Assert - Verifica que las credenciales fueron validadas
            assert token_dto is not None
            assert isinstance(token_dto, TokenDTO)
            # El token está vacío - será generado por Auth-Service
            assert token_dto.access_token == ''
            assert token_dto.token_type == 'Bearer'
            assert token_dto.expires_in == 0
            # Verifica que la información del usuario está presente
            assert token_dto.user_info is not None
            assert token_dto.user_info['id'] == usuario.id
            assert token_dto.user_info['email'] == email
            assert token_dto.user_info['tipo_usuario'] == "vendedor"
            assert token_dto.user_info['identificacion'] == "1234567890"
    
    def test_login_email_no_existe(self, app_context):
        """Test login con email no registrado"""
        with app_context.app_context():
            # Arrange
            repositorio = RepositorioUsuario()
            comando = Login(email="noexiste@example.com", password="password123")
            handler = LoginHandler(repositorio)
            
            # Act & Assert
            with pytest.raises(CredencialesInvalidasError):
                handler.handle(comando)
    
    def test_login_password_incorrecta(self, app_context):
        """Test login con password incorrecta"""
        with app_context.app_context():
            # Arrange
            repositorio = RepositorioUsuario()
            email = "test@example.com"
            
            # Crear usuario
            repositorio.crear(
                email=email,
                password="passwordCorrecto",
                tipo_usuario="vendedor",
                identificacion="1234567890",
                entidad_id=str(uuid.uuid4())
            )
            
            comando = Login(email=email, password="passwordIncorrecto")
            handler = LoginHandler(repositorio)
            
            # Act & Assert
            with pytest.raises(CredencialesInvalidasError):
                handler.handle(comando)
    
    def test_login_usuario_inactivo(self, app_context):
        """Test login con usuario inactivo"""
        with app_context.app_context():
            # Arrange
            repositorio = RepositorioUsuario()
            email = "test@example.com"
            password = "password123"
            
            # Crear usuario y desactivarlo
            usuario = repositorio.crear(
                email=email,
                password=password,
                tipo_usuario="vendedor",
                identificacion="1234567890",
                entidad_id=str(uuid.uuid4())
            )
            repositorio.desactivar(usuario.id)
            
            comando = Login(email=email, password=password)
            handler = LoginHandler(repositorio)
            
            # Act & Assert
            with pytest.raises(UsuarioInactivoError):
                handler.handle(comando)
    
    
    def test_login_diferentes_tipos_usuario(self, app_context):
        """Test login para diferentes tipos de usuario"""
        with app_context.app_context():
            # Arrange
            repositorio = RepositorioUsuario()
            password = "password123"
            
            # Crear usuarios de diferentes tipos
            vendedor = repositorio.crear(
                email="vendedor@example.com",
                password=password,
                tipo_usuario="vendedor",
                identificacion="1111111111",
                entidad_id=str(uuid.uuid4())
            )
            
            cliente = repositorio.crear(
                email="cliente@example.com",
                password=password,
                tipo_usuario="cliente",
                identificacion="2222222222",
                entidad_id=str(uuid.uuid4())
            )
            
            proveedor = repositorio.crear(
                email="proveedor@example.com",
                password=password,
                tipo_usuario="proveedor",
                identificacion="3333333333",
                entidad_id=str(uuid.uuid4())
            )
            
            handler = LoginHandler(repositorio)
            
            # Act & Assert - Vendedor
            token_vendedor = handler.handle(Login(email="vendedor@example.com", password=password))
            assert token_vendedor.user_info['tipo_usuario'] == "vendedor"
            
            # Act & Assert - Cliente
            token_cliente = handler.handle(Login(email="cliente@example.com", password=password))
            assert token_cliente.user_info['tipo_usuario'] == "cliente"
            
            # Act & Assert - Proveedor
            token_proveedor = handler.handle(Login(email="proveedor@example.com", password=password))
            assert token_proveedor.user_info['tipo_usuario'] == "proveedor"
    
    def test_login_user_info_completo(self, app_context):
        """Test que user_info contiene todos los campos necesarios"""
        with app_context.app_context():
            # Arrange
            from infraestructura.modelos import VendedorModel
            from config.db import db
            
            repositorio = RepositorioUsuario()
            email = "test@example.com"
            password = "password123"
            identificacion = "9876543210"
            entidad_id = str(uuid.uuid4())
            
            # Crear la entidad Vendedor primero
            vendedor_model = VendedorModel(
                id=entidad_id,
                nombre="Test Vendedor",
                email=email,
                identificacion=identificacion,
                telefono="3001234567",
                direccion="Test Dirección"
            )
            db.session.add(vendedor_model)
            db.session.commit()
            
            # Crear usuario
            usuario = repositorio.crear(
                email=email,
                password=password,
                tipo_usuario="vendedor",
                identificacion=identificacion,
                entidad_id=entidad_id
            )
            
            comando = Login(email=email, password=password)
            handler = LoginHandler(repositorio)
            
            # Act
            token_dto = handler.handle(comando)
            
            # Assert
            user_info = token_dto.user_info
            assert 'id' in user_info
            assert 'nombre' in user_info  # Verificar que el nombre está presente
            assert 'email' in user_info
            assert 'tipo_usuario' in user_info
            assert 'identificacion' in user_info
            assert 'entidad_id' in user_info
            assert user_info['id'] == usuario.id
            assert user_info['nombre'] == "Test Vendedor"  # Verificar que el nombre es correcto
            assert user_info['email'] == email
            assert user_info['tipo_usuario'] == "vendedor"
            assert user_info['identificacion'] == identificacion
            assert user_info['entidad_id'] == entidad_id
    
    def test_login_no_incluye_password_en_respuesta(self, app_context):
        """Test que el login no incluye el password en la respuesta"""
        with app_context.app_context():
            # Arrange
            repositorio = RepositorioUsuario()
            email = "test@example.com"
            password = "password123"
            
            # Crear usuario
            repositorio.crear(
                email=email,
                password=password,
                tipo_usuario="vendedor",
                identificacion="1234567890",
                entidad_id=str(uuid.uuid4())
            )
            
            comando = Login(email=email, password=password)
            handler = LoginHandler(repositorio)
            
            # Act
            token_dto = handler.handle(comando)
            
            # Assert
            user_info = token_dto.user_info
            assert 'password' not in user_info
            assert 'password_hash' not in user_info

