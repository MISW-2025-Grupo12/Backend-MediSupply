from dataclasses import dataclass
from seedwork.aplicacion.consultas import Consulta, ejecutar_consulta
import logging
from aplicacion.dto import RepartidorDTO
from infraestructura.repositorios import RepositorioRepartidorSQLite

logger = logging.getLogger(__name__)

@dataclass
class ObtenerRepartidores(Consulta):
    """Consulta para obtener todos los repartidores"""
    pass

class ObtenerRepartidoresHandler:
    def __init__(self, repositorio=None):
        self.repositorio = repositorio or RepositorioRepartidorSQLite()
    
    def handle(self, consulta: ObtenerRepartidores) -> list[RepartidorDTO]:
        try:
            repartidores = self.repositorio.obtener_todos()
            return repartidores
            
        except Exception as e:
            logger.error(f"Error obteniendo repartidores: {e}")
            raise

@ejecutar_consulta.register
def _(consulta: ObtenerRepartidores):
    handler = ObtenerRepartidoresHandler()
    return handler.handle(consulta)

