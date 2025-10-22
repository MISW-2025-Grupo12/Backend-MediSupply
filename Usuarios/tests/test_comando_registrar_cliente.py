"""
Tests para el comando RegistrarCliente
"""
import pytest
import uuid
from aplicacion.comandos.registrar_cliente import RegistrarCliente, RegistrarClienteHandler
from aplicacion.dto import ClienteDTO
from dominio.excepciones import (
    EmailYaRegistradoError,
    IdentificacionYaRegistradaError,
    NombreInvalidoError,
    EmailInvalidoError,
    PasswordInvalidaError
)
from infraestructura.repositorios import RepositorioUsuario
from infraestructura.modelos import UsuarioModel, ClienteModel
from config.db import db


class TestComandoRegistrarCliente:
    """Tests para el comando de registro de cliente con autenticación"""
    
    @pytest.fixture(autouse=True)
    def setup(self, app_context):
        """Setup para cada test"""
        with app_context.app_context():
            # Limpiar tablas antes de cada test
            UsuarioModel.query.delete()
            ClienteModel.query.delete()
            db.session.commit()
    
    def test_registrar_cliente_exitoso(self, app_context):
        """Test registrar cliente exitoso"""
        with app_context.app_context():
            # Arrange
            comando = RegistrarCliente(
                nombre="Hospital San Ignacio",
                email="contacto@sanignacio.com",
                identificacion="8601234567",
                telefono="3115566778",
                direccion="Cra 11 # 89 - 76",
                password="ClinicaPass456"
            )
            
            handler = RegistrarClienteHandler()
            
            # Act
            cliente_dto = handler.handle(comando)
            
            # Assert
            assert cliente_dto is not None
            assert isinstance(cliente_dto, ClienteDTO)
            assert cliente_dto.nombre == comando.nombre
            assert cliente_dto.email == comando.email
            assert cliente_dto.identificacion == comando.identificacion
            assert cliente_dto.telefono == comando.telefono
            assert cliente_dto.direccion == comando.direccion
            
            # Verificar que se creó el usuario
            repositorio_usuario = RepositorioUsuario()
            usuario = repositorio_usuario.obtener_por_email(comando.email)
            assert usuario is not None
            assert usuario.tipo_usuario == "CLIENTE"
            assert usuario.verificar_password(comando.password)
    
    def test_registrar_cliente_email_duplicado(self, app_context):
        """Test registrar cliente con email duplicado"""
        with app_context.app_context():
            # Arrange - Crear primer cliente
            comando1 = RegistrarCliente(
                nombre="Hospital San Ignacio",
                email="hospital@example.com",
                identificacion="8601234567",
                telefono="3115566778",
                direccion="Cra 11 # 89 - 76",
                password="ClinicaPass456"
            )
            
            handler = RegistrarClienteHandler()
            handler.handle(comando1)
            
            # Intentar registrar segundo cliente con mismo email
            comando2 = RegistrarCliente(
                nombre="Clínica del Country",
                email="hospital@example.com",  # Email duplicado
                identificacion="8609999999",
                telefono="3117778888",
                direccion="Calle 50 # 10 - 20",
                password="ClinicaPass789"
            )
            
            # Act & Assert
            with pytest.raises(EmailYaRegistradoError):
                handler.handle(comando2)
    
    def test_registrar_cliente_identificacion_duplicada(self, app_context):
        """Test registrar cliente con identificación duplicada"""
        with app_context.app_context():
            # Arrange - Crear primer cliente
            comando1 = RegistrarCliente(
                nombre="Hospital San Ignacio",
                email="hospital1@example.com",
                identificacion="8601234567",
                telefono="3115566778",
                direccion="Cra 11 # 89 - 76",
                password="ClinicaPass456"
            )
            
            handler = RegistrarClienteHandler()
            handler.handle(comando1)
            
            # Intentar registrar segundo cliente con misma identificación
            comando2 = RegistrarCliente(
                nombre="Clínica del Country",
                email="hospital2@example.com",
                identificacion="8601234567",  # Identificación duplicada
                telefono="3117778888",
                direccion="Calle 50 # 10 - 20",
                password="ClinicaPass789"
            )
            
            # Act & Assert
            with pytest.raises(IdentificacionYaRegistradaError):
                handler.handle(comando2)
    
    def test_registrar_cliente_crea_entidad_y_usuario(self, app_context):
        """Test que registrar cliente crea tanto la entidad como el usuario"""
        with app_context.app_context():
            # Arrange
            comando = RegistrarCliente(
                nombre="Hospital San Ignacio",
                email="contacto@sanignacio.com",
                identificacion="8601234567",
                telefono="3115566778",
                direccion="Cra 11 # 89 - 76",
                password="ClinicaPass456"
            )
            
            handler = RegistrarClienteHandler()
            
            # Act
            cliente_dto = handler.handle(comando)
            
            # Assert - Verificar que existe el cliente
            from infraestructura.repositorios import RepositorioClienteSQLite
            repo_cliente = RepositorioClienteSQLite()
            cliente = repo_cliente.obtener_por_id(str(cliente_dto.id))
            assert cliente is not None
            
            # Assert - Verificar que existe el usuario
            repositorio_usuario = RepositorioUsuario()
            usuario = repositorio_usuario.obtener_por_email(comando.email)
            assert usuario is not None
            assert usuario.entidad_id == str(cliente_dto.id)
            assert usuario.tipo_usuario == "CLIENTE"
    
    def test_registrar_cliente_no_almacena_password_plano(self, app_context):
        """Test que el password no se almacena en texto plano"""
        with app_context.app_context():
            # Arrange
            password = "ClinicaPass456"
            comando = RegistrarCliente(
                nombre="Hospital San Ignacio",
                email="contacto@sanignacio.com",
                identificacion="8601234567",
                telefono="3115566778",
                direccion="Cra 11 # 89 - 76",
                password=password
            )
            
            handler = RegistrarClienteHandler()
            
            # Act
            handler.handle(comando)
            
            # Assert
            repositorio_usuario = RepositorioUsuario()
            usuario = repositorio_usuario.obtener_por_email(comando.email)
            assert usuario.password_hash != password
            assert len(usuario.password_hash) > 50
            assert usuario.verificar_password(password)
    
    def test_registrar_cliente_password_corta(self, app_context):
        """Test registrar cliente con password muy corta"""
        with app_context.app_context():
            # Arrange
            comando = RegistrarCliente(
                nombre="Hospital San Ignacio",
                email="contacto@sanignacio.com",
                identificacion="8601234567",
                telefono="3115566778",
                direccion="Cra 11 # 89 - 76",
                password="Pass12"  # Menos de 8 caracteres
            )
            
            handler = RegistrarClienteHandler()
            
            # Act & Assert
            with pytest.raises(PasswordInvalidaError):
                handler.handle(comando)
    
    def test_registrar_cliente_nombre_vacio(self, app_context):
        """Test registrar cliente con nombre vacío"""
        with app_context.app_context():
            # Arrange
            comando = RegistrarCliente(
                nombre="",  # Nombre vacío
                email="contacto@sanignacio.com",
                identificacion="8601234567",
                telefono="3115566778",
                direccion="Cra 11 # 89 - 76",
                password="ClinicaPass456"
            )
            
            handler = RegistrarClienteHandler()
            
            # Act & Assert
            with pytest.raises(NombreInvalidoError):
                handler.handle(comando)
    
    def test_registrar_cliente_email_invalido(self, app_context):
        """Test registrar cliente con email inválido"""
        with app_context.app_context():
            # Arrange
            comando = RegistrarCliente(
                nombre="Hospital San Ignacio",
                email="email_invalido",  # Email sin formato válido
                identificacion="8601234567",
                telefono="3115566778",
                direccion="Cra 11 # 89 - 76",
                password="ClinicaPass456"
            )
            
            handler = RegistrarClienteHandler()
            
            # Act & Assert
            with pytest.raises(EmailInvalidoError):
                handler.handle(comando)

