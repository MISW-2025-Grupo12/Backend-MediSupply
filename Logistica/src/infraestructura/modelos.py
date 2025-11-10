from config.db import db
import uuid
from datetime import datetime
from sqlalchemy.dialects.sqlite import JSON
from sqlalchemy import Boolean

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


class RutaEntregaModel(db.Model):
    __tablename__ = 'ruta_entregas'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    ruta_id = db.Column(db.String(36), db.ForeignKey('rutas.id'), nullable=False)
    entrega_id = db.Column(db.String(36), db.ForeignKey('entregas.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    entrega = db.relationship('EntregaModel', lazy='joined')

    def to_dict(self):
        return {
            'id': self.id,
            'ruta_id': self.ruta_id,
            'entrega_id': self.entrega_id,
            'created_at': self.created_at.isoformat()
        }


class RutaModel(db.Model):
    __tablename__ = 'rutas'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    fecha_ruta = db.Column(db.Date, nullable=False)
    repartidor_id = db.Column(db.String(36), nullable=False)
    estado = db.Column(db.String(20), nullable=False, default='Pendiente')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    entregas = db.relationship(
        'EntregaModel',
        secondary='ruta_entregas',
        lazy='select',
        backref=db.backref('rutas', lazy='dynamic')
    )
    asignaciones = db.relationship(
        'RutaEntregaModel',
        backref='ruta',
        lazy='select',
        cascade='all, delete-orphan'
    )

    def to_dict(self):
        return {
            'id': self.id,
            'fecha_ruta': self.fecha_ruta.isoformat(),
            'repartidor_id': self.repartidor_id,
            'estado': self.estado,
            'entregas': [entrega.id for entrega in self.entregas],
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
    requiere_cadena_frio = db.Column(Boolean, nullable=False, default=False)

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