from dataclasses import dataclass, field
from seedwork.dominio.entidades import AgregacionRaiz
from .objetos_valor import Nombre, Email, Direccion
from .eventos import ProveedorCreado

@dataclass
class Proveedor(AgregacionRaiz):
    nombre: Nombre = field(default_factory=lambda: Nombre(""))
    email: Email = field(default_factory=lambda: Email(""))
    direccion: Direccion = field(default_factory=lambda: Direccion(""))
    
    def disparar_evento_creacion(self):
        evento = ProveedorCreado(
            proveedor_id=self.id,
            nombre=self.nombre.nombre,
            email=self.email.email,
            direccion=self.direccion.direccion
        )
        return evento
