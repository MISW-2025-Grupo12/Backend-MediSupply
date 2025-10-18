from dataclasses import dataclass, field
import uuid
from datetime import datetime
from seedwork.aplicacion.dto import DTO
from typing import Optional, Any

@dataclass(frozen=True)
class EntregaDTO(DTO):
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    direccion: str = ""
    fecha_entrega: datetime = datetime.now()
    pedido: Optional[Any] = None

@dataclass(frozen=True)
class InventarioDTO(DTO):
    producto_id: str
    cantidad_disponible: int
    cantidad_reservada: int
    fecha_vencimiento: datetime
    bodega_id: str = None
    pasillo: str = None
    estante: str = None
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    requiere_cadena_frio: bool = False

@dataclass(frozen=True)
class BodegaDTO(DTO):
    nombre: str
    direccion: str
    id: str = field(default_factory=lambda: str(uuid.uuid4()))