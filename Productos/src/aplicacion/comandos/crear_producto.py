
from dataclasses import dataclass
from seedwork.aplicacion.comandos import Comando, ejecutar_comando
import uuid
import logging
from datetime import datetime
from aplicacion.dto import ProductoDTO
from aplicacion.dto_agregacion import ProductoAgregacionDTO
from dominio.fabricas import FabricaProducto
from dominio.entidades import Producto
from dominio.objetos_valor import Nombre, Descripcion, Precio, Categoria, Proveedor
from dominio.reglas import (
    NombreProductoNoPuedeSerVacio, DescripcionProductoNoPuedeSerVacio, PrecioProductoNoPuedeSerVacio,
    PrecioProductoNoPuedeSerMenorACero, PrecioProductoDebeSerNumerico,
    CategoriaProductoNoPuedeSerVacia, CategoriaIdNoPuedeSerVacio, 
    CategoriaDebeExistir, ProveedorIdNoPuedeSerVacio, ProveedorDebeExistir
)
from infraestructura.repositorios import RepositorioProductoSQLite, RepositorioCategoriaSQLite
from infraestructura.servicio_proveedores import ServicioProveedores

logger = logging.getLogger(__name__)

@dataclass
class CrearProducto(Comando):
    nombre: str
    descripcion: str
    precio: float
    categoria: str
    categoria_id: str
    proveedor_id: str

class CrearProductoHandler:
    def __init__(self, repositorio=None, repositorio_categoria=None, servicio_proveedores=None):
        self.repositorio = repositorio or RepositorioProductoSQLite()
        self.repositorio_categoria = repositorio_categoria or RepositorioCategoriaSQLite()
        self.servicio_proveedores = servicio_proveedores or ServicioProveedores()
    
    def handle(self, comando: CrearProducto) -> ProductoAgregacionDTO:
        try:
            # 1. Obtener y validar categoría (reutilizar objeto obtenido)
            categoria = self.repositorio_categoria.obtener_por_id(comando.categoria_id)
            if not categoria:
                raise ValueError(f"Categoría {comando.categoria_id} no existe")
            
            # 2. Obtener y validar proveedor (reutilizar objeto obtenido)
            proveedor = self.servicio_proveedores.obtener_proveedor_por_id(comando.proveedor_id)
            if not proveedor:
                raise ValueError(f"Proveedor {comando.proveedor_id} no existe")
            
            # 3. Crear el DTO del producto
            producto_dto = ProductoDTO(
                nombre=comando.nombre,
                descripcion=comando.descripcion,
                precio=comando.precio,
                categoria=comando.categoria,
                categoria_id=comando.categoria_id,
                proveedor_id=comando.proveedor_id
            )
            
            # 4. Crear entidad de dominio usando la fábrica (con validaciones)
            producto_temp = Producto(
                nombre=Nombre(comando.nombre),
                descripcion=Descripcion(comando.descripcion),
                precio=Precio(comando.precio),
                categoria=Categoria(comando.categoria),
                categoria_id=comando.categoria_id,
                proveedor_id=comando.proveedor_id
            )
            
            # 5. Validar reglas de negocio básicas
            fabrica = FabricaProducto()
            
            # Validaciones básicas del producto
            fabrica.validar_regla(NombreProductoNoPuedeSerVacio(producto_temp.nombre))
            fabrica.validar_regla(DescripcionProductoNoPuedeSerVacio(producto_temp.descripcion))
            fabrica.validar_regla(PrecioProductoNoPuedeSerVacio(producto_temp.precio))
            fabrica.validar_regla(PrecioProductoNoPuedeSerMenorACero(producto_temp.precio))
            fabrica.validar_regla(PrecioProductoDebeSerNumerico(producto_temp.precio))
            fabrica.validar_regla(CategoriaProductoNoPuedeSerVacia(producto_temp.categoria))
            fabrica.validar_regla(CategoriaIdNoPuedeSerVacio(producto_temp.categoria_id))
            fabrica.validar_regla(ProveedorIdNoPuedeSerVacio(producto_temp.proveedor_id))
            
            # 6. Disparar evento de creación
            producto_temp.disparar_evento_creacion()
            
            # 7. Guardar en SQLite
            producto_guardado = self.repositorio.crear(producto_dto)
            
            # 8. Construir agregación completa reutilizando objetos ya obtenidos
            agregacion = ProductoAgregacionDTO(
                id=producto_guardado.id,
                nombre=producto_guardado.nombre,
                descripcion=producto_guardado.descripcion,
                precio=producto_guardado.precio,
                categoria_id=categoria.id,
                categoria_nombre=categoria.nombre,
                categoria_descripcion=categoria.descripcion,
                proveedor_id=proveedor['id'],
                proveedor_nombre=proveedor['nombre'],
                proveedor_email=proveedor['email'],
                proveedor_direccion=proveedor['direccion']
            )
            
            # 9. Retornar la agregación completa
            return agregacion
            
        except Exception as e:
            logger.error(f"Error creando producto: {e}")
            raise

@ejecutar_comando.register
def _(comando: CrearProducto):
    handler = CrearProductoHandler()
    return handler.handle(comando)