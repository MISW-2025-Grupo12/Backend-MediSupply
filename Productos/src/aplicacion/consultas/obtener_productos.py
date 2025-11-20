from dataclasses import dataclass
from seedwork.aplicacion.consultas import Consulta, ejecutar_consulta
import logging
import requests
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
    
    def _obtener_todos_proveedores(self) -> dict:
        """Obtener todos los proveedores y crear un diccionario indexado por ID"""
        try:
            base_url = self.servicio_proveedores.base_url
            proveedores_dict = {}
            page = 1
            page_size = 1000  # Tamaño grande para minimizar requests
            
            while True:
                response = requests.get(
                    f"{base_url}/proveedores", 
                    params={'page': page, 'page_size': page_size},
                    timeout=10
                )
                
                if response.status_code != 200:
                    logger.error(f"Error consultando proveedores: {response.status_code}")
                    break
                
                proveedores_data = response.json()
                
                # Manejar diferentes formatos de respuesta
                if isinstance(proveedores_data, dict) and 'items' in proveedores_data:
                    proveedores = proveedores_data['items']
                    pagination = proveedores_data.get('pagination', {})
                    has_next = pagination.get('has_next', False)
                elif isinstance(proveedores_data, list):
                    proveedores = proveedores_data
                    has_next = False
                else:
                    logger.error(f"Formato de respuesta inesperado: {type(proveedores_data)}")
                    break
                
                # Indexar proveedores por ID
                for proveedor in proveedores:
                    proveedor_id = proveedor.get('id')
                    if proveedor_id:
                        proveedores_dict[proveedor_id] = proveedor
                
                if not has_next:
                    break
                page += 1
            
            logger.info(f"✅ Cargados {len(proveedores_dict)} proveedores en batch")
            return proveedores_dict
            
        except Exception as e:
            logger.error(f"Error obteniendo todos los proveedores: {e}")
            return {}
    
    def handle(self, consulta: ObtenerProductos) -> list[ProductoAgregacionDTO]:
        try:
            # 1. Obtener todos los productos del repositorio
            productos = self.repositorio.obtener_todos()
            
            # 2. Cargar todas las categorías de una vez
            categorias = self.repositorio_categoria.obtener_todos()
            categorias_dict = {str(cat.id): cat for cat in categorias}
            logger.info(f"✅ Cargadas {len(categorias_dict)} categorías en batch")
            
            # 3. Cargar todos los proveedores de una vez
            proveedores_dict = self._obtener_todos_proveedores()
            
            # 4. Construir agregaciones completas usando diccionarios en memoria
            agregaciones = []
            productos_sin_categoria = 0
            productos_sin_proveedor = 0
            
            for producto in productos:
                try:
                    # Obtener categoría del diccionario (O(1))
                    categoria = categorias_dict.get(producto.categoria_id)
                    if not categoria:
                        productos_sin_categoria += 1
                        logger.warning(f"Categoría {producto.categoria_id} no encontrada para producto {producto.id}")
                        continue
                    
                    # Obtener proveedor del diccionario (O(1))
                    proveedor = proveedores_dict.get(producto.proveedor_id)
                    if not proveedor:
                        productos_sin_proveedor += 1
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
            
            if productos_sin_categoria > 0:
                logger.warning(f"⚠️ {productos_sin_categoria} productos sin categoría")
            if productos_sin_proveedor > 0:
                logger.warning(f"⚠️ {productos_sin_proveedor} productos sin proveedor")
            
            logger.info(f"✅ Construidas {len(agregaciones)} agregaciones de {len(productos)} productos")
            return agregaciones
            
        except Exception as e:
            logger.error(f"Error obteniendo productos con agregación: {e}")
            raise

@ejecutar_consulta.register
def _(consulta: ObtenerProductos):
    handler = ObtenerProductosHandler()
    return handler.handle(consulta)
