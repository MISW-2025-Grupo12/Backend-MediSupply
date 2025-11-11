from datetime import datetime
import logging

from seedwork.dominio.eventos import ManejadorEvento
from infraestructura.repositorios import RepositorioEntregaSQLite

logger = logging.getLogger(__name__)


class ManejadorPedidoEstadoActualizado(ManejadorEvento):
    def __init__(self):
        self._repositorio = RepositorioEntregaSQLite()

    def manejar(self, evento):
        try:
            fecha_evento = None
            if getattr(evento, 'fecha_actualizacion', None):
                if isinstance(evento.fecha_actualizacion, datetime):
                    fecha_evento = evento.fecha_actualizacion
                else:
                    try:
                        fecha_evento = datetime.fromisoformat(str(evento.fecha_actualizacion))
                    except ValueError:
                        fecha_evento = None

            actualizadas = 0

            if self._repositorio.actualizar_estado_pedido:
                actualizadas = self._repositorio.actualizar_estado_pedido(
                    pedido_id=str(evento.pedido_id),
                    nuevo_estado=str(evento.estado),
                    fecha_actualizacion=fecha_evento
                )

            if not actualizadas:
                logger.warning(
                    f"No se encontraron entregas asociadas al pedido {evento.pedido_id} para actualizar estado '{evento.estado}'"
                )
        except Exception as error:
            logger.error(f"Error actualizando estado de pedido {evento.pedido_id}: {error}")


from seedwork.dominio.eventos import despachador_eventos

manejador = ManejadorPedidoEstadoActualizado()
despachador_eventos.registrar_manejador('PedidoEstadoActualizado', manejador)

