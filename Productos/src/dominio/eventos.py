from dataclasses import dataclass
from datetime import datetime
from seedwork.dominio.eventos import EventoDominio
import uuid

@dataclass
class ProductoCreado(EventoDominio):
    producto_id: uuid.UUID = None
    nombre: str = ""
    descripcion: str = ""
    precio: float = 0.0
    categoria: str = ""
    categoria_id: str = ""
    proveedor_id: str = ""
    
    def _get_datos_evento(self) -> dict:
        return {
            'producto_id': str(self.producto_id),
            'nombre': self.nombre,
            'descripcion': self.descripcion,
            'precio': self.precio,
            'categoria': self.categoria,
            'categoria_id': self.categoria_id,
            'proveedor_id': self.proveedor_id
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

