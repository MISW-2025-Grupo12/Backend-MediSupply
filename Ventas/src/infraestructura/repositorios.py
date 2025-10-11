from config.db import db
from infraestructura.modelos import VisitaModel, PedidoModel, ItemPedidoModel
from aplicacion.dto import VisitaDTO, PedidoDTO, ItemPedidoDTO
from dominio.entidades import Pedido, ItemPedido
from dominio.objetos_valor import EstadoPedido, Cantidad, Precio
import uuid

class RepositorioVisitaSQLite:
    def crear(self, visita_dto: VisitaDTO) -> VisitaDTO:
        """Crear una nueva visita en SQLite"""
        visita_model = VisitaModel(
            id=str(visita_dto.id),
            vendedor_id=visita_dto.vendedor_id,
            cliente_id=visita_dto.cliente_id,
            fecha_programada=visita_dto.fecha_programada,
            direccion=visita_dto.direccion,
            telefono=visita_dto.telefono,
            estado=visita_dto.estado,
            descripcion=visita_dto.descripcion
        )
        
        db.session.add(visita_model)
        db.session.commit()
        
        return visita_dto
    
    def obtener_por_id(self, visita_id: str) -> VisitaDTO:
        """Obtener una visita por ID"""
        visita_model = VisitaModel.query.get(visita_id)
        if not visita_model:
            return None
            
        return VisitaDTO(
            id=uuid.UUID(visita_model.id),
            vendedor_id=visita_model.vendedor_id,
            cliente_id=visita_model.cliente_id,
            fecha_programada=visita_model.fecha_programada,
            direccion=visita_model.direccion,
            telefono=visita_model.telefono,
            estado=visita_model.estado,
            descripcion=visita_model.descripcion,
            fecha_realizada=visita_model.fecha_realizada,
            hora_realizada=visita_model.hora_realizada,
            novedades=visita_model.novedades,
            pedido_generado=visita_model.pedido_generado
        )
    
    def obtener_todos(self) -> list[VisitaDTO]:
        """Obtener todas las visitas"""
        visitas_model = VisitaModel.query.all()
        visitas_dto = []
        
        for visita_model in visitas_model:
            visitas_dto.append(VisitaDTO(
                id=uuid.UUID(visita_model.id),
                vendedor_id=visita_model.vendedor_id,
                cliente_id=visita_model.cliente_id,
                fecha_programada=visita_model.fecha_programada,
                direccion=visita_model.direccion,
                telefono=visita_model.telefono,
                estado=visita_model.estado,
                descripcion=visita_model.descripcion,
                fecha_realizada=visita_model.fecha_realizada,
                hora_realizada=visita_model.hora_realizada,
                novedades=visita_model.novedades,
                pedido_generado=visita_model.pedido_generado
            ))
        
        return visitas_dto
    
    def actualizar(self, visita_dto: VisitaDTO) -> VisitaDTO:
        """Actualizar una visita existente"""
        visita_model = VisitaModel.query.get(str(visita_dto.id))
        if not visita_model:
            return None
        
        # Actualizar campos
        visita_model.vendedor_id = visita_dto.vendedor_id
        visita_model.cliente_id = visita_dto.cliente_id
        visita_model.fecha_programada = visita_dto.fecha_programada
        visita_model.direccion = visita_dto.direccion
        visita_model.telefono = visita_dto.telefono
        visita_model.estado = visita_dto.estado
        visita_model.descripcion = visita_dto.descripcion
        visita_model.fecha_realizada = visita_dto.fecha_realizada
        visita_model.hora_realizada = visita_dto.hora_realizada
        visita_model.novedades = visita_dto.novedades
        visita_model.pedido_generado = visita_dto.pedido_generado
        
        db.session.commit()
        
        return visita_dto

class RepositorioPedidoSQLite:
    def crear(self, pedido: Pedido) -> Pedido:
        """Crear un nuevo pedido en SQLite"""
        import logging
        logger = logging.getLogger(__name__)
        
        # Obtener el ID usando el método obtener_id()
        pedido_id = str(pedido.obtener_id())
        
        logger.info(f"Creando pedido con ID: {pedido_id}")
        
        pedido_model = PedidoModel(
            id=pedido_id,
            vendedor_id=pedido.vendedor_id,
            cliente_id=pedido.cliente_id,
            estado=pedido.estado.estado,
            total=pedido.total.valor
        )
        
        db.session.add(pedido_model)
        db.session.commit()
        logger.info(f"Pedido guardado exitosamente: {pedido_id}")
        
        # Crear items del pedido
        for item in pedido.items:
            # Obtener el ID del item usando el método obtener_id()
            item_id = str(item.obtener_id())
                
            item_model = ItemPedidoModel(
                id=item_id,
                pedido_id=pedido_id,
                producto_id=item.producto_id,
                nombre_producto=item.nombre_producto,
                cantidad=item.cantidad.valor,
                precio_unitario=item.precio_unitario.valor,
                subtotal=item.calcular_subtotal()
            )
            db.session.add(item_model)
        
        db.session.commit()
        return pedido
    
    def obtener_por_id(self, pedido_id: str) -> Pedido:
        """Obtener un pedido por ID con sus items"""
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Buscando pedido con ID: {pedido_id}")
        
        pedido_model = PedidoModel.query.get(pedido_id)
        if not pedido_model:
            logger.warning(f"Pedido no encontrado: {pedido_id}")
            # Listar todos los pedidos para debug
            todos = PedidoModel.query.all()
            logger.info(f"Pedidos en BD: {[p.id for p in todos]}")
            return None
        
        logger.info(f"Pedido encontrado: {pedido_id}")
        
        # Obtener items del pedido
        items_model = ItemPedidoModel.query.filter_by(pedido_id=pedido_id).all()
        
        # Crear entidades de dominio
        items = []
        for item_model in items_model:
            item = ItemPedido(
                id=uuid.UUID(item_model.id),
                producto_id=item_model.producto_id,
                nombre_producto=item_model.nombre_producto,
                cantidad=Cantidad(item_model.cantidad),
                precio_unitario=Precio(item_model.precio_unitario)
            )
            items.append(item)
        
        pedido = Pedido(
            id=uuid.UUID(pedido_model.id),
            vendedor_id=pedido_model.vendedor_id,
            cliente_id=pedido_model.cliente_id,
            items=items,
            estado=EstadoPedido(pedido_model.estado),
            total=Precio(pedido_model.total)
        )
        
        return pedido
    
    def obtener_todos(self) -> list[Pedido]:
        """Obtener todos los pedidos con sus items"""
        import logging
        logger = logging.getLogger(__name__)
        logger.info("Obteniendo todos los pedidos")
        
        pedidos_model = PedidoModel.query.all()
        pedidos = []
        
        for pedido_model in pedidos_model:
            # Obtener items del pedido
            items_model = ItemPedidoModel.query.filter_by(pedido_id=pedido_model.id).all()
            
            # Crear entidades de dominio para items
            items = []
            for item_model in items_model:
                item = ItemPedido(
                    id=uuid.UUID(item_model.id),
                    producto_id=item_model.producto_id,
                    nombre_producto=item_model.nombre_producto,
                    cantidad=Cantidad(item_model.cantidad),
                    precio_unitario=Precio(item_model.precio_unitario)
                )
                items.append(item)
            
            # Crear entidad de dominio del pedido
            pedido = Pedido(
                id=uuid.UUID(pedido_model.id),
                vendedor_id=pedido_model.vendedor_id,
                cliente_id=pedido_model.cliente_id,
                items=items,
                estado=EstadoPedido(pedido_model.estado),
                total=Precio(pedido_model.total)
            )
            pedidos.append(pedido)
        
        logger.info(f"Encontrados {len(pedidos)} pedidos")
        return pedidos
    
    def actualizar(self, pedido: Pedido) -> Pedido:
        """Actualizar un pedido existente"""
        pedido_model = PedidoModel.query.get(str(pedido.id))
        if not pedido_model:
            return None
        
        # Actualizar datos del pedido
        pedido_model.estado = pedido.estado.estado
        pedido_model.total = pedido.total.valor
        
        # Eliminar items existentes
        ItemPedidoModel.query.filter_by(pedido_id=str(pedido.id)).delete()
        
        # Crear nuevos items
        for item in pedido.items:
            item_model = ItemPedidoModel(
                id=str(item.id),
                pedido_id=str(pedido.id),
                producto_id=item.producto_id,
                nombre_producto=item.nombre_producto,
                cantidad=item.cantidad.valor,
                precio_unitario=item.precio_unitario.valor,
                subtotal=item.calcular_subtotal()
            )
            db.session.add(item_model)
        
        db.session.commit()
        return pedido
    
    def eliminar(self, pedido_id: str) -> bool:
        """Eliminar un pedido y sus items"""
        try:
            # Eliminar items primero
            ItemPedidoModel.query.filter_by(pedido_id=pedido_id).delete()
            
            # Eliminar pedido
            pedido_model = PedidoModel.query.get(pedido_id)
            if pedido_model:
                db.session.delete(pedido_model)
                db.session.commit()
                return True
            return False
        except Exception as e:
            db.session.rollback()
            return False
