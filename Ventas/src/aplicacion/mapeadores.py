from aplicacion.dto import VisitaDTO, PlanDTO
from aplicacion.dto_agregacion import VisitaAgregacionDTO
from dominio.entidades import Visita
from dominio.objetos_valor import EstadoVisita, FechaProgramada, Direccion, Telefono, Descripcion, FechaRealizada, HoraRealizada, Novedades, PedidoGenerado
from infraestructura.modelos import PlanVisitaModel

class MapeadorVisitaDTOJson:
    def dto_a_externo(self, dto: VisitaDTO) -> dict:
        return {
            'id': str(dto.id),
            'vendedor_id': dto.vendedor_id,
            'cliente_id': dto.cliente_id,
            'fecha_programada': dto.fecha_programada.isoformat(),
            'direccion': dto.direccion,
            'telefono': dto.telefono,
            'estado': dto.estado,
            'descripcion': dto.descripcion,
            'fecha_realizada': dto.fecha_realizada.isoformat() if dto.fecha_realizada else None,
            'hora_realizada': dto.hora_realizada.isoformat() if dto.hora_realizada else None,
            'novedades': dto.novedades,
            'pedido_generado': dto.pedido_generado
        }
    
    def externo_a_dto(self, externo: dict) -> VisitaDTO:
        from datetime import datetime, date, time
        return VisitaDTO(
            id=externo.get('id'),
            vendedor_id=externo.get('vendedor_id', ''),
            cliente_id=externo.get('cliente_id', ''),
            fecha_programada=datetime.fromisoformat(externo.get('fecha_programada', datetime.now().isoformat())),
            direccion=externo.get('direccion', ''),
            telefono=externo.get('telefono', ''),
            estado=externo.get('estado', 'pendiente'),
            descripcion=externo.get('descripcion', ''),
            fecha_realizada=date.fromisoformat(externo.get('fecha_realizada')) if externo.get('fecha_realizada') else None,
            hora_realizada=time.fromisoformat(externo.get('hora_realizada')) if externo.get('hora_realizada') else None,
            novedades=externo.get('novedades'),
            pedido_generado=externo.get('pedido_generado')
        )

class MapeadorVisitaAgregacionDTOJson:
    def agregacion_a_externo(self, agregacion: VisitaAgregacionDTO) -> dict:
        return {
            'id': str(agregacion.id),
            'fecha_programada': agregacion.fecha_programada.isoformat() if agregacion.fecha_programada else None,
            'direccion': agregacion.direccion,
            'telefono': agregacion.telefono,
            'estado': agregacion.estado,
            'descripcion': agregacion.descripcion,
            'vendedor': {
                'id': agregacion.vendedor_id,
                'nombre': agregacion.vendedor_nombre,
                'email': agregacion.vendedor_email,
                'telefono': agregacion.vendedor_telefono,
                'direccion': agregacion.vendedor_direccion
            },
            'cliente': {
                'id': agregacion.cliente_id,
                'nombre': agregacion.cliente_nombre,
                'email': agregacion.cliente_email,
                'telefono': agregacion.cliente_telefono,
                'direccion': agregacion.cliente_direccion
            }
        }
    
    def agregaciones_a_externo(self, agregaciones: list[VisitaAgregacionDTO]) -> list[dict]:
        return [self.agregacion_a_externo(agregacion) for agregacion in agregaciones]

class MapeadorVisita:
    def entidad_a_dto(self, entidad: Visita) -> VisitaDTO:
        return VisitaDTO(
            id=entidad.id,
            vendedor_id=entidad.vendedor_id,
            cliente_id=entidad.cliente_id,
            fecha_programada=entidad.fecha_programada.fecha,
            direccion=entidad.direccion.direccion,
            telefono=entidad.telefono.telefono,
            estado=entidad.estado.estado,
            descripcion=entidad.descripcion.descripcion,
            fecha_realizada=entidad.fecha_realizada.fecha if entidad.fecha_realizada else None,
            hora_realizada=entidad.hora_realizada.hora if entidad.hora_realizada else None,
            novedades=entidad.novedades.novedades if entidad.novedades else None,
            pedido_generado=entidad.pedido_generado.pedido_generado if entidad.pedido_generado else None
        )
    

class MapeadorPlanDTOJson:
    def modelo_a_dto(self, modelo: PlanVisitaModel) -> PlanDTO:
        return PlanDTO(
            id=modelo.id,
            nombre=modelo.nombre,
            id_usuario=modelo.id_usuario,
            fecha_inicio=modelo.fecha_inicio,
            fecha_fin=modelo.fecha_fin
        )

    def dto_a_json(self, dto: PlanDTO) -> dict:
        return {
            "id": str(dto.id),
            "nombre": dto.nombre,
            "id_usuario": dto.id_usuario,
            "fecha_inicio": dto.fecha_inicio.isoformat() if dto.fecha_inicio else None,
            "fecha_fin": dto.fecha_fin.isoformat() if dto.fecha_fin else None
        }

    def modelos_a_json(self, modelos: list[PlanVisitaModel]) -> list[dict]:
        return [self.dto_a_json(self.modelo_a_dto(m)) for m in modelos]

