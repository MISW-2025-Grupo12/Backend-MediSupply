from dataclasses import dataclass
from seedwork.aplicacion.consultas import Consulta
from seedwork.aplicacion.consultas import ejecutar_consulta as consulta
from infraestructura.repositorios import RepositorioPlanes
from datetime import datetime
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
            # El repositorio ya retorna diccionarios con la estructura completa
            # Solo necesitamos formatear las fechas a solo fecha (sin hora)
            data = []
            for plan in planes:
                # Convertir fechas ISO completas a solo fecha
                fecha_inicio = datetime.fromisoformat(plan["fecha_inicio"]).date().isoformat()
                fecha_fin = datetime.fromisoformat(plan["fecha_fin"]).date().isoformat()
                
                # Formatear fechas de visitas también
                visitas_clientes_formateadas = []
                for cliente_visita in plan.get("visitas_clientes", []):
                    visitas_fechas = [
                        datetime.fromisoformat(fecha).date().isoformat() 
                        if 'T' in fecha else fecha
                        for fecha in cliente_visita.get("visitas", [])
                    ]
                    visitas_clientes_formateadas.append({
                        "id_cliente": cliente_visita["id_cliente"],
                        "visitas": visitas_fechas
                    })
                
                data.append({
                    "id": plan["id"],
                    "nombre": plan["nombre"],
                    "id_usuario": plan["id_usuario"],
                    "fecha_inicio": fecha_inicio,
                    "fecha_fin": fecha_fin,
                    "visitas_clientes": visitas_clientes_formateadas
                })
            
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
            # El repositorio ya retorna diccionarios con la estructura completa
            # Solo necesitamos formatear las fechas a solo fecha (sin hora)
            data = []
            for plan in planes:
                # Convertir fechas ISO completas a solo fecha
                fecha_inicio = datetime.fromisoformat(plan["fecha_inicio"]).date().isoformat()
                fecha_fin = datetime.fromisoformat(plan["fecha_fin"]).date().isoformat()
                
                # Formatear fechas de visitas también
                visitas_clientes_formateadas = []
                for cliente_visita in plan.get("visitas_clientes", []):
                    visitas_fechas = [
                        datetime.fromisoformat(fecha).date().isoformat() 
                        if 'T' in fecha else fecha
                        for fecha in cliente_visita.get("visitas", [])
                    ]
                    visitas_clientes_formateadas.append({
                        "id_cliente": cliente_visita["id_cliente"],
                        "visitas": visitas_fechas
                    })
                
                data.append({
                    "id": plan["id"],
                    "nombre": plan["nombre"],
                    "id_usuario": plan["id_usuario"],
                    "fecha_inicio": fecha_inicio,
                    "fecha_fin": fecha_fin,
                    "visitas_clientes": visitas_clientes_formateadas
                })
            
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
