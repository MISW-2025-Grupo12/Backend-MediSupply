from dataclasses import dataclass, field
import uuid
from seedwork.aplicacion.dto import DTO

@dataclass(frozen=True)
class ProveedorDTO(DTO):
    nombre: str
    email: str
    direccion: str
    id: uuid.UUID = field(default_factory=uuid.uuid4)
