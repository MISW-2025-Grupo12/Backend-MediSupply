"""
Tests para el comando RegistrarProveedor
"""
import pytest
import uuid
from aplicacion.comandos.registrar_proveedor import RegistrarProveedor, RegistrarProveedorHandler
from aplicacion.dto import ProveedorDTO
from dominio.excepciones import (
    EmailYaRegistradoError,
    IdentificacionYaRegistradaError,
    NombreInvalidoError,
    EmailInvalidoError,
    TelefonoInvalidoError,
    PasswordInvalidaError
)
from infraestructura.repositorios import RepositorioUsuario
from infraestructura.modelos import UsuarioModel, ProveedorModel
from config.db import db


class TestComandoRegistrarProveedor:
    """Tests para el comando de registro de proveedor con autenticación"""
    
    @pytest.fixture(autouse=True)
    def setup(self, app_context):
        """Setup para cada test"""
        with app_context.app_context():
            # Limpiar tablas antes de cada test
            UsuarioModel.query.delete()
            ProveedorModel.query.delete()
            db.session.commit()
    
    def test_registrar_proveedor_exitoso(self, app_context):
        """Test registrar proveedor exitoso"""
        with app_context.app_context():
            # Arrange
            comando = RegistrarProveedor(
                nombre="Pfizer Colombia",
                email="contacto@pfizer.com.co",
                identificacion="9005678901",
                telefono="6017654321",
                direccion="Carrera 9 #50-30, Bogotá",
                password="PfizerPass789"
            )
            
            handler = RegistrarProveedorHandler()
            
            # Act
            proveedor_dto = handler.handle(comando)
            
            # Assert
            assert proveedor_dto is not None
            assert isinstance(proveedor_dto, ProveedorDTO)
            assert proveedor_dto.nombre == comando.nombre
            assert proveedor_dto.email == comando.email
            assert proveedor_dto.identificacion == comando.identificacion
            assert proveedor_dto.telefono == comando.telefono
            assert proveedor_dto.direccion == comando.direccion
            
            # Verificar que se creó el usuario
            repositorio_usuario = RepositorioUsuario()
            usuario = repositorio_usuario.obtener_por_email(comando.email)
            assert usuario is not None
            assert usuario.tipo_usuario == "PROVEEDOR"
            assert usuario.verificar_password(comando.password)
    
    def test_registrar_proveedor_email_duplicado(self, app_context):
        """Test registrar proveedor con email duplicado"""
        with app_context.app_context():
            # Arrange - Crear primer proveedor
            comando1 = RegistrarProveedor(
                nombre="Pfizer Colombia",
                email="contacto@pfizer.com.co",
                identificacion="9005678901",
                telefono="6017654321",
                direccion="Carrera 9 #50-30, Bogotá",
                password="PfizerPass789"
            )
            
            handler = RegistrarProveedorHandler()
            handler.handle(comando1)
            
            # Intentar registrar segundo proveedor con mismo email
            comando2 = RegistrarProveedor(
                nombre="Bayer Colombia",
                email="contacto@pfizer.com.co",  # Email duplicado
                identificacion="9009999999",
                telefono="6019999999",
                direccion="Calle 100 #20-30, Bogotá",
                password="BayerPass123"
            )
            
            # Act & Assert
            with pytest.raises(EmailYaRegistradoError):
                handler.handle(comando2)
    
    def test_registrar_proveedor_identificacion_duplicada(self, app_context):
        """Test registrar proveedor con identificación duplicada"""
        with app_context.app_context():
            # Arrange - Crear primer proveedor
            comando1 = RegistrarProveedor(
                nombre="Pfizer Colombia",
                email="pfizer@example.com",
                identificacion="9005678901",
                telefono="6017654321",
                direccion="Carrera 9 #50-30, Bogotá",
                password="PfizerPass789"
            )
            
            handler = RegistrarProveedorHandler()
            handler.handle(comando1)
            
            # Intentar registrar segundo proveedor con misma identificación
            comando2 = RegistrarProveedor(
                nombre="Bayer Colombia",
                email="bayer@example.com",
                identificacion="9005678901",  # Identificación duplicada
                telefono="6019999999",
                direccion="Calle 100 #20-30, Bogotá",
                password="BayerPass123"
            )
            
            # Act & Assert
            with pytest.raises(IdentificacionYaRegistradaError):
                handler.handle(comando2)
    
    def test_registrar_proveedor_crea_entidad_y_usuario(self, app_context):
        """Test que registrar proveedor crea tanto la entidad como el usuario"""
        with app_context.app_context():
            # Arrange
            comando = RegistrarProveedor(
                nombre="Pfizer Colombia",
                email="contacto@pfizer.com.co",
                identificacion="9005678901",
                telefono="6017654321",
                direccion="Carrera 9 #50-30, Bogotá",
                password="PfizerPass789"
            )
            
            handler = RegistrarProveedorHandler()
            
            # Act
            proveedor_dto = handler.handle(comando)
            
            # Assert - Verificar que existe el proveedor
            from infraestructura.repositorios import RepositorioProveedorSQLite
            repo_proveedor = RepositorioProveedorSQLite()
            proveedor = repo_proveedor.obtener_por_id(str(proveedor_dto.id))
            assert proveedor is not None
            
            # Assert - Verificar que existe el usuario
            repositorio_usuario = RepositorioUsuario()
            usuario = repositorio_usuario.obtener_por_email(comando.email)
            assert usuario is not None
            assert usuario.entidad_id == str(proveedor_dto.id)
            assert usuario.tipo_usuario == "PROVEEDOR"
    
    def test_registrar_proveedor_no_almacena_password_plano(self, app_context):
        """Test que el password no se almacena en texto plano"""
        with app_context.app_context():
            # Arrange
            password = "PfizerPass789"
            comando = RegistrarProveedor(
                nombre="Pfizer Colombia",
                email="contacto@pfizer.com.co",
                identificacion="9005678901",
                telefono="6017654321",
                direccion="Carrera 9 #50-30, Bogotá",
                password=password
            )
            
            handler = RegistrarProveedorHandler()
            
            # Act
            handler.handle(comando)
            
            # Assert
            repositorio_usuario = RepositorioUsuario()
            usuario = repositorio_usuario.obtener_por_email(comando.email)
            assert usuario.password_hash != password
            assert len(usuario.password_hash) > 50
            assert usuario.verificar_password(password)
    
    def test_registrar_proveedor_password_corta(self, app_context):
        """Test registrar proveedor con password muy corta"""
        with app_context.app_context():
            # Arrange
            comando = RegistrarProveedor(
                nombre="Pfizer Colombia",
                email="contacto@pfizer.com.co",
                identificacion="9005678901",
                telefono="6017654321",
                direccion="Carrera 9 #50-30, Bogotá",
                password="Pass12"  # Menos de 8 caracteres
            )
            
            handler = RegistrarProveedorHandler()
            
            # Act & Assert
            with pytest.raises(PasswordInvalidaError):
                handler.handle(comando)
    
    def test_registrar_proveedor_nombre_vacio(self, app_context):
        """Test registrar proveedor con nombre vacío"""
        with app_context.app_context():
            # Arrange
            comando = RegistrarProveedor(
                nombre="",  # Nombre vacío
                email="contacto@pfizer.com.co",
                identificacion="9005678901",
                telefono="6017654321",
                direccion="Carrera 9 #50-30, Bogotá",
                password="PfizerPass789"
            )
            
            handler = RegistrarProveedorHandler()
            
            # Act & Assert
            with pytest.raises(NombreInvalidoError):
                handler.handle(comando)
    
    def test_registrar_proveedor_email_invalido(self, app_context):
        """Test registrar proveedor con email inválido"""
        with app_context.app_context():
            # Arrange
            comando = RegistrarProveedor(
                nombre="Pfizer Colombia",
                email="email_invalido",  # Email sin formato válido
                identificacion="9005678901",
                telefono="6017654321",
                direccion="Carrera 9 #50-30, Bogotá",
                password="PfizerPass789"
            )
            
            handler = RegistrarProveedorHandler()
            
            # Act & Assert
            with pytest.raises(EmailInvalidoError):
                handler.handle(comando)
    
    def test_registrar_proveedor_telefono_no_numerico(self, app_context):
        """Test registrar proveedor con teléfono no numérico"""
        with app_context.app_context():
            # Arrange
            comando = RegistrarProveedor(
                nombre="Pfizer Colombia",
                email="contacto@pfizer.com.co",
                identificacion="9005678901",
                telefono="601-ABCD-EFG",  # Teléfono con caracteres no numéricos
                direccion="Carrera 9 #50-30, Bogotá",
                password="PfizerPass789"
            )
            
            handler = RegistrarProveedorHandler()
            
            # Act & Assert
            with pytest.raises(TelefonoInvalidoError):
                handler.handle(comando)
    
    def test_registrar_proveedor_con_todos_los_campos(self, app_context):
        """Test registrar proveedor verificando que todos los campos se guardan correctamente"""
        with app_context.app_context():
            # Arrange
            comando = RegistrarProveedor(
                nombre="Pfizer Colombia",
                email="contacto@pfizer.com.co",
                identificacion="9005678901",
                telefono="6017654321",
                direccion="Carrera 9 #50-30, Bogotá",
                password="PfizerPass789"
            )
            
            handler = RegistrarProveedorHandler()
            
            # Act
            proveedor_dto = handler.handle(comando)
            
            # Assert - Verificar todos los campos del DTO
            assert proveedor_dto.nombre == "Pfizer Colombia"
            assert proveedor_dto.email == "contacto@pfizer.com.co"
            assert proveedor_dto.identificacion == "9005678901"
            assert proveedor_dto.telefono == "6017654321"
            assert proveedor_dto.direccion == "Carrera 9 #50-30, Bogotá"
            
            # Assert - Verificar que el proveedor tiene telefono en la BD
            from infraestructura.repositorios import RepositorioProveedorSQLite
            repo_proveedor = RepositorioProveedorSQLite()
            proveedor = repo_proveedor.obtener_por_id(str(proveedor_dto.id))
            assert proveedor.telefono == "6017654321"

