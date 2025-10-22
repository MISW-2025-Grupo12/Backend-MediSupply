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

@dataclass
class VendedorCreado(EventoDominio):
    vendedor_id: uuid.UUID = None
    nombre: str = ""
    email: str = ""
    telefono: str = ""
    direccion: str = ""
    
    def _get_datos_evento(self) -> dict:
        return {
            'vendedor_id': str(self.vendedor_id),
            'nombre': self.nombre,
            'email': self.email,
            'telefono': self.telefono,
            'direccion': self.direccion
        }

@dataclass
class ClienteCreado(EventoDominio):
    cliente_id: uuid.UUID = None
    nombre: str = ""
    email: str = ""
    telefono: str = ""
    direccion: str = ""
    
    def _get_datos_evento(self) -> dict:
        return {
            'cliente_id': str(self.cliente_id),
            'nombre': self.nombre,
            'email': self.email,
            'telefono': self.telefono,
            'direccion': self.direccion
        }

@dataclass
class AdministradorCreado(EventoDominio):
    administrador_id: uuid.UUID = None
    nombre: str = ""
    email: str = ""
    
    def _get_datos_evento(self) -> dict:
        return {
            'administrador_id': str(self.administrador_id),
            'nombre': self.nombre,
            'email': self.email
        }

@dataclass
class RepartidorCreado(EventoDominio):
    repartidor_id: uuid.UUID = None
    nombre: str = ""
    email: str = ""
    identificacion: str = ""
    telefono: str = ""
    
    def _get_datos_evento(self) -> dict:
        return {
            'repartidor_id': str(self.repartidor_id),
            'nombre': self.nombre,
            'email': self.email,
            'identificacion': self.identificacion,
            'telefono': self.telefono
        }