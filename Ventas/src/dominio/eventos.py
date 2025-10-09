from dataclasses import dataclass
from seedwork.dominio.eventos import EventoDominio
import uuid
from datetime import datetime

@dataclass
class VisitaCreada(EventoDominio):
    visita_id: uuid.UUID = None
    vendedor_id: str = ""
    cliente_id: str = ""
    fecha_programada: datetime = None
    direccion: str = ""
    telefono: str = ""
    estado: str = ""
    descripcion: str = ""
    
    def _get_datos_evento(self) -> dict:
        return {
            'visita_id': str(self.visita_id),
            'vendedor_id': self.vendedor_id,
            'cliente_id': self.cliente_id,
            'fecha_programada': self.fecha_programada.isoformat() if self.fecha_programada else None,
            'direccion': self.direccion,
            'telefono': self.telefono,
            'estado': self.estado,
            'descripcion': self.descripcion
        }
