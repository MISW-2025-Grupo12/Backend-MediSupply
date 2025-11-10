from dataclasses import dataclass
from seedwork.aplicacion.consultas import Consulta, ejecutar_consulta
import logging
from aplicacion.dto import EntregaDTO
from infraestructura.repositorios import RepositorioEntregaSQLite
from datetime import datetime

logger = logging.getLogger(__name__)

# --- Consulta CQRS ---
@dataclass
class ObtenerEntregas(Consulta):
    """Consulta para obtener entregas programadas"""
    fecha_inicio: datetime = None
    fecha_fin: datetime = None
    estado_pedido: str | None = None


# --- Handler ---
class ObtenerEntregasHandler:
    def __init__(self):
        self.repositorio = RepositorioEntregaSQLite()
    
    def handle(self, consulta: ObtenerEntregas) -> list[EntregaDTO]:
        try:
            # Si hay rango de fechas -> buscar filtrado
            if consulta.fecha_inicio and consulta.fecha_fin:
                logger.info(f"📅 Filtrando entregas entre {consulta.fecha_inicio} y {consulta.fecha_fin}")
                entregas = self.repositorio.obtener_por_rango(consulta.fecha_inicio, consulta.fecha_fin)
            else:
                logger.info("📦 Consultando todas las entregas")
                entregas = self.repositorio.obtener_todos()

            if consulta.estado_pedido:
                estado_objetivo = consulta.estado_pedido.lower()
                entregas = [
                    e for e in entregas
                    if isinstance(e.pedido, dict)
                    and (e.pedido.get('estado') or '').lower() == estado_objetivo
                ]

            return entregas

        except Exception as e:
            logger.error(f"❌ Error obteniendo entregas: {e}")
            raise


# --- Registro de la consulta ---
@ejecutar_consulta.register
def _(consulta: ObtenerEntregas):
    handler = ObtenerEntregasHandler()
    return handler.handle(consulta)
