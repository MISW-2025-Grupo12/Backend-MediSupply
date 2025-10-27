"""
Auth-Service: Servicio centralizado de autenticación y autorización
"""
from flask import Flask, request, Response, jsonify
from flask_cors import CORS
import jwt
from datetime import datetime, timedelta
import os
import json
import re
import requests
import logging
from config.version import get_version_info

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Configuración JWT
JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'medisupply-jwt-secret-key-production-2024')
JWT_ALGORITHM = 'HS256'
TOKEN_EXPIRATION_HOURS = int(os.getenv('TOKEN_EXPIRATION_HOURS', '24'))

# Configuración de servicios
USUARIOS_SERVICE_URL = os.getenv('USUARIOS_SERVICE_URL', 'http://usuarios:5001')

# Cargar permisos desde archivo
PERMISSIONS = {}

def load_permissions():
    """Carga la configuración de permisos desde el archivo JSON"""
    try:
        config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'permissions.json')
        with open(config_path, 'r', encoding='utf-8') as f:
            perms = json.load(f)
            # Filtrar comentarios
            return {k: v for k, v in perms.items() if not k.startswith('_')}
    except Exception as e:
        logger.error(f"Error cargando permisos: {e}")
        return {}

PERMISSIONS = load_permissions()
logger.info(f"✅ Permisos cargados: {len(PERMISSIONS)} reglas")


def generar_token(usuario_id: str, tipo_usuario: str, email: str) -> str:
    """
    Genera un token JWT para un usuario autenticado
    
    Args:
        usuario_id: ID del usuario
        tipo_usuario: Tipo de usuario (VENDEDOR, CLIENTE, PROVEEDOR, ADMINISTRADOR, REPARTIDOR)
        email: Email del usuario
        
    Returns:
        Token JWT como string
    """
    try:
        expiracion = datetime.utcnow() + timedelta(hours=TOKEN_EXPIRATION_HOURS)
        
        payload = {
            'usuario_id': usuario_id,
            'tipo_usuario': tipo_usuario,
            'email': email,
            'exp': expiracion,
            'iat': datetime.utcnow()
        }
        
        token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
        logger.info(f"Token generado para {email} ({tipo_usuario})")
        return token
        
    except Exception as e:
        logger.error(f"Error generando token JWT: {e}")
        raise


def verificar_token(token: str) -> dict:
    """
    Verifica y decodifica un token JWT
    
    Args:
        token: Token JWT a verificar
        
    Returns:
        Payload del token si es válido, None si no es válido
    """
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
        
    except jwt.ExpiredSignatureError:
        logger.warning("Token JWT expirado")
        return None
        
    except jwt.InvalidTokenError as e:
        logger.warning(f"Token JWT inválido: {e}")
        return None
        
    except Exception as e:
        logger.error(f"Error verificando token JWT: {e}")
        return None


def match_path_pattern(pattern, path):
    """Compara path con patrón regex"""
    try:
        return re.match(f'^{pattern}$', path) is not None
    except Exception as e:
        logger.error(f"Error en regex pattern '{pattern}': {e}")
        return False


def get_required_roles(method, path):
    """
    Obtiene los roles requeridos para un método y path específico
    
    Returns:
        Lista de roles permitidos, o ['AUTHENTICATED'] si no hay regla específica
    """
    key = f"{method}:{path}"
    
    # Buscar coincidencia exacta
    if key in PERMISSIONS:
        return PERMISSIONS[key]
    
    # Buscar con patrones regex
    for pattern, roles in PERMISSIONS.items():
        try:
            pattern_method, pattern_path = pattern.split(':', 1)
            if pattern_method == method and match_path_pattern(pattern_path, path):
                return roles
        except Exception as e:
            logger.error(f"Error procesando patrón {pattern}: {e}")
            continue
    
    # Por defecto: requiere autenticación (cualquier usuario autenticado)
    return ['AUTHENTICATED']


@app.route('/login', methods=['POST'])
def login():
    """
    Endpoint de login - Valida credenciales y genera token JWT
    
    Request Body:
        {
            "email": "string",
            "password": "string"
        }
    
    Responses:
        200: Login exitoso - retorna token JWT
        401: Credenciales inválidas
        400: Datos inválidos
        500: Error interno del servidor
    """
    try:
        datos = request.json
        
        # Validación básica
        if not datos:
            return jsonify({'error': 'Se requiere un JSON válido'}), 400
        
        if 'email' not in datos or not datos['email']:
            return jsonify({'error': 'El email es requerido'}), 400
        
        if 'password' not in datos or not datos['password']:
            return jsonify({'error': 'La contraseña es requerida'}), 400
        
        email = datos['email']
        password = datos['password']
        
        logger.info(f"🔐 Intento de login: {email}")
        
        # Llamar al servicio de Usuarios para validar credenciales
        try:
            response = requests.post(
                f"{USUARIOS_SERVICE_URL}/usuarios/api/auth/validate-credentials",
                json={'email': email, 'password': password},
                timeout=5
            )
            
            if response.status_code == 200:
                user_data = response.json()
                
                # Generar token JWT
                token = generar_token(
                    usuario_id=user_data['id'],
                    tipo_usuario=user_data['tipo_usuario'],
                    email=user_data['email']
                )
                
                # Preparar respuesta
                respuesta = {
                    'access_token': token,
                    'token_type': 'Bearer',
                    'expires_in': TOKEN_EXPIRATION_HOURS * 3600,
                    'user_info': user_data
                }
                
                logger.info(f"✅ Login exitoso: {email} ({user_data['tipo_usuario']})")
                return jsonify(respuesta), 200
                
            elif response.status_code == 401:
                logger.warning(f"❌ Credenciales inválidas: {email}")
                return jsonify({'error': 'Credenciales inválidas'}), 401
                
            else:
                logger.error(f"Error del servicio de usuarios: {response.status_code}")
                return jsonify({'error': 'Error interno del servidor'}), 500
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Error conectando con servicio de Usuarios: {e}")
            return jsonify({'error': 'Servicio de autenticación no disponible'}), 503
        
    except Exception as e:
        logger.error(f"Error en login: {e}")
        return jsonify({'error': f'Error interno del servidor: {str(e)}'}), 500


@app.route('/verify', methods=['GET', 'POST'])
def verify():
    """
    Endpoint de verificación - Valida token JWT y autorización por roles
    
    Headers esperados (de Nginx):
        Authorization: Bearer <token>
        X-Original-Method: GET/POST/etc
        X-Original-URI: /path/completo
    
    Responses:
        200: Token válido y autorizado - headers X-User-Id, X-User-Role, X-User-Email
        401: Token inválido o ausente
        403: Token válido pero rol no autorizado
    """
    try:
        # Obtener información del request original
        original_method = request.headers.get('X-Original-Method', request.method)
        original_uri = request.headers.get('X-Original-URI', request.path)
        auth_header = request.headers.get('Authorization', '')
        
        logger.info(f"🔍 Verificando: {original_method} {original_uri}")
        
        # Verificar permisos públicos primero
        required_roles = get_required_roles(original_method, original_uri)
        
        if '*' in required_roles:
            logger.info(f"✅ Endpoint público - acceso permitido")
            response = Response('', status=200)
            response.headers['X-Public-Endpoint'] = 'true'
            return response
        
        # Requiere autenticación - validar token
        if not auth_header.startswith('Bearer '):
            logger.warning(f"❌ Sin token de autorización")
            return Response('Token required', status=401)
        
        token = auth_header.split(' ')[1]
        
        # Verificar token
        payload = verificar_token(token)
        
        if not payload:
            logger.warning(f"❌ Token inválido")
            return Response('Invalid or expired token', status=401)
        
        user_role = payload.get('tipo_usuario', '')
        user_id = payload.get('usuario_id', '')
        user_email = payload.get('email', '')
        
        logger.info(f"👤 Usuario: {user_email} (ID: {user_id}, Rol: {user_role})")
        logger.info(f"🔒 Roles requeridos: {required_roles}")
        
        # Verificar autorización por rol
        if 'AUTHENTICATED' in required_roles or user_role in required_roles:
            logger.info(f"✅ Autorizado")
            response = Response('', status=200)
            response.headers['X-User-Id'] = user_id
            response.headers['X-User-Role'] = user_role
            response.headers['X-User-Email'] = user_email
            return response
        
        # Rol no autorizado
        logger.warning(f"❌ Rol {user_role} no permitido. Requiere: {required_roles}")
        return Response(f'Forbidden: requires one of {required_roles}', status=403)
        
    except Exception as e:
        logger.error(f"Error en verify: {e}")
        return Response('Internal server error', status=500)


@app.route('/health', methods=['GET'])
def health():
    """Endpoint de health check"""
    return jsonify({
        'status': 'up',
        'service': 'auth-service',
        'version': '1.0.0',
        'permissions_loaded': len(PERMISSIONS),
        'usuarios_service': USUARIOS_SERVICE_URL
    }), 200


@app.route('/', methods=['GET'])
def root():
    """Endpoint raíz con información del servicio"""
    return jsonify({
        'service': 'MediSupply Auth Service',
        'version': '1.0.0',
        'endpoints': {
            'POST /login': 'Autenticación de usuarios',
            'GET/POST /verify': 'Verificación de tokens y autorización',
            'GET /health': 'Health check',
            'GET /version': 'Información de versión del servicio',
            'POST /reload-permissions': 'Recargar permisos sin reiniciar'
        }
    }), 200


@app.route('/reload-permissions', methods=['POST'])
def reload_permissions():
    """
    Recarga los permisos desde el archivo permissions.json sin reiniciar el servicio
    
    Útil para actualizar permisos en caliente durante desarrollo/producción
    """
    global PERMISSIONS
    
    try:
        PERMISSIONS = load_permissions()
        logger.info(f"🔄 Permisos recargados: {len(PERMISSIONS)} reglas")
        
        return jsonify({
            'success': True,
            'message': 'Permisos recargados exitosamente',
            'permissions_count': len(PERMISSIONS)
        }), 200
        
    except Exception as e:
        logger.error(f"❌ Error recargando permisos: {e}")
        return jsonify({
            'success': False,
            'error': f'Error recargando permisos: {str(e)}'
        }), 500


@app.route('/version', methods=['GET'])
def version():
    """
    Endpoint de versión - Retorna información de la versión del servicio
    
    Responses:
        200: Información de versión
            {
                "version": "1.0.0",
                "build_date": "2025-10-26T15:30:00Z",
                "commit_hash": "abc123",
                "environment": "production"
            }
    """
    return jsonify(get_version_info()), 200


if __name__ == '__main__':
    port = int(os.getenv('PORT', 5004))
    host = os.getenv('HOST', '0.0.0.0')
    debug = os.getenv('FLASK_ENV', 'production') == 'development'
    
    logger.info(f"🚀 Iniciando Auth-Service en {host}:{port}")
    logger.info(f"📋 Permisos cargados: {len(PERMISSIONS)} reglas")
    logger.info(f"🔗 Servicio de Usuarios: {USUARIOS_SERVICE_URL}")
    
    app.run(host=host, port=port, debug=debug)

