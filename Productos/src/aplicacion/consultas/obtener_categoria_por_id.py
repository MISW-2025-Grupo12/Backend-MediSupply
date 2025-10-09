from dataclasses import dataclass
from seedwork.aplicacion.consultas import Consulta, ejecutar_consulta
from aplicacion.dto import CategoriaDTO
from infraestructura.repositorios import RepositorioCategoriaSQLite
import logging

logger = logging.getLogger(__name__)

@dataclass
class ObtenerCategoriaPorId(Consulta):
    categoria_id: str

class ObtenerCategoriaPorIdHandler:
    def __init__(self):
        self.repositorio = RepositorioCategoriaSQLite()
    
    def handle(self, consulta: ObtenerCategoriaPorId) -> CategoriaDTO:
        try:
            categoria = self.repositorio.obtener_por_id(consulta.categoria_id)
            return categoria
        except Exception as e:
            logger.error(f"Error obteniendo categoría {consulta.categoria_id}: {e}")
            raise

@ejecutar_consulta.register
def _(consulta: ObtenerCategoriaPorId):
    handler = ObtenerCategoriaPorIdHandler()
    return handler.handle(consulta)
