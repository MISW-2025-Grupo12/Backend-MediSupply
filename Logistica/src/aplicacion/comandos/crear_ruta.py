from dataclasses import dataclass
from datetime import date
from seedwork.aplicacion.comandos import Comando, ejecutar_comando as comando
from infraestructura.repositorios import RepositorioRutaSQLite, RepositorioEntregaSQLite, RepositorioBodegaSQLite
from aplicacion.dto import RutaDTO, RutaEntregaDTO
from dominio.entidades import Ruta
from dominio.objetos_valor import FechaRuta, RepartidorID, EstadoRuta, EntregaAsignada
from aplicacion.mapeadores import MapeadorRuta


@dataclass
class CrearRuta(Comando):
    fecha_ruta: date
    repartidor_id: str
    bodega_id: str
    entregas: list[str]


class CrearRutaHandler:
    def __init__(self):
        self._repo_rutas = RepositorioRutaSQLite()
        self._repo_entregas = RepositorioEntregaSQLite()
        self._repo_bodegas = RepositorioBodegaSQLite()
        self._mapeador_ruta = MapeadorRuta()

    def handle(self, comando: CrearRuta) -> RutaDTO:
        if not comando.entregas or not isinstance(comando.entregas, list):
            raise ValueError("Debe suministrar al menos una entrega para la ruta")

        bodega = self._repo_bodegas.obtener_por_id(comando.bodega_id)
        if not bodega:
            raise ValueError(f"La bodega {comando.bodega_id} no existe")

        fecha_ruta = FechaRuta(comando.fecha_ruta)
        repartidor_id = RepartidorID(comando.repartidor_id)

        entregas_asignadas: list[EntregaAsignada] = []
        entregas_detalle: list[RutaEntregaDTO] = []
        entregas_unicas = set(comando.entregas)

        for entrega_id in entregas_unicas:
            entregas_dto = self._repo_entregas.obtener_todos()
            entrega_dto = next((e for e in entregas_dto if str(e.id) == entrega_id), None)
            if not entrega_dto:
                raise ValueError(f"La entrega {entrega_id} no existe")

            if entrega_dto.fecha_entrega.date() != fecha_ruta.valor:
                raise ValueError(
                    f"La entrega {entrega_id} tiene fecha {entrega_dto.fecha_entrega.date()} "
                    f"que no coincide con la fecha de la ruta {fecha_ruta.valor}"
                )

            pedido = entrega_dto.pedido or {}
            estado_pedido = (pedido.get('estado') or '').lower()
            if estado_pedido != 'confirmado':
                raise ValueError(f"La entrega {entrega_id} no tiene un pedido confirmado")

            if self._repo_rutas.entrega_ya_asignada(entrega_id):
                raise ValueError(f"La entrega {entrega_id} ya está asignada a otra ruta")

            entregas_asignadas.append(
                EntregaAsignada(entrega_id=entrega_id, fecha_entrega=entrega_dto.fecha_entrega)
            )

            entregas_detalle.append(
                RutaEntregaDTO(
                    entrega_id=entrega_id,
                    direccion=entrega_dto.direccion,
                    fecha_entrega=entrega_dto.fecha_entrega,
                    pedido=pedido
                )
            )

        ruta_entidad = Ruta(
            fecha_ruta=fecha_ruta,
            repartidor_id=repartidor_id,
            estado=EstadoRuta("Pendiente"),
            entregas=entregas_asignadas
        )

        ruta_dto = self._mapeador_ruta.entidad_a_dto(ruta_entidad, entregas_detalle)
        ruta_dto_con_bodega = RutaDTO(
            id=ruta_dto.id,
            fecha_ruta=ruta_dto.fecha_ruta,
            repartidor_id=ruta_dto.repartidor_id,
            bodega_id=comando.bodega_id,
            estado=ruta_dto.estado,
            entregas=ruta_dto.entregas
        )
        return self._repo_rutas.crear(ruta_dto_con_bodega)


@comando.register(CrearRuta)
def ejecutar_crear_ruta(comando: CrearRuta):
    handler = CrearRutaHandler()
    return handler.handle(comando)

