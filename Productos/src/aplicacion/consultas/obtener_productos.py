from dataclasses import dataclass
from seedwork.aplicacion.consultas import Consulta, ejecutar_consulta
import logging
from aplicacion.dto import ProductoDTO
from infraestructura.repositorios import RepositorioProductoSQLite

logger = logging.getLogger(__name__)

@dataclass
class ObtenerProductos(Consulta):
    """Consulta para obtener todos los productos"""
    pass

class ObtenerProductosHandler:
    def __init__(self):
        self.repositorio = RepositorioProductoSQLite()
    
    def handle(self, consulta: ObtenerProductos) -> list[ProductoDTO]:
        try:
            # Obtener todos los productos del repositorio
            productos = self.repositorio.obtener_todos()
            return productos
            
        except Exception as e:
            logger.error(f"Error obteniendo productos: {e}")
            raise

@ejecutar_consulta.register
def _(consulta: ObtenerProductos):
    handler = ObtenerProductosHandler()
    return handler.handle(consulta)
