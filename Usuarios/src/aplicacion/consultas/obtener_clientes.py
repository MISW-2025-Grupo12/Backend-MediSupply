from dataclasses import dataclass
from seedwork.aplicacion.consultas import Consulta, ejecutar_consulta
import logging
from aplicacion.dto import ClienteDTO
from infraestructura.repositorios import RepositorioClienteSQLite
from typing import Optional

logger = logging.getLogger(__name__)

@dataclass
class ObtenerClientes(Consulta):
    """Consulta para obtener todos los clientes, con soporte de ordenamiento"""
    sort_by: Optional[str] = None  # nombre, email, identificacion, created_at
    order: Optional[str] = None    # asc, desc

class ObtenerClientesHandler:
    def __init__(self, repositorio=None):
        self.repositorio = repositorio or RepositorioClienteSQLite()
    
    def handle(self, consulta: ObtenerClientes) -> list[ClienteDTO]:
        try:
            clientes = self.repositorio.obtener_todos(
                sort_by=consulta.sort_by,
                order=consulta.order
            )
            return clientes
            
        except Exception as e:
            logger.error(f"Error obteniendo clientes: {e}")
            raise

@ejecutar_consulta.register
def _(consulta: ObtenerClientes):
    handler = ObtenerClientesHandler()
    return handler.handle(consulta)
