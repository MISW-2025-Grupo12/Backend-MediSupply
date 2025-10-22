"""
Comando para registrar un vendedor con autenticación
"""
from dataclasses import dataclass
from seedwork.aplicacion.comandos import Comando, ejecutar_comando
import uuid
import logging
from aplicacion.dto import VendedorDTO
from dominio.entidades import Vendedor
from dominio.objetos_valor import Nombre, Email, Telefono, Direccion, Identificacion, Password
from dominio.excepciones import (
    EmailYaRegistradoError,
    IdentificacionYaRegistradaError
)
from infraestructura.repositorios import RepositorioVendedorSQLite, RepositorioUsuario
from infraestructura.modelos import TipoUsuario

logger = logging.getLogger(__name__)


@dataclass
class RegistrarVendedor(Comando):
    """Comando para registrar un vendedor con autenticación"""
    nombre: str
    email: str
    identificacion: str
    telefono: str
    direccion: str
    password: str


class RegistrarVendedorHandler:
    """Handler para el comando RegistrarVendedor"""
    
    def __init__(self, repositorio_vendedor=None, repositorio_usuario=None):
        self.repositorio_vendedor = repositorio_vendedor or RepositorioVendedorSQLite()
        self.repositorio_usuario = repositorio_usuario or RepositorioUsuario()
    
    def handle(self, comando: RegistrarVendedor) -> VendedorDTO:
        """
        Maneja el registro de un vendedor con autenticación
        
        Pasos:
        1. Verificar que email no esté registrado
        2. Verificar que identificacion no esté registrada
        3. Crear entidad Vendedor con validaciones de objetos de valor
        4. Guardar Vendedor en repositorio
        5. Crear Usuario vinculado al Vendedor con hash de password
        6. Guardar Usuario en repositorio
        7. Retornar VendedorDTO (sin contraseña)
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
            
            # 4. Crear entidad de dominio Vendedor
            vendedor = Vendedor(
                nombre=nombre_vo,
                email=email_vo,
                identificacion=identificacion_vo,
                telefono=telefono_vo,
                direccion=direccion_vo
            )
            
            # Disparar evento de creación
            vendedor.disparar_evento_creacion()
            
            # 5. Crear DTO del vendedor
            vendedor_dto = VendedorDTO(
                nombre=comando.nombre,
                email=comando.email,
                identificacion=comando.identificacion,
                telefono=comando.telefono,
                direccion=comando.direccion
            )
            
            # 6. Guardar vendedor en base de datos
            vendedor_guardado = self.repositorio_vendedor.crear(vendedor_dto)
            
            # 7. Crear usuario con autenticación (hash de password)
            self.repositorio_usuario.crear(
                email=comando.email,
                password=comando.password,
                tipo_usuario=TipoUsuario.VENDEDOR.value,
                identificacion=comando.identificacion,
                entidad_id=str(vendedor_guardado.id)
            )
            
            logger.info(f"Vendedor registrado exitosamente: {vendedor_guardado.email}")
            
            return vendedor_guardado
            
        except (EmailYaRegistradoError, IdentificacionYaRegistradaError) as e:
            # Re-lanzar excepciones de dominio
            logger.warning(f"Error de validación en registro: {str(e)}")
            raise
            
        except Exception as e:
            logger.error(f"Error registrando vendedor: {e}")
            raise


@ejecutar_comando.register
def _(comando: RegistrarVendedor):
    """Registra el handler para el comando RegistrarVendedor"""
    handler = RegistrarVendedorHandler()
    return handler.handle(comando)

