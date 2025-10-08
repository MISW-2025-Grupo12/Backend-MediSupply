from dataclasses import dataclass
from seedwork.aplicacion.consultas import Consulta, ejecutar_consulta
from aplicacion.dto import ProveedorDTO
from infraestructura.repositorios import RepositorioProveedorSQLite
import logging

logger = logging.getLogger(__name__)

@dataclass
class ObtenerProveedorPorId(Consulta):
    proveedor_id: str

class ObtenerProveedorPorIdHandler:
    def __init__(self):
        self.repositorio = RepositorioProveedorSQLite()
    
    def handle(self, consulta: ObtenerProveedorPorId) -> ProveedorDTO:
        try:
            proveedor = self.repositorio.obtener_por_id(consulta.proveedor_id)
            return proveedor
        except Exception as e:
            logger.error(f"Error obteniendo proveedor {consulta.proveedor_id}: {e}")
            raise

@ejecutar_consulta.register
def _(consulta: ObtenerProveedorPorId):
    handler = ObtenerProveedorPorIdHandler()
    return handler.handle(consulta)
