from dataclasses import dataclass
from datetime import date
from typing import Optional
from seedwork.aplicacion.consultas import Consulta, ejecutar_consulta as consulta
from infraestructura.repositorios import RepositorioRutaSQLite
from aplicacion.dto import RutaDTO


@dataclass
class ObtenerRutas(Consulta):
    fecha: Optional[date] = None
    repartidor_id: Optional[str] = None


class ObtenerRutasHandler:
    def __init__(self):
        self._repositorio = RepositorioRutaSQLite()

    def handle(self, consulta: ObtenerRutas) -> list[RutaDTO]:
        return self._repositorio.obtener_por_fecha_y_repartidor(
            fecha=consulta.fecha,
            repartidor_id=consulta.repartidor_id
        )


@consulta.register(ObtenerRutas)
def ejecutar_obtener_rutas(consulta: ObtenerRutas):
    handler = ObtenerRutasHandler()
    return handler.handle(consulta)

