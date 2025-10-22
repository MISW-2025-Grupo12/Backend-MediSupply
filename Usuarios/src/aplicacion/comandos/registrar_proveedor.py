"""
Comando para registrar un proveedor con autenticación
"""
from dataclasses import dataclass
from seedwork.aplicacion.comandos import Comando, ejecutar_comando
import uuid
import logging
from aplicacion.dto import ProveedorDTO
from dominio.entidades import Proveedor
from dominio.objetos_valor import Nombre, Email, Direccion, Identificacion, Telefono, Password
from dominio.excepciones import (
    EmailYaRegistradoError,
    IdentificacionYaRegistradaError
)
from infraestructura.repositorios import RepositorioProveedorSQLite, RepositorioUsuario
from infraestructura.modelos import TipoUsuario

logger = logging.getLogger(__name__)


@dataclass
class RegistrarProveedor(Comando):
    """Comando para registrar un proveedor con autenticación"""
    nombre: str
    email: str
    identificacion: str
    telefono: str
    direccion: str
    password: str


class RegistrarProveedorHandler:
    """Handler para el comando RegistrarProveedor"""
    
    def __init__(self, repositorio_proveedor=None, repositorio_usuario=None):
        self.repositorio_proveedor = repositorio_proveedor or RepositorioProveedorSQLite()
        self.repositorio_usuario = repositorio_usuario or RepositorioUsuario()
    
    def handle(self, comando: RegistrarProveedor) -> ProveedorDTO:
        """
        Maneja el registro de un proveedor con autenticación
        
        Pasos:
        1. Verificar que email no esté registrado
        2. Verificar que identificacion no esté registrada
        3. Crear entidad Proveedor con validaciones de objetos de valor
        4. Guardar Proveedor en repositorio
        5. Crear Usuario vinculado al Proveedor con hash de password
        6. Guardar Usuario en repositorio
        7. Retornar ProveedorDTO (sin contraseña)
        """
        try:
            # 1. Verificar que el email no esté registrado
            if self.repositorio_usuario.existe_email(comando.email):
                raise EmailYaRegistradoError(comando.email)
            
            # 2. Verificar que la identificación no esté registrada
            if self.repositorio_usuario.existe_identificacion(comando.identificacion):
                raise IdentificacionYaRegistradaError(comando.identificacion)
            
            # 3. Crear objetos de valor (se validan automáticamente en __post_init__)
            nombre_vo = Nombre(comando.nombre)
            email_vo = Email(comando.email)
            identificacion_vo = Identificacion(comando.identificacion)
            telefono_vo = Telefono(comando.telefono)
            direccion_vo = Direccion(comando.direccion)
            password_vo = Password(comando.password)  # Valida longitud
            
            # 4. Crear entidad de dominio Proveedor
            proveedor = Proveedor(
                nombre=nombre_vo,
                email=email_vo,
                identificacion=identificacion_vo,
                telefono=telefono_vo,
                direccion=direccion_vo
            )
            
            # Disparar evento de creación
            proveedor.disparar_evento_creacion()
            
            # 5. Crear DTO del proveedor
            proveedor_dto = ProveedorDTO(
                nombre=comando.nombre,
                email=comando.email,
                identificacion=comando.identificacion,
                telefono=comando.telefono,
                direccion=comando.direccion
            )
            
            # 6. Guardar proveedor en base de datos
            proveedor_guardado = self.repositorio_proveedor.crear(proveedor_dto)
            
            # 7. Crear usuario con autenticación (hash de password)
            self.repositorio_usuario.crear(
                email=comando.email,
                password=comando.password,
                tipo_usuario=TipoUsuario.PROVEEDOR.value,
                identificacion=comando.identificacion,
                entidad_id=str(proveedor_guardado.id)
            )
            
            logger.info(f"Proveedor registrado exitosamente: {proveedor_guardado.email}")
            
            return proveedor_guardado
            
        except (EmailYaRegistradoError, IdentificacionYaRegistradaError) as e:
            # Re-lanzar excepciones de dominio
            logger.warning(f"Error de validación en registro: {str(e)}")
            raise
            
        except Exception as e:
            logger.error(f"Error registrando proveedor: {e}")
            raise


@ejecutar_comando.register
def _(comando: RegistrarProveedor):
    """Registra el handler para el comando RegistrarProveedor"""
    handler = RegistrarProveedorHandler()
    return handler.handle(comando)

