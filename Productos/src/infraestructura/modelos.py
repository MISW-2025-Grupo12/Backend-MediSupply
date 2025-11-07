from config.db import db
import uuid
from datetime import datetime

class CategoriaModel(db.Model):
    __tablename__ = 'categorias'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    nombre = db.Column(db.String(255), nullable=False)
    descripcion = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'descripcion': self.descripcion,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class ProductoModel(db.Model):
    __tablename__ = 'productos'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    nombre = db.Column(db.String(255), nullable=False)
    descripcion = db.Column(db.Text, nullable=False)
    precio = db.Column(db.Float, nullable=False)
    categoria = db.Column(db.String(255), nullable=False)
    categoria_id = db.Column(db.String(36), db.ForeignKey('categorias.id'), nullable=False)
    proveedor_id = db.Column(db.String(36), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'descripcion': self.descripcion,
            'precio': self.precio,
            'categoria': self.categoria,
            'categoria_id': self.categoria_id,
            'proveedor_id': self.proveedor_id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class CargaMasivaJobModel(db.Model):
    __tablename__ = 'carga_masiva_jobs'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    status = db.Column(db.String(20), nullable=False)  # pending, processing, completed, failed
    total_filas = db.Column(db.Integer, nullable=False)
    filas_procesadas = db.Column(db.Integer, default=0)
    filas_exitosas = db.Column(db.Integer, default=0)
    filas_error = db.Column(db.Integer, default=0)
    filas_rechazadas = db.Column(db.Integer, default=0)
    result_url = db.Column(db.Text, nullable=True)
    error = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        porcentaje = (self.filas_procesadas / self.total_filas * 100) if self.total_filas > 0 else 0.0
        return {
            'id': self.id,
            'status': self.status,
            'progreso': {
                'total_filas': self.total_filas,
                'filas_procesadas': self.filas_procesadas,
                'filas_exitosas': self.filas_exitosas,
                'filas_error': self.filas_error,
                'filas_rechazadas': self.filas_rechazadas,
                'porcentaje': round(porcentaje, 2)
            },
            'result_url': self.result_url,
            'error': self.error,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }