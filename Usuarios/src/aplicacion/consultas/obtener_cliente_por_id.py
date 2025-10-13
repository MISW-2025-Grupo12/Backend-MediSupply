from dataclasses import dataclass
from seedwork.aplicacion.consultas import Consulta, ejecutar_consulta
import logging
from aplicacion.dto import ClienteDTO
from infraestructura.repositorios import RepositorioClienteSQLite

logger = logging.getLogger(__name__)

@dataclass
class ObtenerClientePorId(Consulta):
    """Consulta para obtener un cliente por ID"""
    cliente_id: str

class ObtenerClientePorIdHandler:
    def __init__(self, repositorio=None):
        self.repositorio = repositorio or RepositorioClienteSQLite()
    
    def handle(self, consulta: ObtenerClientePorId) -> ClienteDTO:
        try:
            cliente = self.repositorio.obtener_por_id(consulta.cliente_id)
            return cliente
            
        except Exception as e:
            logger.error(f"Error obteniendo cliente por ID: {e}")
            raise

@ejecutar_consulta.register
def _(consulta: ObtenerClientePorId):
    handler = ObtenerClientePorIdHandler()
    return handler.handle(consulta)
