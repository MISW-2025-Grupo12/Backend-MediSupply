from dataclasses import dataclass
from seedwork.aplicacion.consultas import Consulta, ejecutar_consulta
import logging
from aplicacion.dto import ProductoDTO
from aplicacion.dto_agregacion import ProductoAgregacionDTO
from infraestructura.repositorios import RepositorioProductoSQLite, RepositorioCategoriaSQLite
from infraestructura.servicio_proveedores import ServicioProveedores

logger = logging.getLogger(__name__)

@dataclass
class ObtenerProductos(Consulta):
    """Consulta para obtener todos los productos con agregación completa"""
    pass

class ObtenerProductosHandler:
    def __init__(self, repositorio=None, repositorio_categoria=None, servicio_proveedores=None):
        self.repositorio = repositorio or RepositorioProductoSQLite()
        self.repositorio_categoria = repositorio_categoria or RepositorioCategoriaSQLite()
        self.servicio_proveedores = servicio_proveedores or ServicioProveedores()
    
    def handle(self, consulta: ObtenerProductos) -> list[ProductoAgregacionDTO]:
        try:
            # 1. Obtener todos los productos del repositorio
            productos = self.repositorio.obtener_todos()
            
            # 2. Construir agregaciones completas reutilizando consultas optimizadas
            agregaciones = []
            for producto in productos:
                try:
                    # Obtener categoría (consulta optimizada por ID)
                    categoria = self.repositorio_categoria.obtener_por_id(producto.categoria_id)
                    if not categoria:
                        logger.warning(f"Categoría {producto.categoria_id} no encontrada para producto {producto.id}")
                        continue
                    
                    # Obtener proveedor (consulta optimizada por ID)
                    proveedor = self.servicio_proveedores.obtener_proveedor_por_id(producto.proveedor_id)
                    if not proveedor:
                        logger.warning(f"Proveedor {producto.proveedor_id} no encontrado para producto {producto.id}")
                        continue
                    
                    # Construir agregación completa
                    agregacion = ProductoAgregacionDTO(
                        id=producto.id,
                        nombre=producto.nombre,
                        descripcion=producto.descripcion,
                        precio=producto.precio,
                        categoria_id=categoria.id,
                        categoria_nombre=categoria.nombre,
                        categoria_descripcion=categoria.descripcion,
                        proveedor_id=proveedor['id'],
                        proveedor_nombre=proveedor['nombre'],
                        proveedor_email=proveedor['email'],
                        proveedor_direccion=proveedor['direccion']
                    )
                    
                    agregaciones.append(agregacion)
                    
                except Exception as e:
                    logger.warning(f"Error construyendo agregación para producto {producto.id}: {e}")
                    continue
            
            return agregaciones
            
        except Exception as e:
            logger.error(f"Error obteniendo productos con agregación: {e}")
            raise

@ejecutar_consulta.register
def _(consulta: ObtenerProductos):
    handler = ObtenerProductosHandler()
    return handler.handle(consulta)
