from dataclasses import dataclass
from seedwork.aplicacion.consultas import Consulta, ejecutar_consulta
import logging
from aplicacion.dto import VendedorDTO
from infraestructura.repositorios import RepositorioVendedorSQLite

logger = logging.getLogger(__name__)

@dataclass
class ObtenerVendedorPorId(Consulta):
    """Consulta para obtener un vendedor por ID"""
    vendedor_id: str

class ObtenerVendedorPorIdHandler:
    def __init__(self, repositorio=None):
        self.repositorio = repositorio or RepositorioVendedorSQLite()
    
    def handle(self, consulta: ObtenerVendedorPorId) -> VendedorDTO:
        try:
            vendedor = self.repositorio.obtener_por_id(consulta.vendedor_id)
            return vendedor
            
        except Exception as e:
            logger.error(f"Error obteniendo vendedor por ID: {e}")
            raise

@ejecutar_consulta.register
def _(consulta: ObtenerVendedorPorId):
    handler = ObtenerVendedorPorIdHandler()
    return handler.handle(consulta)
