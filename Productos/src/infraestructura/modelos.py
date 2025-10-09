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
    stock = db.Column(db.Integer, nullable=False)
    fecha_vencimiento = db.Column(db.DateTime, nullable=False)
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
            'stock': self.stock,
            'fecha_vencimiento': self.fecha_vencimiento.isoformat(),
            'categoria': self.categoria,
            'categoria_id': self.categoria_id,
            'proveedor_id': self.proveedor_id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
