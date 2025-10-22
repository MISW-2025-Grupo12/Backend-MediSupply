"""
Configuración y utilidades para JWT (JSON Web Tokens)
"""
import os
import jwt
from datetime import datetime, timedelta
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)

# Configuración JWT
JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'medisupply-secret-key-change-in-production')
JWT_ALGORITHM = 'HS256'
TOKEN_EXPIRATION_HOURS = int(os.getenv('TOKEN_EXPIRATION_HOURS', '24'))


def generar_token(usuario_id: str, tipo_usuario: str, email: str) -> str:
    """
    Genera un token JWT para un usuario autenticado
    
    Args:
        usuario_id: ID del usuario
        tipo_usuario: Tipo de usuario (VENDEDOR, CLIENTE, PROVEEDOR)
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
        return token
        
    except Exception as e:
        logger.error(f"Error generando token JWT: {e}")
        raise


def verificar_token(token: str) -> Optional[Dict]:
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


def extraer_token_de_header(authorization_header: Optional[str]) -> Optional[str]:
    """
    Extrae el token del header Authorization
    
    Args:
        authorization_header: Header Authorization (formato: "Bearer <token>")
        
    Returns:
        Token JWT si se encuentra, None en caso contrario
    """
    if not authorization_header:
        return None
        
    parts = authorization_header.split()
    
    if len(parts) != 2 or parts[0].lower() != 'bearer':
        return None
        
    return parts[1]

