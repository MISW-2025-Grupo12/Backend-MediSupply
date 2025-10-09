from dataclasses import dataclass
from seedwork.aplicacion.consultas import Consulta, ejecutar_consulta
from aplicacion.dto import ProveedorDTO
from infraestructura.repositorios import RepositorioProveedorSQLite
import logging

logger = logging.getLogger(__name__)

@dataclass
class ObtenerProveedores(Consulta):
    pass

class ObtenerProveedoresHandler:
    def __init__(self, repositorio=None):
        self.repositorio = repositorio or RepositorioProveedorSQLite()
    
    def handle(self, consulta: ObtenerProveedores) -> list[ProveedorDTO]:
        try:
            proveedores_dto = self.repositorio.obtener_todos()
            return proveedores_dto
        except Exception as e:
            logger.error(f"Error obteniendo proveedores: {e}")
            raise

@ejecutar_consulta.register
def _(consulta: ObtenerProveedores):
    handler = ObtenerProveedoresHandler()
    return handler.handle(consulta)
