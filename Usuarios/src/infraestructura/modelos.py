from config.db import db
import uuid
from datetime import datetime
import bcrypt
from enum import Enum

class ProveedorModel(db.Model):
    __tablename__ = 'proveedores'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    nombre = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    identificacion = db.Column(db.String(20), nullable=False)
    telefono = db.Column(db.String(20), nullable=False)
    direccion = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'email': self.email,
            'identificacion': self.identificacion,
            'telefono': self.telefono,
            'direccion': self.direccion,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class VendedorModel(db.Model):
    __tablename__ = 'vendedores'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    nombre = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    identificacion = db.Column(db.String(20), nullable=False)
    telefono = db.Column(db.String(20), nullable=False)
    direccion = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'email': self.email,
            'identificacion': self.identificacion,
            'telefono': self.telefono,
            'direccion': self.direccion,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class ClienteModel(db.Model):
    __tablename__ = 'clientes'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    nombre = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    identificacion = db.Column(db.String(20), nullable=False)
    telefono = db.Column(db.String(20), nullable=False)
    direccion = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'email': self.email,
            'identificacion': self.identificacion,
            'telefono': self.telefono,
            'direccion': self.direccion,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


class TipoUsuario(str, Enum):
    """Enum para tipos de usuario"""
    VENDEDOR = 'VENDEDOR'
    CLIENTE = 'CLIENTE'
    PROVEEDOR = 'PROVEEDOR'


class UsuarioModel(db.Model):
    """Modelo de autenticación para usuarios"""
    __tablename__ = 'usuarios'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = db.Column(db.String(100), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    tipo_usuario = db.Column(db.String(20), nullable=False)
    identificacion = db.Column(db.String(20), unique=True, nullable=False, index=True)
    entidad_id = db.Column(db.String(36), nullable=False)  # ID de Vendedor/Cliente/Proveedor
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def set_password(self, password: str):
        """Hashea y establece la contraseña"""
        salt = bcrypt.gensalt()
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def verificar_password(self, password: str) -> bool:
        """Verifica si la contraseña es correcta"""
        return bcrypt.checkpw(
            password.encode('utf-8'), 
            self.password_hash.encode('utf-8')
        )
    
    def to_dict(self):
        """Convierte el modelo a diccionario (sin password_hash)"""
        return {
            'id': self.id,
            'email': self.email,
            'tipo_usuario': self.tipo_usuario,
            'identificacion': self.identificacion,
            'entidad_id': self.entidad_id,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }