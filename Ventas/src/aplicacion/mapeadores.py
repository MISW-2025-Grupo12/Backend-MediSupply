from aplicacion.dto import VisitaDTO
from aplicacion.dto_agregacion import VisitaAgregacionDTO
from dominio.entidades import Visita
from dominio.objetos_valor import EstadoVisita, FechaProgramada, Direccion, Telefono, Descripcion

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
            'descripcion': dto.descripcion
        }
    
    def externo_a_dto(self, externo: dict) -> VisitaDTO:
        from datetime import datetime
        return VisitaDTO(
            id=externo.get('id'),
            vendedor_id=externo.get('vendedor_id', ''),
            cliente_id=externo.get('cliente_id', ''),
            fecha_programada=datetime.fromisoformat(externo.get('fecha_programada', datetime.now().isoformat())),
            direccion=externo.get('direccion', ''),
            telefono=externo.get('telefono', ''),
            estado=externo.get('estado', 'pendiente'),
            descripcion=externo.get('descripcion', '')
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
            descripcion=entidad.descripcion.descripcion
        )
