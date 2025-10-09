from dataclasses import dataclass
from datetime import datetime
from seedwork.dominio.eventos import EventoDominio
import uuid

@dataclass
class EntregaCreada(EventoDominio):
    entrega_id: uuid.UUID = None
    direccion: str = ""
    fecha_entrega: datetime = None
    producto_id: str = ""
    cliente_id: str = ""

    def _get_datos_evento(self) -> dict:
        """Retorna los datos estructurados del evento para trazabilidad u observabilidad."""
        return {
            'entrega_id': str(self.entrega_id),
            'direccion': self.direccion,
            'fecha_entrega': self.fecha_entrega.isoformat() if self.fecha_entrega else None,
            'producto_id': self.producto_id,
            'cliente_id': self.cliente_id
        }
