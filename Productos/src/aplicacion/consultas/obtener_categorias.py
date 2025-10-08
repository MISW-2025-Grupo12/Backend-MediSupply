from dataclasses import dataclass
from seedwork.aplicacion.consultas import Consulta, ejecutar_consulta
import logging
from aplicacion.dto import CategoriaDTO
from infraestructura.repositorios import RepositorioCategoriaSQLite

logger = logging.getLogger(__name__)

@dataclass
class ObtenerCategorias(Consulta):
    """Consulta para obtener todas las categorías"""
    pass

class ObtenerCategoriasHandler:
    def __init__(self):
        self.repositorio = RepositorioCategoriaSQLite()
    
    def handle(self, consulta: ObtenerCategorias) -> list[CategoriaDTO]:
        try:
            # Obtener todas las categorías del repositorio
            categorias = self.repositorio.obtener_todos()
            return categorias
            
        except Exception as e:
            logger.error(f"Error obteniendo categorías: {e}")
            raise

@ejecutar_consulta.register
def _(consulta: ObtenerCategorias):
    handler = ObtenerCategoriasHandler()
    return handler.handle(consulta)
