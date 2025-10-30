from config.db import db
from infraestructura.modelos import VisitaModel, PedidoModel, ItemPedidoModel, EvidenciaVisitaModel, PlanVisitaModel
from aplicacion.dto import VisitaDTO, PedidoDTO, ItemPedidoDTO, EvidenciaVisitaDTO
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
        visita_model = db.session.get(VisitaModel, visita_id)
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
        
        pedido_model = db.session.get(PedidoModel, pedido_id)
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

    def obtener_pedidos_confirmados(self, vendedor_id: str = None, fecha_inicio=None, fecha_fin=None) -> list[Pedido]:
        """
        Obtener pedidos ENTREGADOS, opcionalmente filtrados por vendedor y rango de fechas.


        Comportamiento:
        - Si se envían ambas fechas -> filtra entre ellas (rango cerrado).
        - Si solo se envía fecha_inicio -> trae desde esa fecha hasta el futuro.
        - Si solo se envía fecha_fin -> trae desde el inicio hasta esa fecha.
        - Si no se envían fechas -> trae todos los pedidos entregados.
        """
        import logging
        from datetime import datetime
        from sqlalchemy import func

        logger = logging.getLogger(__name__)
        logger.info("🔎 Obteniendo pedidos ENTREGADOS filtrados")

        # Consulta base (insensible a mayúsculas) - CAMBIO: ahora filtra por 'entregado'
        query = PedidoModel.query.filter(func.lower(PedidoModel.estado) == "entregado")

        # Filtro opcional por vendedor
        if vendedor_id:
            query = query.filter(PedidoModel.vendedor_id == vendedor_id)
            logger.info(f"📦 Filtrando por vendedor_id={vendedor_id}")

        # Filtros por fechas usando 'created_at'
        if fecha_inicio or fecha_fin:
            try:
                if fecha_inicio:
                    inicio = datetime.fromisoformat(fecha_inicio)
                else:
                    inicio = datetime.min  # fecha más antigua posible

                if fecha_fin:
                    fin = datetime.fromisoformat(fecha_fin)
                else:
                    fin = datetime.max  # hasta el futuro

                query = query.filter(PedidoModel.created_at >= inicio, PedidoModel.created_at <= fin)
                logger.info(f"🗓️ Filtrando pedidos creados entre {inicio} y {fin}")
            except Exception as e:
                logger.warning(f"⚠️ Formato inválido de fechas: {e}")

        # Ejecutar consulta
        pedidos_model = query.all()

        if not pedidos_model:
            logger.info("⚠️ No se encontraron pedidos confirmados con los filtros aplicados")
            return []

        pedidos = []

        for pedido_model in pedidos_model:
            # Obtener items asociados
            items_model = ItemPedidoModel.query.filter_by(pedido_id=pedido_model.id).all()
            items = []
            for item_model in items_model:
                items.append(ItemPedido(
                    id=uuid.UUID(item_model.id),
                    producto_id=item_model.producto_id,
                    nombre_producto=item_model.nombre_producto,
                    cantidad=Cantidad(item_model.cantidad),
                    precio_unitario=Precio(item_model.precio_unitario)
                ))

            # Convertir total a float de forma segura
            try:
                total_valor = float(pedido_model.total)
            except Exception:
                total_valor = 0.0

            # Crear entidad de dominio Pedido
            pedido = Pedido(
                id=uuid.UUID(pedido_model.id),
                vendedor_id=pedido_model.vendedor_id,
                cliente_id=getattr(pedido_model, 'cliente_id', None),
                items=items,
                estado=EstadoPedido(pedido_model.estado),
                total=Precio(total_valor)
            )

            pedido._created_at_model = pedido_model.created_at

            pedidos.append(pedido)

        logger.info(f"✅ Pedidos CONFIRMADOS encontrados: {len(pedidos)}")
        return pedidos

class RepositorioEvidenciaVisita:
    def crear(self, evidencia_dto: EvidenciaVisitaDTO) -> EvidenciaVisitaDTO:
        """Crear una nueva evidencia de visita"""
        evidencia_model = EvidenciaVisitaModel(
            id=str(evidencia_dto.id),
            visita_id=evidencia_dto.visita_id,
            archivo_url=evidencia_dto.archivo_url,
            nombre_archivo=evidencia_dto.nombre_archivo,
            formato=evidencia_dto.formato,
            tamaño_bytes=evidencia_dto.tamaño_bytes,
            comentarios=evidencia_dto.comentarios,
            vendedor_id=evidencia_dto.vendedor_id
        )
        db.session.add(evidencia_model)
        db.session.commit()
        return evidencia_dto
    
    def obtener_por_visita(self, visita_id: str) -> list[EvidenciaVisitaDTO]:
        """Obtener todas las evidencias de una visita"""
        evidencias_model = EvidenciaVisitaModel.query.filter_by(visita_id=visita_id).all()
        return [
            EvidenciaVisitaDTO(
                id=uuid.UUID(e.id),
                visita_id=e.visita_id,
                archivo_url=e.archivo_url,
                nombre_archivo=e.nombre_archivo,
                formato=e.formato,
                tamaño_bytes=e.tamaño_bytes,
                comentarios=e.comentarios,
                vendedor_id=e.vendedor_id,
                created_at=e.created_at
            )
            for e in evidencias_model
        ]
    
    def eliminar(self, evidencia_id: str, storage_service) -> bool:
        """Eliminar una evidencia y su archivo del storage"""
        evidencia = EvidenciaVisitaModel.query.get(evidencia_id)
        if evidencia:
            storage_service.eliminar_archivo(evidencia.archivo_url)
            db.session.delete(evidencia)
            db.session.commit()
            return True
        return False

# Alias para compatibilidad
RepositorioVisita = RepositorioVisitaSQLite
RepositorioPedido = RepositorioPedidoSQLite

class RepositorioPlanes:
    """Repositorio para gestionar Planes de Visita."""

    def obtener_todos(self) -> list[dict]:
        """Obtener todos los planes incluyendo las visitas agrupadas por cliente"""
        planes = PlanVisitaModel.query.all()
        resultado = []

        for plan in planes:
            # Agrupar visitas por cliente con objetos de visita completos
            visitas_por_cliente = {}
            for visita in plan.plan_visitas:
                if visita.cliente_id not in visitas_por_cliente:
                    visitas_por_cliente[visita.cliente_id] = []
                visitas_por_cliente[visita.cliente_id].append({
                    "id": visita.id,
                    "fecha_programada": visita.fecha_programada.isoformat(),
                    "direccion": visita.direccion,
                    "telefono": visita.telefono,
                    "estado": visita.estado
                })

            visitas_clientes = [
                {"id_cliente": cid, "visitas": visitas}
                for cid, visitas in visitas_por_cliente.items()
            ]

            resultado.append({
                "id": plan.id,
                "nombre": plan.nombre,
                "id_usuario": plan.id_usuario,
                "fecha_inicio": plan.fecha_inicio.isoformat(),
                "fecha_fin": plan.fecha_fin.isoformat(),
                "visitas_clientes": visitas_clientes
            })

        return resultado

    def obtener_por_usuario(self, user_id: str) -> list[dict]:
        """Obtener los planes de un usuario específico incluyendo las visitas agrupadas por cliente"""
        planes = PlanVisitaModel.query.filter_by(id_usuario=user_id).all()
        resultado = []

        for plan in planes:
            # Agrupar visitas por cliente con objetos de visita completos
            visitas_por_cliente = {}
            for visita in plan.plan_visitas:
                if visita.cliente_id not in visitas_por_cliente:
                    visitas_por_cliente[visita.cliente_id] = []
                visitas_por_cliente[visita.cliente_id].append({
                    "id": visita.id,
                    "fecha_programada": visita.fecha_programada.isoformat(),
                    "direccion": visita.direccion,
                    "telefono": visita.telefono,
                    "estado": visita.estado
                })

            visitas_clientes = [
                {"id_cliente": cid, "visitas": visitas}
                for cid, visitas in visitas_por_cliente.items()
            ]

            resultado.append({
                "id": plan.id,
                "nombre": plan.nombre,
                "id_usuario": plan.id_usuario,
                "fecha_inicio": plan.fecha_inicio.isoformat(),
                "fecha_fin": plan.fecha_fin.isoformat(),
                "visitas_clientes": visitas_clientes
            })

        return resultado