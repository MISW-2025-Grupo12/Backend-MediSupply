from dataclasses import dataclass
from seedwork.aplicacion.consultas import Consulta, ejecutar_consulta
import logging
from aplicacion.dto import ClienteDTO
from infraestructura.repositorios import RepositorioClienteSQLite

logger = logging.getLogger(__name__)

@dataclass
class ObtenerClientes(Consulta):
    """Consulta para obtener todos los clientes"""
    pass

class ObtenerClientesHandler:
    def __init__(self, repositorio=None):
        self.repositorio = repositorio or RepositorioClienteSQLite()
    
    def handle(self, consulta: ObtenerClientes) -> list[ClienteDTO]:
        try:
            clientes = self.repositorio.obtener_todos()
            return clientes
            
        except Exception as e:
            logger.error(f"Error obteniendo clientes: {e}")
            raise

@ejecutar_consulta.register
def _(consulta: ObtenerClientes):
    handler = ObtenerClientesHandler()
    return handler.handle(consulta)
