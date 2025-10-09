from dataclasses import dataclass
from seedwork.dominio.eventos import EventoDominio
import uuid

@dataclass
class ProveedorCreado(EventoDominio):
    proveedor_id: uuid.UUID = None
    nombre: str = ""
    email: str = ""
    direccion: str = ""
    
    def _get_datos_evento(self) -> dict:
        return {
            'proveedor_id': str(self.proveedor_id),
            'nombre': self.nombre,
            'email': self.email,
            'direccion': self.direccion
        }
