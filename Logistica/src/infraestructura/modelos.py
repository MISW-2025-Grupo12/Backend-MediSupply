from config.db import db
import uuid
from datetime import datetime
from sqlalchemy.dialects.sqlite import JSON

class EntregaModel(db.Model):
    __tablename__ = 'entregas'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    direccion = db.Column(db.String(255), nullable=False)
    fecha_entrega = db.Column(db.DateTime, nullable=False)
    pedido = db.Column(JSON, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "direccion": self.direccion,
            "fecha_entrega": self.fecha_entrega.isoformat(),
            "pedido": self.pedido,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }

class BodegaModel(db.Model):
    __tablename__ = 'bodegas'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    nombre = db.Column(db.String(100), nullable=False)
    direccion = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'nombre': self.nombre,
            'direccion': self.direccion,
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
    bodega_id = db.Column(db.String(36), nullable=True)
    pasillo = db.Column(db.String(10), nullable=True)
    estante = db.Column(db.String(10), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'producto_id': self.producto_id,
            'cantidad_disponible': self.cantidad_disponible,
            'cantidad_reservada': self.cantidad_reservada,
            'fecha_vencimiento': self.fecha_vencimiento.isoformat(),
            'bodega_id': self.bodega_id,
            'pasillo': self.pasillo,
            'estante': self.estante,
            'ubicacion_fisica': f"Bodega #{self.bodega_id} - Pasillo {self.pasillo} - Estante {self.estante}" if self.bodega_id else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }