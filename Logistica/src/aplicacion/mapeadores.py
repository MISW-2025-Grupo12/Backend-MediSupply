from aplicacion.dto import EntregaDTO, RutaDTO, RutaEntregaDTO
from dominio.entidades import Entrega, Ruta
from dominio.objetos_valor import (
    Direccion,
    FechaEntrega,
    FechaRuta,
    RepartidorID,
    EstadoRuta,
    EntregaAsignada,
)
from datetime import datetime
from typing import Optional, List
import logging

from infraestructura.servicio_usuarios import ServicioUsuarios
from infraestructura.servicio_productos import ServicioProductos

logger = logging.getLogger(__name__)


class MapeadorEntregaDTOJson:
    def externo_a_dto(self, externo: dict) -> EntregaDTO:
        """Convierte JSON externo a EntregaDTO"""
        return EntregaDTO(
            direccion=externo.get('direccion', ''),
            fecha_entrega=datetime.fromisoformat(
                externo.get('fecha_entrega', datetime.now().isoformat())
            ),
            pedido=externo.get('pedido', None),
            id=externo.get('id')
        )

    def dto_a_externo(self, dto: EntregaDTO) -> dict:
        """Convierte EntregaDTO a JSON externo"""
        pedido_normalizado = self._normalizar_pedido(dto.pedido)

        return {
            'id': str(dto.id),
            'direccion': dto.direccion,
            'fecha_entrega': dto.fecha_entrega.isoformat(),
            'pedido': pedido_normalizado
        }

    def _normalizar_pedido(self, pedido: Optional[dict]) -> Optional[dict]:
        """Normaliza la estructura del pedido para mantener compatibilidad con el frontend."""
        if not pedido or not isinstance(pedido, dict):
            return pedido

        # Si ya tiene la estructura legacy (con cliente y productos), retornar igual
        if 'cliente' in pedido and 'productos' in pedido:
            return pedido

        # Si viene en el nuevo formato (cliente_id + items), transformarlo
        if 'cliente_id' in pedido and 'items' in pedido:
            return self._construir_pedido_legacy(pedido)

        # Cualquier otro formato inesperado se retorna tal cual para evitar romper consumidores
        return pedido

    def _construir_pedido_legacy(self, pedido: dict) -> dict:
        """Construye la estructura legacy de pedido enriqueciendo datos de cliente y productos."""
        cliente_id = pedido.get('cliente_id')
        items = pedido.get('items', [])

        cliente = self._obtener_cliente(cliente_id)
        productos = self._construir_productos(items)

        pedido_legacy = {
            'id': pedido.get('id'),
            'total': pedido.get('total', 0),
            'estado': pedido.get('estado', 'confirmado'),
            'fecha_confirmacion': pedido.get('fecha_confirmacion'),
            'vendedor_id': pedido.get('vendedor_id'),
            'cliente': cliente,
            'productos': productos
        }

        return pedido_legacy

    def _obtener_cliente(self, cliente_id: str) -> dict:
        """Obtiene información del cliente o retorna un fallback si no está disponible."""
        cliente_placeholder = {
            'id': cliente_id or '',
            'nombre': 'Cliente desconocido',
            'telefono': '',
            'direccion': '',
            'avatar': 'https://via.placeholder.com/64?text=C'
        }

        if not cliente_id:
            return cliente_placeholder

        try:
            servicio = self._obtener_servicio_usuarios()
            cliente = servicio.obtener_cliente_por_id(cliente_id)

            if not cliente:
                return cliente_placeholder

            return {
                'id': cliente_id,
                'nombre': cliente.get('nombre', cliente_placeholder['nombre']),
                'telefono': cliente.get('telefono', cliente_placeholder['telefono']),
                'direccion': cliente.get('direccion', cliente_placeholder['direccion']),
                'avatar': cliente.get('avatar', cliente_placeholder['avatar'])
                    or cliente_placeholder['avatar']
            }
        except Exception as ex:
            logger.warning(f"Error obteniendo cliente {cliente_id}: {ex}")
            return cliente_placeholder

    def _construir_productos(self, items: List[dict]) -> List[dict]:
        """Enriquece los items con información de productos para mantener compatibilidad."""
        productos = []
        servicio_productos = self._obtener_servicio_productos()

        for index, item in enumerate(items or []):
            producto_id = item.get('producto_id')
            cantidad = item.get('cantidad', 0)
            info_producto = None

            if producto_id and servicio_productos:
                try:
                    info_producto = servicio_productos.obtener_producto_por_id(producto_id)
                except Exception as ex:
                    logger.warning(f"Error obteniendo producto {producto_id}: {ex}")
                    info_producto = None

            nombre = (
                item.get('nombre') or
                (info_producto.get('nombre') if info_producto else None) or
                'Producto'
            )

            precio_unitario = item.get('precio_unitario')
            if precio_unitario is None and info_producto:
                precio_unitario = (
                    info_producto.get('precio_unitario') or
                    info_producto.get('precio') or
                    info_producto.get('precio_sugerido')
                )

            if precio_unitario is None:
                precio_unitario = 0

            subtotal = item.get('subtotal')
            if subtotal is None:
                subtotal = precio_unitario * cantidad

            avatar_text = f"P{index + 1}"
            avatar = item.get('avatar') or (info_producto.get('avatar') if info_producto else None)
            if not avatar:
                avatar = f'https://via.placeholder.com/64?text={avatar_text}'

            productos.append({
                'producto_id': producto_id,
                'nombre': nombre,
                'cantidad': cantidad,
                'precio_unitario': precio_unitario,
                'subtotal': subtotal,
                'avatar': avatar
            })

        return productos

    def _obtener_servicio_usuarios(self) -> Optional[ServicioUsuarios]:
        """Obtiene (con caché simple) la instancia del servicio de usuarios."""
        servicio = getattr(self, '_servicio_usuarios', None)
        if servicio is None:
            try:
                servicio = ServicioUsuarios()
            except Exception as ex:
                logger.warning(f"No fue posible inicializar ServicioUsuarios: {ex}")
                servicio = None
            self._servicio_usuarios = servicio
        return servicio

    def _obtener_servicio_productos(self) -> Optional[ServicioProductos]:
        """Obtiene (con caché simple) la instancia del servicio de productos."""
        servicio = getattr(self, '_servicio_productos', None)
        if servicio is None:
            try:
                servicio = ServicioProductos()
            except Exception as ex:
                logger.warning(f"No fue posible inicializar ServicioProductos: {ex}")
                servicio = None
            self._servicio_productos = servicio
        return servicio



class MapeadorEntrega:
    def entidad_a_dto(self, entidad: Entrega) -> EntregaDTO:
        """Convierte entidad Entrega a EntregaDTO"""
        return EntregaDTO(
            id=entidad.id,
            direccion=entidad.direccion.valor,
            fecha_entrega=entidad.fecha_entrega.valor,
            pedido=None
        )

    def dto_a_entidad(self, dto: EntregaDTO) -> Entrega:
        """Convierte EntregaDTO a entidad Entrega"""
        return Entrega(
            id=dto.id,
            direccion=Direccion(dto.direccion),
            fecha_entrega=FechaEntrega(dto.fecha_entrega)
        )


class MapeadorRuta:
    def dto_a_entidad(self, dto: RutaDTO) -> Ruta:
        entregas = [
            EntregaAsignada(entrega_id=e.entrega_id, fecha_entrega=e.fecha_entrega)
            for e in dto.entregas
        ]

        return Ruta(
            id=dto.id,
            fecha_ruta=FechaRuta(dto.fecha_ruta),
            repartidor_id=RepartidorID(dto.repartidor_id),
            estado=EstadoRuta(dto.estado),
            entregas=entregas
        )

    def entidad_a_dto(self, ruta: Ruta, entregas_detalle: Optional[List[RutaEntregaDTO]] = None) -> RutaDTO:
        entregas = entregas_detalle or [
            RutaEntregaDTO(
                entrega_id=e.entrega_id,
                direccion="",
                fecha_entrega=e.fecha_entrega,
                pedido=None
            )
            for e in ruta.entregas
        ]

        return RutaDTO(
            id=str(ruta.id),
            fecha_ruta=ruta.fecha_ruta.valor,
            repartidor_id=ruta.repartidor_id.valor,
            estado=ruta.estado.valor,
            entregas=entregas
        )


class MapeadorRutaDTOJson:
    def dto_a_externo(self, dto: RutaDTO) -> dict:
        return {
            'id': str(dto.id),
            'fecha_ruta': dto.fecha_ruta.isoformat(),
            'repartidor_id': dto.repartidor_id,
            'bodega_id': dto.bodega_id,
            'estado': dto.estado,
            'entregas': [
                {
                    'id': entrega.entrega_id,
                    'direccion': entrega.direccion,
                    'fecha_entrega': entrega.fecha_entrega.isoformat(),
                    'pedido': entrega.pedido
                }
                for entrega in dto.entregas
            ]
        }

    def externo_a_dto(self, data: dict) -> RutaDTO:
        entregas = [
            RutaEntregaDTO(
                entrega_id=entrega.get('entrega_id'),
                direccion=entrega.get('direccion', ''),
                fecha_entrega=datetime.fromisoformat(entrega['fecha_entrega']),
                pedido=entrega.get('pedido')
            )
            for entrega in data.get('entregas', [])
        ]

        return RutaDTO(
            fecha_ruta=datetime.fromisoformat(data['fecha_ruta']).date(),
            repartidor_id=data['repartidor_id'],
            entregas=entregas
        )
