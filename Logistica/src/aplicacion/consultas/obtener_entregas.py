from dataclasses import dataclass
from seedwork.aplicacion.consultas import Consulta, ejecutar_consulta
import logging
from aplicacion.dto import EntregaDTO
from infraestructura.repositorios import RepositorioEntregaSQLite

logger = logging.getLogger(__name__)

# Consulta CQRS
@dataclass
class ObtenerEntregas(Consulta):
    """Consulta para obtener todas las entregas programadas"""
    pass


# Handler (controlador de la consulta)
class ObtenerEntregasHandler:
    def __init__(self):
        self.repositorio = RepositorioEntregaSQLite()
    
    def handle(self, consulta: ObtenerEntregas) -> list[EntregaDTO]:
        try:
            entregas = self.repositorio.obtener_todos()
            return entregas
        except Exception as e:
            logger.error(f"Error obteniendo entregas: {e}")
            raise


# Registro de la consulta
@ejecutar_consulta.register
def _(consulta: ObtenerEntregas):
    handler = ObtenerEntregasHandler()
    return handler.handle(consulta)
