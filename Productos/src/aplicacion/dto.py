from dataclasses import dataclass, field
import uuid
from datetime import datetime
from seedwork.aplicacion.dto import DTO

@dataclass(frozen=True)
class ProductoDTO(DTO):
    nombre: str
    descripcion: str
    precio: float
    categoria: str
    categoria_id: str
    proveedor_id: str
    id: uuid.UUID = field(default_factory=uuid.uuid4)

@dataclass(frozen=True)
class CategoriaDTO(DTO):
    nombre: str
    descripcion: str
    id: uuid.UUID = field(default_factory=uuid.uuid4)
