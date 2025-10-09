from dataclasses import dataclass, field
import uuid
from datetime import datetime
from seedwork.aplicacion.dto import DTO

@dataclass(frozen=True)
class VisitaAgregacionDTO(DTO):
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    fecha_programada: datetime = None
    direccion: str = ""
    telefono: str = ""
    estado: str = ""
    descripcion: str = ""
    
    vendedor_id: str = ""
    vendedor_nombre: str = ""
    vendedor_email: str = ""
    vendedor_telefono: str = ""
    vendedor_direccion: str = ""
    
    cliente_id: str = ""
    cliente_nombre: str = ""
    cliente_email: str = ""
    cliente_telefono: str = ""
    cliente_direccion: str = ""
