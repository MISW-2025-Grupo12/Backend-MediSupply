from dataclasses import dataclass
from seedwork.aplicacion.consultas import Consulta
from seedwork.aplicacion.consultas import ejecutar_consulta as consulta
from infraestructura.repositorios import RepositorioPlanes
import logging

logger = logging.getLogger(__name__)


@dataclass
class ObtenerPlanes(Consulta):
    """Consulta para obtener todos los planes de visita"""
    pass


@dataclass
class ObtenerPlanesPorUsuario(Consulta):
    """Consulta para obtener los planes de un vendedor"""
    user_id: str


class ObtenerPlanesHandler:
    def __init__(self):
        self._repo = RepositorioPlanes()

    def handle(self, consulta: ObtenerPlanes) -> list[dict]:
        """Obtener todos los planes de visita"""
        try:
            planes = self._repo.obtener_todos()
            data = [
                {
                    "id": plan.id,
                    "nombre": plan.nombre,
                    "id_usuario": plan.id_usuario,
                    "fecha_inicio": plan.fecha_inicio.isoformat(),
                    "fecha_fin": plan.fecha_fin.isoformat()
                }
                for plan in planes
            ]
            logger.info(f"✅ Retornando {len(data)} planes")
            return data
        except Exception as e:
            logger.error(f"❌ Error obteniendo planes: {e}")
            return []


class ObtenerPlanesPorUsuarioHandler:
    def __init__(self):
        self._repo = RepositorioPlanes()

    def handle(self, consulta: ObtenerPlanesPorUsuario) -> list[dict]:
        """Obtener los planes de un vendedor específico"""
        try:
            planes = self._repo.obtener_por_usuario(consulta.user_id)
            data = [
                {
                    "id": plan.id,
                    "nombre": plan.nombre,
                    "id_usuario": plan.id_usuario,
                    "fecha_inicio": plan.fecha_inicio.isoformat(),
                    "fecha_fin": plan.fecha_fin.isoformat()
                }
                for plan in planes
            ]
            logger.info(f"✅ Retornando {len(data)} planes del usuario {consulta.user_id}")
            return data
        except Exception as e:
            logger.error(f"❌ Error obteniendo planes por usuario: {e}")
            return []


@consulta.register(ObtenerPlanes)
def ejecutar_obtener_planes(consulta: ObtenerPlanes):
    handler = ObtenerPlanesHandler()
    return handler.handle(consulta)


@consulta.register(ObtenerPlanesPorUsuario)
def ejecutar_obtener_planes_por_usuario(consulta: ObtenerPlanesPorUsuario):
    handler = ObtenerPlanesPorUsuarioHandler()
    return handler.handle(consulta)
