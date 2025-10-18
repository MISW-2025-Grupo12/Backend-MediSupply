from dataclasses import dataclass
from seedwork.aplicacion.consultas import Consulta, ejecutar_consulta
from infraestructura.repositorios import RepositorioBodegaSQLite

@dataclass
class ObtenerBodegas(Consulta):
    pass

class ObtenerBodegasHandler:
    def __init__(self, repositorio=None):
        self.repositorio = repositorio or RepositorioBodegaSQLite()
    
    def handle(self, consulta: ObtenerBodegas):
        bodegas = self.repositorio.obtener_todas()
        return [bodega.to_dict() for bodega in bodegas]

@ejecutar_consulta.register
def _(consulta: ObtenerBodegas):
    handler = ObtenerBodegasHandler()
    return handler.handle(consulta)
