from dataclasses import dataclass, field
from seedwork.dominio.entidades import AgregacionRaiz
from .objetos_valor import Nombre, Email, Direccion, Telefono, Identificacion
from .eventos import ProveedorCreado, VendedorCreado, ClienteCreado, AdministradorCreado, RepartidorCreado

@dataclass
class Proveedor(AgregacionRaiz):
    nombre: Nombre = field(default_factory=lambda: Nombre(""))
    email: Email = field(default_factory=lambda: Email(""))
    identificacion: Identificacion = field(default_factory=lambda: Identificacion(""))
    telefono: Telefono = field(default_factory=lambda: Telefono(""))
    direccion: Direccion = field(default_factory=lambda: Direccion(""))
    
    def disparar_evento_creacion(self):
        evento = ProveedorCreado(
            proveedor_id=self.id,
            nombre=self.nombre.nombre,
            email=self.email.email,
            direccion=self.direccion.direccion
        )
        return evento

@dataclass
class Vendedor(AgregacionRaiz):
    nombre: Nombre = field(default_factory=lambda: Nombre(""))
    email: Email = field(default_factory=lambda: Email(""))
    identificacion: Identificacion = field(default_factory=lambda: Identificacion(""))
    telefono: Telefono = field(default_factory=lambda: Telefono(""))
    direccion: Direccion = field(default_factory=lambda: Direccion(""))
    
    def disparar_evento_creacion(self):
        evento = VendedorCreado(
            vendedor_id=self.id,
            nombre=self.nombre.nombre,
            email=self.email.email,
            telefono=self.telefono.telefono,
            direccion=self.direccion.direccion
        )
        return evento

@dataclass
class Cliente(AgregacionRaiz):
    nombre: Nombre = field(default_factory=lambda: Nombre(""))
    email: Email = field(default_factory=lambda: Email(""))
    identificacion: Identificacion = field(default_factory=lambda: Identificacion(""))
    telefono: Telefono = field(default_factory=lambda: Telefono(""))
    direccion: Direccion = field(default_factory=lambda: Direccion(""))
    
    def disparar_evento_creacion(self):
        evento = ClienteCreado(
            cliente_id=self.id,
            nombre=self.nombre.nombre,
            email=self.email.email,
            telefono=self.telefono.telefono,
            direccion=self.direccion.direccion
        )
        return evento

@dataclass
class Administrador(AgregacionRaiz):
    nombre: Nombre = field(default_factory=lambda: Nombre(""))
    email: Email = field(default_factory=lambda: Email(""))
    
    def disparar_evento_creacion(self):
        evento = AdministradorCreado(
            administrador_id=self.id,
            nombre=self.nombre.nombre,
            email=self.email.email
        )
        return evento

@dataclass
class Repartidor(AgregacionRaiz):
    nombre: Nombre = field(default_factory=lambda: Nombre(""))
    email: Email = field(default_factory=lambda: Email(""))
    identificacion: Identificacion = field(default_factory=lambda: Identificacion(""))
    telefono: Telefono = field(default_factory=lambda: Telefono(""))
    
    def disparar_evento_creacion(self):
        evento = RepartidorCreado(
            repartidor_id=self.id,
            nombre=self.nombre.nombre,
            email=self.email.email,
            identificacion=self.identificacion.identificacion,
            telefono=self.telefono.telefono
        )
        return evento
