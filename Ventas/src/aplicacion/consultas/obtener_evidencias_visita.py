from dataclasses import dataclass
from seedwork.aplicacion.consultas import Consulta, ejecutar_consulta
from infraestructura.repositorios import RepositorioEvidenciaVisita
import logging

logger = logging.getLogger(__name__)

@dataclass
class ObtenerEvidenciasVisita(Consulta):
    visita_id: str

class ObtenerEvidenciasVisitaHandler:
    def __init__(self, repositorio=None):
        self.repositorio = repositorio or RepositorioEvidenciaVisita()
    
    def handle(self, consulta: ObtenerEvidenciasVisita):
        logger.info(f"Obteniendo evidencias de visita: {consulta.visita_id}")
        evidencias = self.repositorio.obtener_por_visita(consulta.visita_id)
        return evidencias

@ejecutar_consulta.register
def _(consulta: ObtenerEvidenciasVisita):
    handler = ObtenerEvidenciasVisitaHandler()
    return handler.handle(consulta)

