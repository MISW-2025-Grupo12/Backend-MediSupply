from config.db import db
import uuid
from datetime import datetime, date, time

class VisitaModel(db.Model):
    __tablename__ = 'visitas'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    vendedor_id = db.Column(db.String(36), nullable=False)
    cliente_id = db.Column(db.String(36), nullable=False)
    fecha_programada = db.Column(db.DateTime, nullable=False)
    direccion = db.Column(db.Text, nullable=False)
    telefono = db.Column(db.String(20), nullable=False)
    estado = db.Column(db.String(20), nullable=False, default='pendiente')
    descripcion = db.Column(db.Text, nullable=True)
    fecha_realizada = db.Column(db.Date, nullable=True)
    hora_realizada = db.Column(db.Time, nullable=True)
    novedades = db.Column(db.Text, nullable=True)
    pedido_generado = db.Column(db.Boolean, nullable=True, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'vendedor_id': self.vendedor_id,
            'cliente_id': self.cliente_id,
            'fecha_programada': self.fecha_programada.isoformat(),
            'direccion': self.direccion,
            'telefono': self.telefono,
            'estado': self.estado,
            'descripcion': self.descripcion,
            'fecha_realizada': self.fecha_realizada.isoformat() if self.fecha_realizada else None,
            'hora_realizada': self.hora_realizada.isoformat() if self.hora_realizada else None,
            'novedades': self.novedades,
            'pedido_generado': self.pedido_generado,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
