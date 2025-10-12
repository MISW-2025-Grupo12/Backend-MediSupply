from dataclasses import dataclass
from datetime import datetime
from seedwork.dominio.eventos import EventoDominio
import uuid

@dataclass
class EntregaCreada(EventoDominio):
    entrega_id: uuid.UUID = None
    direccion: str = ""
    fecha_entrega: datetime = None
    pedido: dict = None  # ✅ reemplaza producto_id y cliente_id

    def _get_datos_evento(self) -> dict:
        """Retorna los datos estructurados del evento para trazabilidad u observabilidad."""
        return {
            'entrega_id': str(self.entrega_id),
            'direccion': self.direccion,
            'fecha_entrega': self.fecha_entrega.isoformat() if self.fecha_entrega else None,
            'pedido': self.pedido
        }

@dataclass
class InventarioReservado(EventoDominio):
    producto_id: str = ""
    cantidad_reservada: int = 0
    cantidad_disponible_restante: int = 0

    def _get_datos_evento(self) -> dict:
        return {
            'producto_id': self.producto_id,
            'cantidad_reservada': self.cantidad_reservada,
            'cantidad_disponible_restante': self.cantidad_disponible_restante
        }

@dataclass
class InventarioDescontado(EventoDominio):
    producto_id: str = ""
    cantidad_descontada: int = 0
    cantidad_reservada_restante: int = 0

    def _get_datos_evento(self) -> dict:
        return {
            'producto_id': self.producto_id,
            'cantidad_descontada': self.cantidad_descontada,
            'cantidad_reservada_restante': self.cantidad_reservada_restante
        }

@dataclass
class InventarioAsignado(EventoDominio):
    producto_id: uuid.UUID = None
    stock: int = 0
    fecha_vencimiento: str = ""
    
    def _get_datos_evento(self) -> dict:
        return {
            'producto_id': str(self.producto_id),
            'stock': self.stock,
            'fecha_vencimiento': self.fecha_vencimiento
        }