from seedwork.dominio.reglas import ReglaNegocio
from .objetos_valor import Nombre, Email, Direccion

class NombreProveedorNoPuedeSerVacio(ReglaNegocio):
    def __init__(self, nombre, mensaje='El nombre del proveedor no puede ser vacío'):
        super().__init__(mensaje)
        self.nombre = nombre
    
    def es_valido(self) -> bool:
        return self.nombre is not None and self.nombre.nombre.strip() != ''

class EmailProveedorNoPuedeSerVacio(ReglaNegocio):
    def __init__(self, email, mensaje='El email del proveedor no puede ser vacío'):
        super().__init__(mensaje)
        self.email = email
    
    def es_valido(self) -> bool:
        return self.email is not None and self.email.email.strip() != ''

class DireccionProveedorNoPuedeSerVacia(ReglaNegocio):
    def __init__(self, direccion, mensaje='La dirección del proveedor no puede ser vacía'):
        super().__init__(mensaje)
        self.direccion = direccion
    
    def es_valido(self) -> bool:
        return self.direccion is not None and self.direccion.direccion.strip() != ''
