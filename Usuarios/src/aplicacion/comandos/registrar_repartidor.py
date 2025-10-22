"""
Comando para registrar un repartidor con autenticación
"""
from dataclasses import dataclass
from seedwork.aplicacion.comandos import Comando, ejecutar_comando
import uuid
import logging
from aplicacion.dto import RepartidorDTO
from dominio.entidades import Repartidor
from dominio.objetos_valor import Nombre, Email, Telefono, Identificacion, Password
from dominio.excepciones import (
    EmailYaRegistradoError,
    IdentificacionYaRegistradaError
)
from infraestructura.repositorios import RepositorioRepartidorSQLite, RepositorioUsuario
from infraestructura.modelos import TipoUsuario

logger = logging.getLogger(__name__)


@dataclass
class RegistrarRepartidor(Comando):
    """Comando para registrar un repartidor con autenticación"""
    nombre: str
    email: str
    identificacion: str
    telefono: str
    password: str


class RegistrarRepartidorHandler:
    """Handler para el comando RegistrarRepartidor"""
    
    def __init__(self, repositorio_repartidor=None, repositorio_usuario=None):
        self.repositorio_repartidor = repositorio_repartidor or RepositorioRepartidorSQLite()
        self.repositorio_usuario = repositorio_usuario or RepositorioUsuario()
    
    def handle(self, comando: RegistrarRepartidor) -> RepartidorDTO:
        """
        Maneja el registro de un repartidor con autenticación
        
        Pasos:
        1. Verificar que email no esté registrado
        2. Verificar que identificacion no esté registrada
        3. Crear entidad Repartidor con validaciones de objetos de valor
        4. Guardar Repartidor en repositorio
        5. Crear Usuario vinculado al Repartidor con hash de password
        6. Guardar Usuario en repositorio
        7. Retornar RepartidorDTO (sin contraseña)
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
            password_vo = Password(comando.password)  # Valida longitud
            
            # 4. Crear entidad de dominio Repartidor
            repartidor = Repartidor(
                nombre=nombre_vo,
                email=email_vo,
                identificacion=identificacion_vo,
                telefono=telefono_vo
            )
            
            # Disparar evento de creación
            repartidor.disparar_evento_creacion()
            
            # 5. Crear DTO del repartidor
            repartidor_dto = RepartidorDTO(
                nombre=comando.nombre,
                email=comando.email,
                identificacion=comando.identificacion,
                telefono=comando.telefono
            )
            
            # 6. Guardar repartidor en base de datos
            repartidor_guardado = self.repositorio_repartidor.crear(repartidor_dto)
            
            # 7. Crear usuario con autenticación (hash de password)
            self.repositorio_usuario.crear(
                email=comando.email,
                password=comando.password,
                tipo_usuario=TipoUsuario.REPARTIDOR.value,
                entidad_id=str(repartidor_guardado.id),
                identificacion=comando.identificacion
            )
            
            logger.info(f"Repartidor registrado exitosamente: {repartidor_guardado.email}")
            
            return repartidor_guardado
            
        except (EmailYaRegistradoError, IdentificacionYaRegistradaError) as e:
            # Re-lanzar excepciones de dominio
            logger.warning(f"Error de validación en registro: {str(e)}")
            raise
            
        except Exception as e:
            logger.error(f"Error registrando repartidor: {e}")
            raise


@ejecutar_comando.register
def _(comando: RegistrarRepartidor):
    """Registra el handler para el comando RegistrarRepartidor"""
    handler = RegistrarRepartidorHandler()
    return handler.handle(comando)

