from config.db import db
import uuid
from datetime import datetime

class EntregaModel(db.Model):
    __tablename__ = 'entregas'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    direccion = db.Column(db.String(255), nullable=False)
    fecha_entrega = db.Column(db.DateTime, nullable=False)
    producto_id = db.Column(db.String(36), nullable=False)
    cliente_id = db.Column(db.String(36), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'direccion': self.direccion,
            'fecha_entrega': self.fecha_entrega.isoformat(),
            'producto_id': self.producto_id,
            'cliente_id': self.cliente_id,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class InventarioModel(db.Model):
    __tablename__ = 'inventario'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    producto_id = db.Column(db.String(36), nullable=False)
    cantidad_disponible = db.Column(db.Integer, nullable=False, default=0)
    cantidad_reservada = db.Column(db.Integer, nullable=False, default=0)
    fecha_vencimiento = db.Column(db.DateTime, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'producto_id': self.producto_id,
            'cantidad_disponible': self.cantidad_disponible,
            'cantidad_reservada': self.cantidad_reservada,
            'fecha_vencimiento': self.fecha_vencimiento.isoformat(),
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }