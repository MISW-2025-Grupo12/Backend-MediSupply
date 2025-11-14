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
from dominio.eventos import ProductoCreado, InventarioAsignado
from infraestructura.repositorios import RepositorioProductoSQLite, RepositorioCategoriaSQLite
from infraestructura.servicio_proveedores import ServicioProveedores
from seedwork.dominio.eventos import despachador_eventos

logger = logging.getLogger(__name__)

@dataclass
class ActualizarProductoConInventario(Comando):
    producto_id: str
    nombre: str
    descripcion: str
    precio: float
    stock: int
    fecha_vencimiento: str
    categoria: str
    categoria_id: str
    proveedor_id: str

class ActualizarProductoConInventarioHandler:
    def __init__(self, repositorio=None, repositorio_categoria=None, servicio_proveedores=None):
        self.repositorio = repositorio or RepositorioProductoSQLite()
        self.repositorio_categoria = repositorio_categoria or RepositorioCategoriaSQLite()
        self.servicio_proveedores = servicio_proveedores or ServicioProveedores()
    
    def handle(self, comando: ActualizarProductoConInventario) -> ProductoAgregacionDTO:
        try:
            # 1. Verificar que el producto existe
            producto_existente = self.repositorio.obtener_por_id(comando.producto_id)
            if not producto_existente:
                raise ValueError(f"Producto {comando.producto_id} no existe")
            
            # 2. Obtener y validar categoría
            categoria = self.repositorio_categoria.obtener_por_id(comando.categoria_id)
            if not categoria:
                raise ValueError(f"Categoría {comando.categoria_id} no existe")
            
            # 3. Obtener y validar proveedor
            proveedor = self.servicio_proveedores.obtener_proveedor_por_id(comando.proveedor_id)
            if not proveedor:
                raise ValueError(f"Proveedor {comando.proveedor_id} no existe")
            
            # 4. Crear el DTO del producto actualizado
            producto_dto = ProductoDTO(
                id=uuid.UUID(comando.producto_id),
                nombre=comando.nombre,
                descripcion=comando.descripcion,
                precio=comando.precio,
                categoria=comando.categoria,
                categoria_id=comando.categoria_id,
                proveedor_id=comando.proveedor_id
            )
            
            # 5. Crear entidad de dominio para validaciones
            producto_temp = Producto(
                id=uuid.UUID(comando.producto_id),
                nombre=Nombre(comando.nombre),
                descripcion=Descripcion(comando.descripcion),
                precio=Precio(comando.precio),
                categoria=Categoria(comando.categoria),
                categoria_id=comando.categoria_id,
                proveedor_id=comando.proveedor_id
            )
            
            # 6. Validar reglas de negocio básicas
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
            
            # 7. Actualizar producto en BD
            producto_actualizado = self.repositorio.actualizar(producto_dto)
            
            # 8. Crear y disparar evento de inventario (para actualizar inventario en Logística)
            evento_inventario = InventarioAsignado(
                producto_id=producto_actualizado.id,
                stock=comando.stock,
                fecha_vencimiento=comando.fecha_vencimiento
            )
            
            # 9. Publicar evento de inventario
            logger.info(f"Publicando evento InventarioAsignado para producto {evento_inventario.producto_id} con stock {evento_inventario.stock}")
            despachador_eventos.publicar_evento(evento_inventario)
            
            # 10. Construir agregación completa
            agregacion = ProductoAgregacionDTO(
                id=producto_actualizado.id,
                nombre=producto_actualizado.nombre,
                descripcion=producto_actualizado.descripcion,
                precio=producto_actualizado.precio,
                categoria_id=categoria.id,
                categoria_nombre=categoria.nombre,
                categoria_descripcion=categoria.descripcion,
                proveedor_id=proveedor['id'],
                proveedor_nombre=proveedor['nombre'],
                proveedor_email=proveedor['email'],
                proveedor_direccion=proveedor['direccion']
            )
            
            # 11. Retornar la agregación completa
            return agregacion
            
        except Exception as e:
            logger.error(f"Error actualizando producto con inventario: {e}")
            raise

@ejecutar_comando.register
def _(comando: ActualizarProductoConInventario):
    handler = ActualizarProductoConInventarioHandler()
    return handler.handle(comando)

