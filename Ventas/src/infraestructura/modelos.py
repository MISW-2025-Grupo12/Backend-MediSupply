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

class PedidoModel(db.Model):
    __tablename__ = 'pedidos'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    vendedor_id = db.Column(db.String(36), nullable=False)
    cliente_id = db.Column(db.String(36), nullable=False)
    estado = db.Column(db.String(20), nullable=False, default='borrador')
    total = db.Column(db.Float, nullable=False, default=0.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'vendedor_id': self.vendedor_id,
            'cliente_id': self.cliente_id,
            'estado': self.estado,
            'total': self.total,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class ItemPedidoModel(db.Model):
    __tablename__ = 'items_pedido'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    pedido_id = db.Column(db.String(36), db.ForeignKey('pedidos.id'), nullable=False)
    producto_id = db.Column(db.String(36), nullable=False)
    nombre_producto = db.Column(db.String(255), nullable=False)
    cantidad = db.Column(db.Integer, nullable=False)
    precio_unitario = db.Column(db.Float, nullable=False)
    subtotal = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'pedido_id': self.pedido_id,
            'producto_id': self.producto_id,
            'nombre_producto': self.nombre_producto,
            'cantidad': self.cantidad,
            'precio_unitario': self.precio_unitario,
            'subtotal': self.subtotal,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

class EvidenciaVisitaModel(db.Model):
    __tablename__ = 'evidencias_visitas'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    visita_id = db.Column(db.String(36), db.ForeignKey('visitas.id'), nullable=False)
    archivo_url = db.Column(db.Text, nullable=False)
    nombre_archivo = db.Column(db.String(255), nullable=False)
    formato = db.Column(db.String(10), nullable=False)
    tamaño_bytes = db.Column(db.Integer, nullable=False)
    comentarios = db.Column(db.Text, nullable=True)
    vendedor_id = db.Column(db.String(36), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'visita_id': self.visita_id,
            'archivo_url': self.archivo_url,
            'nombre_archivo': self.nombre_archivo,
            'formato': self.formato,
            'tamaño_bytes': self.tamaño_bytes,
            'tamaño_mb': round(self.tamaño_bytes / 1024 / 1024, 2),
            'comentarios': self.comentarios,
            'vendedor_id': self.vendedor_id,
            'created_at': self.created_at.isoformat()
        }