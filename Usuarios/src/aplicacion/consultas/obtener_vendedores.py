from dataclasses import dataclass
from seedwork.aplicacion.consultas import Consulta, ejecutar_consulta
import logging
from aplicacion.dto import VendedorDTO
from infraestructura.repositorios import RepositorioVendedorSQLite

logger = logging.getLogger(__name__)

@dataclass
class ObtenerVendedores(Consulta):
    """Consulta para obtener todos los vendedores"""
    pass

class ObtenerVendedoresHandler:
    def __init__(self, repositorio=None):
        self.repositorio = repositorio or RepositorioVendedorSQLite()
    
    def handle(self, consulta: ObtenerVendedores) -> list[VendedorDTO]:
        try:
            vendedores = self.repositorio.obtener_todos()
            return vendedores
            
        except Exception as e:
            logger.error(f"Error obteniendo vendedores: {e}")
            raise

@ejecutar_consulta.register
def _(consulta: ObtenerVendedores):
    handler = ObtenerVendedoresHandler()
    return handler.handle(consulta)
