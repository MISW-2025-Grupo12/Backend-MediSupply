"""
Middleware de autenticación y autorización con JWT
"""
from functools import wraps
from flask import request, jsonify, g
from config.jwt_config import verificar_token, extraer_token_de_header
import logging

logger = logging.getLogger(__name__)


def require_auth(f):
    """
    Decorator para proteger endpoints que requieren autenticación
    
    Verifica que el request tenga un token JWT válido en el header Authorization.
    Si es válido, inyecta la información del usuario en g.usuario
    
    Uso:
        @bp.route('/protegido')
        @require_auth
        def endpoint_protegido():
            usuario_id = g.usuario['usuario_id']
            return {'mensaje': 'Acceso autorizado'}
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Extraer token del header
        auth_header = request.headers.get('Authorization')
        token = extraer_token_de_header(auth_header)
        
        if not token:
            logger.warning("Intento de acceso sin token")
            return jsonify({
                'error': 'Token de autenticación requerido',
                'mensaje': 'Debe incluir un token JWT válido en el header Authorization'
            }), 401
        
        # Verificar token
        payload = verificar_token(token)
        
        if not payload:
            logger.warning("Intento de acceso con token inválido")
            return jsonify({
                'error': 'Token inválido o expirado',
                'mensaje': 'El token proporcionado no es válido o ha expirado'
            }), 401
        
        # Inyectar información del usuario en el contexto
        g.usuario = payload
        
        return f(*args, **kwargs)
    
    return decorated_function


def require_role(*roles_permitidos):
    """
    Decorator para proteger endpoints que requieren roles específicos
    
    Verifica que el usuario autenticado tenga uno de los roles permitidos.
    DEBE usarse después de @require_auth
    
    Args:
        roles_permitidos: Uno o más roles que tienen acceso (ej: 'VENDEDOR', 'ADMIN')
    
    Uso:
        @bp.route('/solo-vendedores')
        @require_auth
        @require_role('VENDEDOR')
        def endpoint_vendedores():
            return {'mensaje': 'Solo vendedores'}
        
        @bp.route('/vendedores-y-clientes')
        @require_auth
        @require_role('VENDEDOR', 'CLIENTE')
        def endpoint_multiple():
            return {'mensaje': 'Vendedores o clientes'}
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Verificar que el usuario esté autenticado (debe haberse ejecutado @require_auth)
            if not hasattr(g, 'usuario'):
                logger.error("require_role usado sin require_auth")
                return jsonify({
                    'error': 'Error de configuración',
                    'mensaje': 'Endpoint mal configurado'
                }), 500
            
            # Obtener el rol del usuario
            tipo_usuario = g.usuario.get('tipo_usuario')
            
            if not tipo_usuario:
                logger.warning("Token sin tipo_usuario")
                return jsonify({
                    'error': 'Token inválido',
                    'mensaje': 'El token no contiene información de rol'
                }), 401
            
            # Verificar que el usuario tenga un rol permitido
            if tipo_usuario not in roles_permitidos:
                logger.warning(f"Acceso denegado para rol {tipo_usuario} en endpoint {request.path}")
                return jsonify({
                    'error': 'Acceso denegado',
                    'mensaje': f'Este endpoint requiere uno de los siguientes roles: {", ".join(roles_permitidos)}'
                }), 403
            
            return f(*args, **kwargs)
        
        return decorated_function
    
    return decorator


def get_current_user():
    """
    Obtiene la información del usuario autenticado desde el contexto
    
    Returns:
        dict: Información del usuario si está autenticado, None en caso contrario
        
    Uso:
        @bp.route('/mi-perfil')
        @require_auth
        def mi_perfil():
            usuario = get_current_user()
            return {'usuario': usuario}
    """
    return getattr(g, 'usuario', None)

