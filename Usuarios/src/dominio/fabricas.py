from dataclasses import dataclass
from seedwork.dominio.fabricas import Fabrica
from .reglas import (
    NombreProveedorNoPuedeSerVacio,
    EmailProveedorNoPuedeSerVacio,
    DireccionProveedorNoPuedeSerVacia
)

@dataclass
class FabricaProveedor(Fabrica):
    def crear_objeto(self, obj: any, mapeador=None) -> any:
        proveedor = obj
        self.validar_regla(NombreProveedorNoPuedeSerVacio(proveedor.nombre))
        self.validar_regla(EmailProveedorNoPuedeSerVacio(proveedor.email))
        self.validar_regla(DireccionProveedorNoPuedeSerVacia(proveedor.direccion))
        return proveedor
