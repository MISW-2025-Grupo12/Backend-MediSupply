from dataclasses import dataclass, field
import uuid
from datetime import datetime
from seedwork.aplicacion.dto import DTO

@dataclass(frozen=True)
class ProductoDTO(DTO):
    nombre: str
    descripcion: str
    precio: float
    stock: int
    fecha_vencimiento: datetime
    categoria: str
    proveedor: str
    categoria_id: str
    id: uuid.UUID = field(default_factory=uuid.uuid4)
