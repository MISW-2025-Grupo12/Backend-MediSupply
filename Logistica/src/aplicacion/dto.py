from dataclasses import dataclass, field
import uuid
from datetime import datetime
from seedwork.aplicacion.dto import DTO

@dataclass(frozen=True)
class EntregaDTO(DTO):
    direccion: str
    fecha_entrega: datetime
    producto_id: str
    cliente_id: str
    id: uuid.UUID = field(default_factory=uuid.uuid4)
