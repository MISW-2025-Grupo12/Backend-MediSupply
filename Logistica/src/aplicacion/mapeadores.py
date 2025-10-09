from aplicacion.dto import EntregaDTO
from dominio.entidades import Entrega
from dominio.objetos_valor import Direccion, FechaEntrega, ProductoID, ClienteID
from datetime import datetime

class MapeadorEntregaDTOJson:
    def externo_a_dto(self, externo: dict) -> EntregaDTO:
        """Convierte JSON externo a EntregaDTO"""
        return EntregaDTO(
            direccion=externo.get('direccion', ''),
            fecha_entrega=datetime.fromisoformat(externo.get('fecha_entrega', datetime.now().isoformat())),
            producto_id=externo.get('producto_id', ''),
            cliente_id=externo.get('cliente_id', ''),
            id=externo.get('id')
        )

    def dto_a_externo(self, dto: EntregaDTO) -> dict:
        """Convierte EntregaDTO a JSON externo"""
        return {
            'id': str(dto.id),
            'direccion': dto.direccion,
            'fecha_entrega': dto.fecha_entrega.isoformat(),
            'producto_id': dto.producto_id,
            'cliente_id': dto.cliente_id
        }

class MapeadorEntrega:
    def entidad_a_dto(self, entidad: Entrega) -> EntregaDTO:
        """Convierte entidad Entrega a EntregaDTO"""
        return EntregaDTO(
            id=entidad.id,
            direccion=entidad.direccion.valor,
            fecha_entrega=entidad.fecha_entrega.valor,
            producto_id=entidad.producto_id.valor,
            cliente_id=entidad.cliente_id.valor
        )

    def dto_a_entidad(self, dto: EntregaDTO) -> Entrega:
        """Convierte EntregaDTO a entidad Entrega"""
        return Entrega(
            id=dto.id,
            direccion=Direccion(dto.direccion),
            fecha_entrega=FechaEntrega(dto.fecha_entrega),
            producto_id=ProductoID(dto.producto_id),
            cliente_id=ClienteID(dto.cliente_id)
        )
