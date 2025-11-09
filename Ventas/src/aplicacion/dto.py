from dataclasses import dataclass, field
from typing import Optional
import uuid
from datetime import datetime, date, time
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
    fecha_realizada: date = None
    hora_realizada: time = None
    novedades: str = None
    pedido_generado: bool = None
    id: uuid.UUID = field(default_factory=uuid.uuid4)

@dataclass(frozen=True)
class ItemPedidoDTO(DTO):
    producto_id: str
    nombre_producto: str
    cantidad: int
    precio_unitario: float
    subtotal: float
    id: uuid.UUID = field(default_factory=uuid.uuid4)

@dataclass(frozen=True)
class PedidoDTO(DTO):
    vendedor_id: str
    cliente_id: str
    estado: str
    total: float
    items: list = field(default_factory=list)
    id: uuid.UUID = field(default_factory=uuid.uuid4)

@dataclass(frozen=True)
class EvidenciaVisitaDTO(DTO):
    visita_id: str
    archivo_url: str
    nombre_archivo: str
    formato: str
    tamaño_bytes: int
    comentarios: str
    vendedor_id: str
    created_at: datetime
    id: uuid.UUID = field(default_factory=uuid.uuid4)

@dataclass(frozen=True)
class PlanDTO(DTO):
    id: uuid.UUID = field(default_factory=uuid.uuid4)
    nombre: str = ""
    id_usuario: str = ""
    fecha_inicio: datetime = None
    fecha_fin: datetime = None

@dataclass(frozen=True)
class SugerenciaClienteDTO(DTO):
    cliente_id: str
    evidencia_id: Optional[str] = None
    sugerencias_texto: str = ""
    modelo_usado: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    id: uuid.UUID = field(default_factory=uuid.uuid4)