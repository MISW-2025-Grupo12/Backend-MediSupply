from dataclasses import dataclass, field
import uuid
from datetime import datetime
from seedwork.aplicacion.dto import DTO

@dataclass(frozen=True)
class VisitaDTO(DTO):
    vendedor_id: str
    cliente_id: str
    fecha_programada: datetime
    direccion: str
    telefono: str
    estado: str
    descripcion: str
    id: uuid.UUID = field(default_factory=uuid.uuid4)
