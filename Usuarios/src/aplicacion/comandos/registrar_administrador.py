"""
Comando para registrar un administrador con autenticación
"""
from dataclasses import dataclass
from seedwork.aplicacion.comandos import Comando, ejecutar_comando
import uuid
import logging
from aplicacion.dto import AdministradorDTO
from dominio.entidades import Administrador
from dominio.objetos_valor import Nombre, Email, Password
from dominio.excepciones import EmailYaRegistradoError
from infraestructura.repositorios import RepositorioAdministradorSQLite, RepositorioUsuario
from infraestructura.modelos import TipoUsuario

logger = logging.getLogger(__name__)


@dataclass
class RegistrarAdministrador(Comando):
    """Comando para registrar un administrador con autenticación"""
    nombre: str
    email: str
    password: str


class RegistrarAdministradorHandler:
    """Handler para el comando RegistrarAdministrador"""
    
    def __init__(self, repositorio_administrador=None, repositorio_usuario=None):
        self.repositorio_administrador = repositorio_administrador or RepositorioAdministradorSQLite()
        self.repositorio_usuario = repositorio_usuario or RepositorioUsuario()
    
    def handle(self, comando: RegistrarAdministrador) -> AdministradorDTO:
        """
        Maneja el registro de un administrador con autenticación
        
        Pasos:
        1. Verificar que email no esté registrado
        2. Crear entidad Administrador con validaciones de objetos de valor
        3. Guardar Administrador en repositorio
        4. Crear Usuario vinculado al Administrador con hash de password
        5. Guardar Usuario en repositorio
        6. Retornar AdministradorDTO (sin contraseña)
        """
        try:
            # 1. Verificar que el email no esté registrado
            if self.repositorio_usuario.existe_email(comando.email):
                raise EmailYaRegistradoError(comando.email)
            
            # 2. Crear objetos de valor (se validan automáticamente en __post_init__)
            nombre_vo = Nombre(comando.nombre)
            email_vo = Email(comando.email)
            password_vo = Password(comando.password)  # Valida longitud
            
            # 3. Crear entidad de dominio Administrador
            administrador = Administrador(
                nombre=nombre_vo,
                email=email_vo
            )
            
            # Disparar evento de creación
            administrador.disparar_evento_creacion()
            
            # 4. Crear DTO del administrador
            administrador_dto = AdministradorDTO(
                nombre=comando.nombre,
                email=comando.email
            )
            
            # 5. Guardar administrador en base de datos
            administrador_guardado = self.repositorio_administrador.crear(administrador_dto)
            
            # 6. Crear usuario con autenticación (hash de password)
            # Los administradores no tienen identificacion
            self.repositorio_usuario.crear(
                email=comando.email,
                password=comando.password,
                tipo_usuario=TipoUsuario.ADMINISTRADOR.value,
                entidad_id=str(administrador_guardado.id),
                identificacion=None  # Administradores no tienen identificación
            )
            
            logger.info(f"Administrador registrado exitosamente: {administrador_guardado.email}")
            
            return administrador_guardado
            
        except EmailYaRegistradoError as e:
            # Re-lanzar excepciones de dominio
            logger.warning(f"Error de validación en registro: {str(e)}")
            raise
            
        except Exception as e:
            logger.error(f"Error registrando administrador: {e}")
            raise


@ejecutar_comando.register
def _(comando: RegistrarAdministrador):
    """Registra el handler para el comando RegistrarAdministrador"""
    handler = RegistrarAdministradorHandler()
    return handler.handle(comando)

