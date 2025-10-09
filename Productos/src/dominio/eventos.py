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
    stock: int = 0
    fecha_vencimiento: datetime = None
    categoria: str = ""
    categoria_id: str = ""
    proveedor_id: str = ""
    
    def _get_datos_evento(self) -> dict:
        return {
            'producto_id': str(self.producto_id),
            'nombre': self.nombre,
            'descripcion': self.descripcion,
            'precio': self.precio,
            'stock': self.stock,
            'fecha_vencimiento': self.fecha_vencimiento.isoformat(),
            'categoria': self.categoria,
            'categoria_id': self.categoria_id,
            'proveedor_id': self.proveedor_id
        }

