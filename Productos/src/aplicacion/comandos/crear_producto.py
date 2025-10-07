
from dataclasses import dataclass
from seedwork.aplicacion.comandos import Comando, ejecutar_comando
import uuid
import logging
from datetime import datetime
from aplicacion.dto import ProductoDTO
from dominio.fabricas import FabricaProducto
from dominio.entidades import Producto
from dominio.objetos_valor import Nombre, Descripcion, Precio, Stock, FechaVencimiento, Categoria, Proveedor
from dominio.reglas import (
    NombreProductoNoPuedeSerVacio, DescripcionProductoNoPuedeSerVacio, PrecioProductoNoPuedeSerVacio,
    PrecioProductoNoPuedeSerMenorACero, PrecioProductoDebeSerNumerico, StockProductoDebeSerPositivo,
    FechaVencimientoDebeSerFutura, CategoriaProductoNoPuedeSerVacia, ProveedorProductoNoPuedeSerVacio,
    CategoriaIdNoPuedeSerVacio
)
from infraestructura.repositorios import RepositorioProductoSQLite

logger = logging.getLogger(__name__)

@dataclass
class CrearProducto(Comando):
    nombre: str
    descripcion: str
    precio: float
    stock: int
    fecha_vencimiento: datetime
    categoria: str
    proveedor: str
    categoria_id: str

class CrearProductoHandler:
    def __init__(self):
        self.repositorio = RepositorioProductoSQLite()
    
    def handle(self, comando: CrearProducto) -> ProductoDTO:
        try:
            # 1. Crear el DTO del producto
            producto_dto = ProductoDTO(
                nombre=comando.nombre,
                descripcion=comando.descripcion,
                precio=comando.precio,
                stock=comando.stock,
                fecha_vencimiento=comando.fecha_vencimiento,
                categoria=comando.categoria,
                proveedor=comando.proveedor,
                categoria_id=comando.categoria_id
            )
            
            # 2. Crear entidad de dominio usando la fábrica (con validaciones)
            producto_temp = Producto(
                nombre=Nombre(comando.nombre),
                descripcion=Descripcion(comando.descripcion),
                precio=Precio(comando.precio),
                stock=Stock(comando.stock),
                fecha_vencimiento=FechaVencimiento(comando.fecha_vencimiento),
                categoria=Categoria(comando.categoria),
                proveedor=Proveedor(comando.proveedor, "", ""),
                categoria_id=comando.categoria_id
            )
            
            # 3. Usar la fábrica para validar y crear el producto final
            fabrica = FabricaProducto()
            # La fábrica solo valida las reglas de negocio, no necesita mapeador
            fabrica.validar_regla(NombreProductoNoPuedeSerVacio(producto_temp.nombre))
            fabrica.validar_regla(DescripcionProductoNoPuedeSerVacio(producto_temp.descripcion))
            fabrica.validar_regla(PrecioProductoNoPuedeSerVacio(producto_temp.precio))
            fabrica.validar_regla(PrecioProductoNoPuedeSerMenorACero(producto_temp.precio))
            fabrica.validar_regla(PrecioProductoDebeSerNumerico(producto_temp.precio))
            fabrica.validar_regla(StockProductoDebeSerPositivo(producto_temp.stock))
            fabrica.validar_regla(FechaVencimientoDebeSerFutura(producto_temp.fecha_vencimiento))
            fabrica.validar_regla(CategoriaProductoNoPuedeSerVacia(producto_temp.categoria))
            fabrica.validar_regla(ProveedorProductoNoPuedeSerVacio(producto_temp.proveedor))
            fabrica.validar_regla(CategoriaIdNoPuedeSerVacio(producto_temp.categoria_id))
            
            # 4. Disparar evento de creación
            producto_temp.disparar_evento_creacion()
            
            # 5. Guardar en SQLite
            producto_guardado = self.repositorio.crear(producto_dto)
            
            # 6. Retornar el DTO del producto creado
            return producto_guardado
            
        except Exception as e:
            logger.error(f"Error creando producto: {e}")
            raise

@ejecutar_comando.register
def _(comando: CrearProducto):
    handler = CrearProductoHandler()
    return handler.handle(comando)