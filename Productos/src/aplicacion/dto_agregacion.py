from dataclasses import dataclass, field
import uuid
from datetime import datetime
from seedwork.aplicacion.dto import DTO

@dataclass(frozen=True)
class ProductoAgregacionDTO(DTO):
    """DTO de agregación completa para productos con categoría y proveedor"""
    # Datos del producto
    id: uuid.UUID
    nombre: str
    descripcion: str
    precio: float
    stock: int
    fecha_vencimiento: datetime
    
    # Datos de categoría (obtenidos durante validación)
    categoria_id: str
    categoria_nombre: str
    categoria_descripcion: str
    
    # Datos de proveedor (obtenidos durante validación)
    proveedor_id: str
    proveedor_nombre: str
    proveedor_email: str
    proveedor_direccion: str
