from dataclasses import dataclass
from seedwork.dominio.fabricas import Fabrica
from seedwork.dominio.entidades import Entidad
from seedwork.dominio.repositorios import Mapeador
from .entidades import Producto
from .reglas import (
    NombreProductoNoPuedeSerVacio, DescripcionProductoNoPuedeSerVacio, PrecioProductoNoPuedeSerVacio,
    PrecioProductoNoPuedeSerMenorACero, PrecioProductoDebeSerNumerico,     StockProductoDebeSerPositivo, FechaVencimientoDebeSerFutura,
    CategoriaProductoNoPuedeSerVacia, ProveedorProductoNoPuedeSerVacio, CategoriaIdNoPuedeSerVacio
)

@dataclass
class FabricaProducto(Fabrica):
    def crear_objeto(self, obj: any, mapeador: Mapeador) -> any:
        if isinstance(obj, Entidad):
            return mapeador.entidad_a_dto(obj)
        else:
            print( "Fabricando producto: ", obj)
            
            producto: Producto = mapeador.dto_a_entidad(obj)
            
            # Validar todas las reglas de negocio en la fábrica
            self.validar_regla(NombreProductoNoPuedeSerVacio(producto.nombre))
            self.validar_regla(DescripcionProductoNoPuedeSerVacio(producto.descripcion))
            self.validar_regla(PrecioProductoNoPuedeSerVacio(producto.precio))
            self.validar_regla(PrecioProductoNoPuedeSerMenorACero(producto.precio))
            self.validar_regla(PrecioProductoDebeSerNumerico(producto.precio))
            self.validar_regla(StockProductoDebeSerPositivo(producto.stock))
            self.validar_regla(FechaVencimientoDebeSerFutura(producto.fecha_vencimiento))
            self.validar_regla(CategoriaProductoNoPuedeSerVacia(producto.categoria))
            self.validar_regla(ProveedorProductoNoPuedeSerVacio(producto.proveedor))
            self.validar_regla(CategoriaIdNoPuedeSerVacio(producto.categoria_id))
                        
            return producto


    