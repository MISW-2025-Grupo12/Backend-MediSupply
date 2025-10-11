from dataclasses import dataclass, field
from datetime import datetime
from seedwork.dominio.entidades import Entidad, AgregacionRaiz
from .objetos_valor import Nombre, Descripcion, Precio, Categoria, Proveedor
from .eventos import ProductoCreado

@dataclass
class CategoriaEntidad(Entidad):    
    nombre: Nombre = field(default_factory=lambda: Nombre(""))
    descripcion: Descripcion = field(default_factory=lambda: Descripcion(""))

@dataclass
class ProveedorEntidad(Entidad):    
    nombre: Nombre = field(default_factory=lambda: Nombre(""))
    contacto: Descripcion = field(default_factory=lambda: Descripcion(""))
    direccion: Descripcion = field(default_factory=lambda: Descripcion(""))



@dataclass
class Producto(AgregacionRaiz):
    nombre: Nombre = field(default_factory=lambda: Nombre(""))
    descripcion: Descripcion = field(default_factory=lambda: Descripcion(""))
    precio: Precio = field(default_factory=lambda: Precio(0.0))
    categoria: Categoria = field(default_factory=lambda: Categoria(""))
    categoria_id: str = field(default_factory=lambda: "")
    proveedor_id: str = field(default_factory=lambda: "")
    
    def __post_init__(self):
        super().__post_init__()
    
    def disparar_evento_creacion(self):
        """Dispara el evento de creación del producto"""
        evento = ProductoCreado(
            producto_id=self.id,
            nombre=self.nombre.nombre,
            descripcion=self.descripcion.descripcion,
            precio=self.precio.precio,
            categoria=self.categoria.nombre,
            categoria_id=self.categoria_id,
            proveedor_id=self.proveedor_id
        )
        return evento
    