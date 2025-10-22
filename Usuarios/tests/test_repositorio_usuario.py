"""
Tests para el RepositorioUsuario
"""
import pytest
import uuid
from infraestructura.repositorios import RepositorioUsuario
from infraestructura.modelos import UsuarioModel
from config.db import db


class TestRepositorioUsuario:
    """Tests para el repositorio de usuarios (autenticación)"""
    
    @pytest.fixture(autouse=True)
    def setup(self, app_context):
        """Setup para cada test"""
        with app_context.app_context():
            # Limpiar tabla de usuarios antes de cada test
            UsuarioModel.query.delete()
            db.session.commit()
    
    def test_crear_usuario_exitoso(self, app_context):
        """Test crear usuario con autenticación"""
        with app_context.app_context():
            # Arrange
            repositorio = RepositorioUsuario()
            email = "test@example.com"
            password = "password123"
            tipo_usuario = "vendedor"
            identificacion = "1234567890"
            entidad_id = str(uuid.uuid4())
            
            # Act
            usuario = repositorio.crear(
                email=email,
                password=password,
                tipo_usuario=tipo_usuario,
                identificacion=identificacion,
                entidad_id=entidad_id
            )
            
            # Assert
            assert usuario is not None
            assert usuario.email == email
            assert usuario.tipo_usuario == tipo_usuario
            assert usuario.identificacion == identificacion
            assert usuario.entidad_id == entidad_id
            assert usuario.is_active is True
            assert usuario.password_hash is not None
            assert usuario.password_hash != password  # No debe guardar el password en texto plano
            assert usuario.verificar_password(password) is True
    
    def test_obtener_por_email_existente(self, app_context):
        """Test obtener usuario por email existente"""
        with app_context.app_context():
            # Arrange
            repositorio = RepositorioUsuario()
            email = "test@example.com"
            usuario_creado = repositorio.crear(
                email=email,
                password="password123",
                tipo_usuario="vendedor",
                identificacion="1234567890",
                entidad_id=str(uuid.uuid4())
            )
            
            # Act
            usuario = repositorio.obtener_por_email(email)
            
            # Assert
            assert usuario is not None
            assert usuario.id == usuario_creado.id
            assert usuario.email == email
    
    def test_obtener_por_email_no_existente(self, app_context):
        """Test obtener usuario por email no existente"""
        with app_context.app_context():
            # Arrange
            repositorio = RepositorioUsuario()
            
            # Act
            usuario = repositorio.obtener_por_email("noexiste@example.com")
            
            # Assert
            assert usuario is None
    
    def test_obtener_por_identificacion_existente(self, app_context):
        """Test obtener usuario por identificación existente"""
        with app_context.app_context():
            # Arrange
            repositorio = RepositorioUsuario()
            identificacion = "9876543210"
            usuario_creado = repositorio.crear(
                email="test@example.com",
                password="password123",
                tipo_usuario="cliente",
                identificacion=identificacion,
                entidad_id=str(uuid.uuid4())
            )
            
            # Act
            usuario = repositorio.obtener_por_identificacion(identificacion)
            
            # Assert
            assert usuario is not None
            assert usuario.id == usuario_creado.id
            assert usuario.identificacion == identificacion
    
    def test_obtener_por_identificacion_no_existente(self, app_context):
        """Test obtener usuario por identificación no existente"""
        with app_context.app_context():
            # Arrange
            repositorio = RepositorioUsuario()
            
            # Act
            usuario = repositorio.obtener_por_identificacion("0000000000")
            
            # Assert
            assert usuario is None
    
    def test_existe_email_true(self, app_context):
        """Test verificar si existe email (true)"""
        with app_context.app_context():
            # Arrange
            repositorio = RepositorioUsuario()
            email = "existe@example.com"
            repositorio.crear(
                email=email,
                password="password123",
                tipo_usuario="vendedor",
                identificacion="1234567890",
                entidad_id=str(uuid.uuid4())
            )
            
            # Act
            existe = repositorio.existe_email(email)
            
            # Assert
            assert existe is True
    
    def test_existe_email_false(self, app_context):
        """Test verificar si existe email (false)"""
        with app_context.app_context():
            # Arrange
            repositorio = RepositorioUsuario()
            
            # Act
            existe = repositorio.existe_email("noexiste@example.com")
            
            # Assert
            assert existe is False
    
    def test_existe_identificacion_true(self, app_context):
        """Test verificar si existe identificación (true)"""
        with app_context.app_context():
            # Arrange
            repositorio = RepositorioUsuario()
            identificacion = "1234567890"
            repositorio.crear(
                email="test@example.com",
                password="password123",
                tipo_usuario="vendedor",
                identificacion=identificacion,
                entidad_id=str(uuid.uuid4())
            )
            
            # Act
            existe = repositorio.existe_identificacion(identificacion)
            
            # Assert
            assert existe is True
    
    def test_existe_identificacion_false(self, app_context):
        """Test verificar si existe identificación (false)"""
        with app_context.app_context():
            # Arrange
            repositorio = RepositorioUsuario()
            
            # Act
            existe = repositorio.existe_identificacion("0000000000")
            
            # Assert
            assert existe is False
    
    def test_verificar_password_correcto(self, app_context):
        """Test verificar password correcto"""
        with app_context.app_context():
            # Arrange
            repositorio = RepositorioUsuario()
            password = "miPassword123"
            usuario = repositorio.crear(
                email="test@example.com",
                password=password,
                tipo_usuario="vendedor",
                identificacion="1234567890",
                entidad_id=str(uuid.uuid4())
            )
            
            # Act
            resultado = usuario.verificar_password(password)
            
            # Assert
            assert resultado is True
    
    def test_verificar_password_incorrecto(self, app_context):
        """Test verificar password incorrecto"""
        with app_context.app_context():
            # Arrange
            repositorio = RepositorioUsuario()
            usuario = repositorio.crear(
                email="test@example.com",
                password="passwordCorrecto",
                tipo_usuario="vendedor",
                identificacion="1234567890",
                entidad_id=str(uuid.uuid4())
            )
            
            # Act
            resultado = usuario.verificar_password("passwordIncorrecto")
            
            # Assert
            assert resultado is False
    
    def test_obtener_por_id_existente(self, app_context):
        """Test obtener usuario por ID existente"""
        with app_context.app_context():
            # Arrange
            repositorio = RepositorioUsuario()
            usuario_creado = repositorio.crear(
                email="test@example.com",
                password="password123",
                tipo_usuario="vendedor",
                identificacion="1234567890",
                entidad_id=str(uuid.uuid4())
            )
            
            # Act
            usuario = repositorio.obtener_por_id(usuario_creado.id)
            
            # Assert
            assert usuario is not None
            assert usuario.id == usuario_creado.id
            assert usuario.email == usuario_creado.email
    
    def test_obtener_por_id_no_existente(self, app_context):
        """Test obtener usuario por ID no existente"""
        with app_context.app_context():
            # Arrange
            repositorio = RepositorioUsuario()
            
            # Act
            usuario = repositorio.obtener_por_id("id-no-existe-123")
            
            # Assert
            assert usuario is None
    
    def test_desactivar_usuario(self, app_context):
        """Test desactivar usuario"""
        with app_context.app_context():
            # Arrange
            repositorio = RepositorioUsuario()
            usuario = repositorio.crear(
                email="test@example.com",
                password="password123",
                tipo_usuario="vendedor",
                identificacion="1234567890",
                entidad_id=str(uuid.uuid4())
            )
            assert usuario.is_active is True
            
            # Act
            repositorio.desactivar(usuario.id)
            
            # Assert
            usuario_actualizado = repositorio.obtener_por_id(usuario.id)
            assert usuario_actualizado.is_active is False
    
    def test_crear_usuarios_diferentes_tipos(self, app_context):
        """Test crear usuarios de diferentes tipos"""
        with app_context.app_context():
            # Arrange
            repositorio = RepositorioUsuario()
            
            # Act
            vendedor = repositorio.crear(
                email="vendedor@example.com",
                password="pass123",
                tipo_usuario="vendedor",
                identificacion="1111111111",
                entidad_id=str(uuid.uuid4())
            )
            
            cliente = repositorio.crear(
                email="cliente@example.com",
                password="pass123",
                tipo_usuario="cliente",
                identificacion="2222222222",
                entidad_id=str(uuid.uuid4())
            )
            
            proveedor = repositorio.crear(
                email="proveedor@example.com",
                password="pass123",
                tipo_usuario="proveedor",
                identificacion="3333333333",
                entidad_id=str(uuid.uuid4())
            )
            
            # Assert
            assert vendedor.tipo_usuario == "vendedor"
            assert cliente.tipo_usuario == "cliente"
            assert proveedor.tipo_usuario == "proveedor"

