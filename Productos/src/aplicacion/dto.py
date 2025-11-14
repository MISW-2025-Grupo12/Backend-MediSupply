from dataclasses import dataclass, field
import uuid
from datetime import datetime
from typing import Optional
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

@dataclass
class CargaMasivaJobDTO:
    """DTO para tracking de trabajos de carga masiva. No hereda de DTO porque necesita ser mutable."""
    status: str  # pending, processing, completed, failed
    total_filas: int
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    filas_procesadas: int = 0
    filas_exitosas: int = 0
    filas_error: int = 0
    filas_rechazadas: int = 0
    result_url: Optional[str] = None
    error: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)