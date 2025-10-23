from dataclasses import dataclass
from seedwork.dominio.eventos import EventoDominio
import uuid
from datetime import datetime

@dataclass
class VisitaCreada(EventoDominio):
    visita_id: uuid.UUID = None
    vendedor_id: str = ""
    cliente_id: str = ""
    fecha_programada: datetime = None
    direccion: str = ""
    telefono: str = ""
    estado: str = ""
    descripcion: str = ""
    
    def _get_datos_evento(self) -> dict:
        return {
            'visita_id': str(self.visita_id),
            'vendedor_id': self.vendedor_id,
            'cliente_id': self.cliente_id,
            'fecha_programada': self.fecha_programada.isoformat() if self.fecha_programada else None,
            'direccion': self.direccion,
            'telefono': self.telefono,
            'estado': self.estado,
            'descripcion': self.descripcion
        }

@dataclass
class PedidoCreado(EventoDominio):
    pedido_id: uuid.UUID = None
    vendedor_id: str = ""
    cliente_id: str = ""
    total: float = 0.0
    
    def _get_datos_evento(self) -> dict:
        return {
            'pedido_id': str(self.pedido_id),
            'vendedor_id': self.vendedor_id,
            'cliente_id': self.cliente_id,
            'total': self.total
        }

@dataclass
class PedidoConfirmado(EventoDominio):
    pedido_id: uuid.UUID = None
    vendedor_id: str = ""
    cliente_id: str = ""
    items: list = None
    total: float = 0.0
    
    def __post_init__(self):
        if self.items is None:
            self.items = []
    
    def _get_datos_evento(self) -> dict:
        return {
            'pedido_id': str(self.pedido_id),
            'vendedor_id': self.vendedor_id,
            'cliente_id': self.cliente_id,
            'items': self.items,
            'total': self.total
        }

@dataclass
class ItemAgregado(EventoDominio):
    pedido_id: uuid.UUID = None
    item_id: uuid.UUID = None
    producto_id: str = ""
    cantidad: int = 0
    subtotal: float = 0.0
    
    def _get_datos_evento(self) -> dict:
        return {
            'pedido_id': str(self.pedido_id),
            'item_id': str(self.item_id),
            'producto_id': self.producto_id,
            'cantidad': self.cantidad,
            'subtotal': self.subtotal
        }

@dataclass
class ItemQuitado(EventoDominio):
    pedido_id: uuid.UUID = None
    item_id: uuid.UUID = None
    producto_id: str = ""
    
    def _get_datos_evento(self) -> dict:
        return {
            'pedido_id': str(self.pedido_id),
            'item_id': str(self.item_id),
            'producto_id': self.producto_id
        }

@dataclass
class EvidenciaSubida(EventoDominio):
    evidencia_id: uuid.UUID = None
    visita_id: str = ""
    vendedor_id: str = ""
    archivo_url: str = ""
    
    def _get_datos_evento(self) -> dict:
        return {
            'evidencia_id': str(self.evidencia_id),
            'visita_id': self.visita_id,
            'vendedor_id': self.vendedor_id,
            'archivo_url': self.archivo_url
        }