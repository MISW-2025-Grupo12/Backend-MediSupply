"""
Tests para el comando RegistrarVendedor
"""
import pytest
import uuid
from aplicacion.comandos.registrar_vendedor import RegistrarVendedor, RegistrarVendedorHandler
from aplicacion.dto import VendedorDTO
from dominio.excepciones import (
    EmailYaRegistradoError,
    IdentificacionYaRegistradaError,
    NombreInvalidoError,
    EmailInvalidoError,
    TelefonoInvalidoError,
    IdentificacionInvalidaError,
    PasswordInvalidaError
)
from infraestructura.repositorios import RepositorioUsuario
from infraestructura.modelos import UsuarioModel, VendedorModel
from config.db import db


class TestComandoRegistrarVendedor:
    """Tests para el comando de registro de vendedor con autenticación"""
    
    @pytest.fixture(autouse=True)
    def setup(self, app_context):
        """Setup para cada test"""
        with app_context.app_context():
            # Limpiar tablas antes de cada test
            UsuarioModel.query.delete()
            VendedorModel.query.delete()
            db.session.commit()
    
    def test_registrar_vendedor_exitoso(self, app_context):
        """Test registrar vendedor exitoso"""
        with app_context.app_context():
            # Arrange
            comando = RegistrarVendedor(
                nombre="María García",
                email="maria@example.com",
                identificacion="1234567890",
                telefono="3001234567",
                direccion="Calle 123 #45-67",
                password="Password123"
            )
            
            handler = RegistrarVendedorHandler()
            
            # Act
            vendedor_dto = handler.handle(comando)
            
            # Assert
            assert vendedor_dto is not None
            assert isinstance(vendedor_dto, VendedorDTO)
            assert vendedor_dto.nombre == comando.nombre
            assert vendedor_dto.email == comando.email
            assert vendedor_dto.identificacion == comando.identificacion
            assert vendedor_dto.telefono == comando.telefono
            assert vendedor_dto.direccion == comando.direccion
            
            # Verificar que se creó el usuario
            repositorio_usuario = RepositorioUsuario()
            usuario = repositorio_usuario.obtener_por_email(comando.email)
            assert usuario is not None
            assert usuario.tipo_usuario == "VENDEDOR"
            assert usuario.verificar_password(comando.password)
    
    def test_registrar_vendedor_email_duplicado(self, app_context):
        """Test registrar vendedor con email duplicado"""
        with app_context.app_context():
            # Arrange - Crear primer vendedor
            comando1 = RegistrarVendedor(
                nombre="María García",
                email="maria@example.com",
                identificacion="1234567890",
                telefono="3001234567",
                direccion="Calle 123 #45-67",
                password="Password123"
            )
            
            handler = RegistrarVendedorHandler()
            handler.handle(comando1)
            
            # Intentar registrar segundo vendedor con mismo email
            comando2 = RegistrarVendedor(
                nombre="Juan Pérez",
                email="maria@example.com",  # Email duplicado
                identificacion="0987654321",
                telefono="3009876543",
                direccion="Calle 456 #78-90",
                password="Password456"
            )
            
            # Act & Assert
            with pytest.raises(EmailYaRegistradoError):
                handler.handle(comando2)
    
    def test_registrar_vendedor_identificacion_duplicada(self, app_context):
        """Test registrar vendedor con identificación duplicada"""
        with app_context.app_context():
            # Arrange - Crear primer vendedor
            comando1 = RegistrarVendedor(
                nombre="María García",
                email="maria@example.com",
                identificacion="1234567890",
                telefono="3001234567",
                direccion="Calle 123 #45-67",
                password="Password123"
            )
            
            handler = RegistrarVendedorHandler()
            handler.handle(comando1)
            
            # Intentar registrar segundo vendedor con misma identificación
            comando2 = RegistrarVendedor(
                nombre="Juan Pérez",
                email="juan@example.com",
                identificacion="1234567890",  # Identificación duplicada
                telefono="3009876543",
                direccion="Calle 456 #78-90",
                password="Password456"
            )
            
            # Act & Assert
            with pytest.raises(IdentificacionYaRegistradaError):
                handler.handle(comando2)
    
    def test_registrar_vendedor_nombre_vacio(self, app_context):
        """Test registrar vendedor con nombre vacío"""
        with app_context.app_context():
            # Arrange
            comando = RegistrarVendedor(
                nombre="",  # Nombre vacío
                email="test@example.com",
                identificacion="1234567890",
                telefono="3001234567",
                direccion="Calle 123 #45-67",
                password="Password123"
            )
            
            handler = RegistrarVendedorHandler()
            
            # Act & Assert
            with pytest.raises(NombreInvalidoError):
                handler.handle(comando)
    
    def test_registrar_vendedor_email_invalido(self, app_context):
        """Test registrar vendedor con email inválido"""
        with app_context.app_context():
            # Arrange
            comando = RegistrarVendedor(
                nombre="María García",
                email="email_invalido",  # Email sin formato válido
                identificacion="1234567890",
                telefono="3001234567",
                direccion="Calle 123 #45-67",
                password="Password123"
            )
            
            handler = RegistrarVendedorHandler()
            
            # Act & Assert
            with pytest.raises(EmailInvalidoError):
                handler.handle(comando)
    
    def test_registrar_vendedor_telefono_no_numerico(self, app_context):
        """Test registrar vendedor con teléfono no numérico"""
        with app_context.app_context():
            # Arrange
            comando = RegistrarVendedor(
                nombre="María García",
                email="maria@example.com",
                identificacion="1234567890",
                telefono="300-ABC-DEFG",  # Teléfono con caracteres no numéricos
                direccion="Calle 123 #45-67",
                password="Password123"
            )
            
            handler = RegistrarVendedorHandler()
            
            # Act & Assert
            with pytest.raises(TelefonoInvalidoError):
                handler.handle(comando)
    
    def test_registrar_vendedor_identificacion_no_numerica(self, app_context):
        """Test registrar vendedor con identificación no numérica"""
        with app_context.app_context():
            # Arrange
            comando = RegistrarVendedor(
                nombre="María García",
                email="maria@example.com",
                identificacion="ABC1234567",  # Identificación con letras
                telefono="3001234567",
                direccion="Calle 123 #45-67",
                password="Password123"
            )
            
            handler = RegistrarVendedorHandler()
            
            # Act & Assert
            with pytest.raises(IdentificacionInvalidaError):
                handler.handle(comando)
    
    def test_registrar_vendedor_password_corta(self, app_context):
        """Test registrar vendedor con password muy corta"""
        with app_context.app_context():
            # Arrange
            comando = RegistrarVendedor(
                nombre="María García",
                email="maria@example.com",
                identificacion="1234567890",
                telefono="3001234567",
                direccion="Calle 123 #45-67",
                password="Pass12"  # Menos de 8 caracteres
            )
            
            handler = RegistrarVendedorHandler()
            
            # Act & Assert
            with pytest.raises(PasswordInvalidaError):
                handler.handle(comando)
    
    def test_registrar_vendedor_password_larga(self, app_context):
        """Test registrar vendedor con password muy larga"""
        with app_context.app_context():
            # Arrange
            comando = RegistrarVendedor(
                nombre="María García",
                email="maria@example.com",
                identificacion="1234567890",
                telefono="3001234567",
                direccion="Calle 123 #45-67",
                password="P" * 51  # Más de 50 caracteres
            )
            
            handler = RegistrarVendedorHandler()
            
            # Act & Assert
            with pytest.raises(PasswordInvalidaError):
                handler.handle(comando)
    
    def test_registrar_vendedor_crea_entidad_y_usuario(self, app_context):
        """Test que registrar vendedor crea tanto la entidad como el usuario"""
        with app_context.app_context():
            # Arrange
            comando = RegistrarVendedor(
                nombre="María García",
                email="maria@example.com",
                identificacion="1234567890",
                telefono="3001234567",
                direccion="Calle 123 #45-67",
                password="Password123"
            )
            
            handler = RegistrarVendedorHandler()
            
            # Act
            vendedor_dto = handler.handle(comando)
            
            # Assert - Verificar que existe el vendedor
            from infraestructura.repositorios import RepositorioVendedorSQLite
            repo_vendedor = RepositorioVendedorSQLite()
            vendedor = repo_vendedor.obtener_por_id(str(vendedor_dto.id))
            assert vendedor is not None
            
            # Assert - Verificar que existe el usuario
            repositorio_usuario = RepositorioUsuario()
            usuario = repositorio_usuario.obtener_por_email(comando.email)
            assert usuario is not None
            assert usuario.entidad_id == str(vendedor_dto.id)
            assert usuario.tipo_usuario == "VENDEDOR"
    
    def test_registrar_vendedor_no_almacena_password_plano(self, app_context):
        """Test que el password no se almacena en texto plano"""
        with app_context.app_context():
            # Arrange
            password = "Password123"
            comando = RegistrarVendedor(
                nombre="María García",
                email="maria@example.com",
                identificacion="1234567890",
                telefono="3001234567",
                direccion="Calle 123 #45-67",
                password=password
            )
            
            handler = RegistrarVendedorHandler()
            
            # Act
            handler.handle(comando)
            
            # Assert
            repositorio_usuario = RepositorioUsuario()
            usuario = repositorio_usuario.obtener_por_email(comando.email)
            assert usuario.password_hash != password
            assert len(usuario.password_hash) > 50  # Hash bcrypt es largo
            assert usuario.verificar_password(password)  # Pero se puede verificar

