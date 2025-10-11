from dataclasses import dataclass
from seedwork.aplicacion.consultas import Consulta, ejecutar_consulta
from infraestructura.repositorios import RepositorioProductoSQLite, RepositorioCategoriaSQLite
from infraestructura.servicio_proveedores import ServicioProveedores
import logging

logger = logging.getLogger(__name__)

@dataclass
class ObtenerProductoPorId(Consulta):
    producto_id: str

class ObtenerProductoPorIdHandler:
    def __init__(self, repositorio=None, repositorio_categoria=None, servicio_proveedores=None):
        self.repositorio = repositorio or RepositorioProductoSQLite()
        self.repositorio_categoria = repositorio_categoria or RepositorioCategoriaSQLite()
        self.servicio_proveedores = servicio_proveedores or ServicioProveedores()
    
    def handle(self, consulta: ObtenerProductoPorId) -> dict:
        """Obtener un producto específico por ID con agregación completa"""
        try:
            # 1. Obtener producto del repositorio
            producto = self.repositorio.obtener_por_id(consulta.producto_id)
            if not producto:
                return None
            
            # 2. Obtener categoría
            categoria = self.repositorio_categoria.obtener_por_id(producto.categoria_id)
            if not categoria:
                logger.warning(f"Categoría {producto.categoria_id} no encontrada para producto {producto.id}")
                return None
            
            # 3. Obtener proveedor
            proveedor = self.servicio_proveedores.obtener_proveedor_por_id(producto.proveedor_id)
            if not proveedor:
                logger.warning(f"Proveedor {producto.proveedor_id} no encontrado para producto {producto.id}")
                return None
            
            # 4. Construir respuesta completa
            return {
                'id': str(producto.id),
                'nombre': producto.nombre,
                'descripcion': producto.descripcion,
                'precio': producto.precio,
                'categoria': {
                    'id': str(categoria.id),
                    'nombre': categoria.nombre,
                    'descripcion': categoria.descripcion
                },
                'proveedor': {
                    'id': proveedor['id'],
                    'nombre': proveedor['nombre'],
                    'email': proveedor['email'],
                    'direccion': proveedor['direccion']
                }
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo producto por ID: {e}")
            return None

@ejecutar_consulta.register
def _(consulta: ObtenerProductoPorId):
    handler = ObtenerProductoPorIdHandler()
    return handler.handle(consulta)
