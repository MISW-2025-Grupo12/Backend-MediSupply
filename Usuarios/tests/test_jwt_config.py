"""
Tests para la configuración y funciones JWT
"""
import pytest
import jwt
import time
from datetime import datetime, timedelta
from config.jwt_config import (
    generar_token,
    verificar_token,
    JWT_SECRET_KEY,
    TOKEN_EXPIRATION_HOURS
)


class TestJWTConfig:
    """Tests para las funciones de JWT"""
    
    def test_generar_token_exitoso(self):
        """Test generar token JWT con datos válidos"""
        # Arrange
        usuario_id = "test-user-123"
        tipo_usuario = "vendedor"
        email = "test@example.com"
        
        # Act
        token = generar_token(usuario_id, tipo_usuario, email)
        
        # Assert
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0
        
        # Verificar que el token se puede decodificar
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])
        assert payload['usuario_id'] == usuario_id
        assert payload['tipo_usuario'] == tipo_usuario
        assert payload['email'] == email
        assert 'exp' in payload
        assert 'iat' in payload
    
    def test_generar_token_verifica_expiracion(self):
        """Test que el token generado tiene la expiración correcta"""
        # Arrange
        usuario_id = "test-user-123"
        tipo_usuario = "vendedor"
        email = "test@example.com"
        
        # Act
        token = generar_token(usuario_id, tipo_usuario, email)
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=['HS256'])
        
        # Assert
        exp_time = datetime.fromtimestamp(payload['exp'])
        iat_time = datetime.fromtimestamp(payload['iat'])
        diferencia = (exp_time - iat_time).total_seconds() / 3600
        
        assert diferencia == TOKEN_EXPIRATION_HOURS
    
    def test_verificar_token_valido(self):
        """Test verificar token JWT válido"""
        # Arrange
        token = generar_token("user-123", "vendedor", "test@example.com")
        
        # Act
        resultado = verificar_token(token)
        
        # Assert
        assert resultado is not None
        assert isinstance(resultado, dict)
        assert resultado['usuario_id'] == "user-123"
    
    def test_verificar_token_invalido(self):
        """Test verificar token JWT inválido"""
        # Arrange
        token_invalido = "token.invalido.aqui"
        
        # Act
        resultado = verificar_token(token_invalido)
        
        # Assert
        assert resultado is None
    
    def test_verificar_token_expirado(self):
        """Test verificar token JWT expirado"""
        # Arrange - Crear token con expiración inmediata
        payload = {
            'usuario_id': 'test-user',
            'tipo_usuario': 'vendedor',
            'email': 'test@example.com',
            'exp': datetime.utcnow() - timedelta(hours=1),  # Expirado hace 1 hora
            'iat': datetime.utcnow() - timedelta(hours=2)
        }
        token_expirado = jwt.encode(payload, JWT_SECRET_KEY, algorithm='HS256')
        
        # Act
        resultado = verificar_token(token_expirado)
        
        # Assert
        assert resultado is None
    
    def test_verificar_token_vacio(self):
        """Test verificar token JWT vacío"""
        # Act
        resultado = verificar_token("")
        
        # Assert
        assert resultado is None
    
    def test_verificar_token_none(self):
        """Test verificar token JWT None"""
        # Act
        resultado = verificar_token(None)
        
        # Assert
        assert resultado is None
    
    def test_verificar_y_decodificar_token_exitoso(self):
        """Test verificar y decodificar token JWT válido"""
        # Arrange
        usuario_id = "user-123"
        tipo_usuario = "cliente"
        email = "cliente@example.com"
        token = generar_token(usuario_id, tipo_usuario, email)
        
        # Act
        payload = verificar_token(token)
        
        # Assert
        assert payload is not None
        assert payload['usuario_id'] == usuario_id
        assert payload['tipo_usuario'] == tipo_usuario
        assert payload['email'] == email
        assert 'exp' in payload
        assert 'iat' in payload
    
    def test_verificar_token_con_firma_incorrecta(self):
        """Test verificar token JWT con firma incorrecta"""
        # Arrange - Crear token con una clave diferente
        payload = {
            'usuario_id': 'test-user',
            'tipo_usuario': 'vendedor',
            'email': 'test@example.com',
            'exp': datetime.utcnow() + timedelta(hours=24),
            'iat': datetime.utcnow()
        }
        token_mal_firmado = jwt.encode(payload, 'clave_incorrecta', algorithm='HS256')
        
        # Act
        resultado = verificar_token(token_mal_firmado)
        
        # Assert
        assert resultado is None
    
    def test_generar_token_con_diferentes_tipos_usuario(self):
        """Test generar tokens para diferentes tipos de usuario"""
        # Arrange & Act
        token_vendedor = generar_token("user-1", "vendedor", "vendedor@test.com")
        token_cliente = generar_token("user-2", "cliente", "cliente@test.com")
        token_proveedor = generar_token("user-3", "proveedor", "proveedor@test.com")
        
        # Assert
        payload_vendedor = verificar_token(token_vendedor)
        payload_cliente = verificar_token(token_cliente)
        payload_proveedor = verificar_token(token_proveedor)
        
        assert payload_vendedor['tipo_usuario'] == 'vendedor'
        assert payload_cliente['tipo_usuario'] == 'cliente'
        assert payload_proveedor['tipo_usuario'] == 'proveedor'

