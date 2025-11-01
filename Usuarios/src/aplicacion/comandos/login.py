"""
Comando para autenticación de usuarios (login)
"""
from dataclasses import dataclass
from seedwork.aplicacion.comandos import Comando, ejecutar_comando
import logging
from aplicacion.dto import TokenDTO
from dominio.excepciones import CredencialesInvalidasError, UsuarioInactivoError
from infraestructura.repositorios import RepositorioUsuario
from infraestructura.modelos import ProveedorModel, VendedorModel, ClienteModel, AdministradorModel, RepartidorModel

logger = logging.getLogger(__name__)


@dataclass
class Login(Comando):
    """Comando para login de usuario"""
    email: str
    password: str


class LoginHandler:
    """Handler para el comando Login"""
    
    def __init__(self, repositorio_usuario=None):
        self.repositorio_usuario = repositorio_usuario or RepositorioUsuario()
    
    def _obtener_nombre_entidad(self, tipo_usuario: str, entidad_id: str) -> str:
        """Obtiene el nombre de la entidad según el tipo de usuario"""
        try:
            tipo_usuario_upper = tipo_usuario.upper()
            
            if tipo_usuario_upper == 'PROVEEDOR':
                entidad = ProveedorModel.query.get(entidad_id)
                return entidad.nombre if entidad else ''
            elif tipo_usuario_upper == 'VENDEDOR':
                entidad = VendedorModel.query.get(entidad_id)
                return entidad.nombre if entidad else ''
            elif tipo_usuario_upper == 'CLIENTE':
                entidad = ClienteModel.query.get(entidad_id)
                return entidad.nombre if entidad else ''
            elif tipo_usuario_upper == 'ADMINISTRADOR':
                entidad = AdministradorModel.query.get(entidad_id)
                return entidad.nombre if entidad else ''
            elif tipo_usuario_upper == 'REPARTIDOR':
                entidad = RepartidorModel.query.get(entidad_id)
                return entidad.nombre if entidad else ''
            else:
                logger.warning(f'Tipo de usuario desconocido: {tipo_usuario}')
                return ''
        except Exception as e:
            logger.error(f'Error obteniendo nombre de entidad: {e}')
            return ''
    
    def handle(self, comando: Login) -> TokenDTO:
        """
        Valida credenciales de un usuario
        """
        try:
            # 1. Buscar usuario por email
            usuario = self.repositorio_usuario.obtener_por_email(comando.email)
            
            # 2. Verificar que el usuario existe
            if not usuario:
                logger.warning(f"Intento de login con email no registrado: {comando.email}")
                raise CredencialesInvalidasError()
            
            # 3. Verificar que el usuario está activo
            if not usuario.is_active:
                logger.warning(f"Intento de login con usuario inactivo: {comando.email}")
                raise UsuarioInactivoError()
            
            # 4. Verificar la contraseña
            if not usuario.verificar_password(comando.password):
                logger.warning(f"Intento de login con contraseña incorrecta: {comando.email}")
                raise CredencialesInvalidasError()
            
            # 5. Obtener el nombre desde la entidad correspondiente
            nombre_usuario = self._obtener_nombre_entidad(usuario.tipo_usuario, usuario.entidad_id)
            
            # 6. Preparar información del usuario (sin datos sensibles)
            user_info = {
                'id': usuario.id,
                'nombre': nombre_usuario,
                'email': usuario.email,
                'tipo_usuario': usuario.tipo_usuario,
                'identificacion': usuario.identificacion,
                'entidad_id': usuario.entidad_id
            }
            
            # 7. Crear TokenDTO (sin token real - solo para compatibilidad)
            # El Auth-Service generará el token JWT real
            token_dto = TokenDTO(
                access_token='',  # Token vacío - será generado por Auth-Service
                token_type='Bearer',
                expires_in=0,  # Será definido por Auth-Service
                user_info=user_info
            )
            
            logger.info(f"Credenciales validadas para usuario: {usuario.email}")
            
            return token_dto
            
        except (CredencialesInvalidasError, UsuarioInactivoError) as e:
            # Re-lanzar excepciones de dominio
            raise
            
        except Exception as e:
            logger.error(f"Error en validación de credenciales: {e}")
            raise


@ejecutar_comando.register
def _(comando: Login):
    """Registra el handler para el comando Login"""
    handler = LoginHandler()
    return handler.handle(comando)

