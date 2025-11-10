from config.db import db
from infraestructura.modelos import EntregaModel, InventarioModel, BodegaModel
from aplicacion.dto import EntregaDTO, InventarioDTO, BodegaDTO
from datetime import datetime
import uuid
import json

class RepositorioEntregaSQLite:
    """Repositorio para acceder a las entregas programadas (SQLite)."""

    def crear(self, entrega_dto: EntregaDTO) -> EntregaDTO:
        """Crear una nueva entrega en SQLite con el pedido almacenado como JSON."""
        entrega_model = EntregaModel(
            id=str(entrega_dto.id),
            direccion=entrega_dto.direccion,
            fecha_entrega=entrega_dto.fecha_entrega,
            pedido=json.dumps(entrega_dto.pedido or {})  # ✅ guardamos JSON
        )

        db.session.add(entrega_model)
        db.session.commit()
        return entrega_dto

    def obtener_todos(self) -> list[EntregaDTO]:
        entregas_model = EntregaModel.query.all()
        entregas_dto = []

        for entrega_model in entregas_model:
            pedido_data = None
            if entrega_model.pedido:
                try:
                    pedido_data = json.loads(entrega_model.pedido)
                except Exception:
                    pedido_data = None

            entregas_dto.append(EntregaDTO(
                id=uuid.UUID(entrega_model.id),
                direccion=entrega_model.direccion,
                fecha_entrega=entrega_model.fecha_entrega,
                pedido=pedido_data
            ))

        return entregas_dto

    def obtener_por_rango(self, fecha_inicio: datetime, fecha_fin: datetime) -> list[EntregaDTO]:
        """Obtener entregas filtradas por rango de fechas (incluye pedido JSON)."""

        # Si las fechas son iguales → ampliar el rango de 00:00 a 23:59:59
        if fecha_inicio.date() == fecha_fin.date():
            fecha_fin = datetime.combine(fecha_fin.date(), datetime.max.time())

        entregas_model = EntregaModel.query.filter(
            EntregaModel.fecha_entrega >= fecha_inicio,
            EntregaModel.fecha_entrega <= fecha_fin
        ).all()

        entregas_dto = []
        for entrega_model in entregas_model:
            try:
                pedido_data = json.loads(entrega_model.pedido) if entrega_model.pedido else None
            except Exception:
                pedido_data = None

            entregas_dto.append(EntregaDTO(
                id=uuid.UUID(entrega_model.id),
                direccion=entrega_model.direccion,
                fecha_entrega=entrega_model.fecha_entrega,
                pedido=pedido_data
            ))

        return entregas_dto

class RepositorioBodegaSQLite:
    """Repositorio para acceder a las bodegas (SQLite)."""

    def crear(self, bodega_dto: BodegaDTO) -> BodegaDTO:
        """Crear una nueva bodega."""
        bodega_model = BodegaModel(
            id=bodega_dto.id,
            nombre=bodega_dto.nombre,
            direccion=bodega_dto.direccion
        )
        db.session.add(bodega_model)
        db.session.commit()
        return bodega_dto
    
    def obtener_por_id(self, bodega_id: str) -> BodegaModel:
        """Obtener una bodega por su ID."""
        return BodegaModel.query.get(bodega_id)
    
    def obtener_todas(self) -> list[BodegaModel]:
        """Obtener todas las bodegas."""
        return BodegaModel.query.all()
    
    def obtener_inventario_por_bodega(self, bodega_id: str) -> list[InventarioModel]:
        """Obtener inventario de una bodega específica."""
        return InventarioModel.query.filter_by(bodega_id=bodega_id).all()
    
    def obtener_todos_los_inventarios(self) -> list[InventarioModel]:
        """Obtener todos los inventarios de todas las bodegas."""
        return InventarioModel.query.all()

class RepositorioInventarioSQLite:
    """Repositorio para acceder al inventario (SQLite)."""

    def obtener_por_producto_id(self, producto_id: str) -> list[InventarioDTO]:
        """Obtener todos los lotes de inventario de un producto específico."""
        inventarios_model = InventarioModel.query.filter_by(producto_id=producto_id).all()
        
        if not inventarios_model:
            return []
        
        inventarios_dto = []
        for inventario_model in inventarios_model:
            inventarios_dto.append(InventarioDTO(
                producto_id=inventario_model.producto_id,
                cantidad_disponible=inventario_model.cantidad_disponible,
                cantidad_reservada=inventario_model.cantidad_reservada,
                fecha_vencimiento=inventario_model.fecha_vencimiento,
                requiere_cadena_frio=inventario_model.requiere_cadena_frio, 
                bodega_id=inventario_model.bodega_id,
                pasillo=inventario_model.pasillo,
                estante=inventario_model.estante,
                id=inventario_model.id
            ))
        
        return inventarios_dto

    def crear(self, inventario_dto: InventarioDTO) -> InventarioDTO:
        """Crear un nuevo lote de inventario."""
        inventario_model = InventarioModel(
            id=inventario_dto.id,
            producto_id=inventario_dto.producto_id,
            cantidad_disponible=inventario_dto.cantidad_disponible,
            cantidad_reservada=inventario_dto.cantidad_reservada,
            fecha_vencimiento=inventario_dto.fecha_vencimiento,
            bodega_id=inventario_dto.bodega_id if hasattr(inventario_dto, 'bodega_id') else None,
            pasillo=inventario_dto.pasillo if hasattr(inventario_dto, 'pasillo') else None,
            estante=inventario_dto.estante if hasattr(inventario_dto, 'estante') else None,
            requiere_cadena_frio=inventario_dto.requiere_cadena_frio
        )
        db.session.add(inventario_model)
        db.session.commit()
        return inventario_dto

    def crear_lote(self, inventario_dto: InventarioDTO) -> InventarioDTO:
        """Crear un nuevo lote de inventario."""
        inventario_model = InventarioModel(
            producto_id=inventario_dto.producto_id,
            cantidad_disponible=inventario_dto.cantidad_disponible,
            cantidad_reservada=inventario_dto.cantidad_reservada,
            fecha_vencimiento=inventario_dto.fecha_vencimiento,
            requiere_cadena_frio=inventario_dto.requiere_cadena_frio,
            bodega_id=inventario_dto.bodega_id if hasattr(inventario_dto, 'bodega_id') else None,
            pasillo=inventario_dto.pasillo if hasattr(inventario_dto, 'pasillo') else None,
            estante=inventario_dto.estante if hasattr(inventario_dto, 'estante') else None
        )
        db.session.add(inventario_model)
        db.session.commit()
        return inventario_dto

    def actualizar_cantidades_lote(self, lote_id: str, cantidad_disponible: int, cantidad_reservada: int) -> bool:
        """Actualizar cantidades de un lote específico."""
        try:
            inventario_model = InventarioModel.query.get(lote_id)
            
            if not inventario_model:
                return False
            
            inventario_model.cantidad_disponible = cantidad_disponible
            inventario_model.cantidad_reservada = cantidad_reservada
            
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            return False

    def crear_o_actualizar(self, inventario_dto: InventarioDTO) -> InventarioDTO:
        """Crear o actualizar un lote de inventario basado en producto_id y fecha_vencimiento, o por ID si está disponible."""
        try:
            inventario_model = None
            
            # Si el DTO tiene un ID, intentar buscar por ID primero
            if inventario_dto.id:
                inventario_model = InventarioModel.query.get(inventario_dto.id)
            
            # Si no se encontró por ID, buscar por producto_id y fecha_vencimiento
            if not inventario_model:
                inventario_model = InventarioModel.query.filter_by(
                    producto_id=inventario_dto.producto_id,
                    fecha_vencimiento=inventario_dto.fecha_vencimiento
                ).first()

            if inventario_model:
                # Actualizar el lote existente con todos los campos
                inventario_model.cantidad_disponible = inventario_dto.cantidad_disponible
                inventario_model.cantidad_reservada = inventario_dto.cantidad_reservada
                inventario_model.requiere_cadena_frio = inventario_dto.requiere_cadena_frio
                # Actualizar ubicación si está disponible
                if inventario_dto.bodega_id is not None:
                    inventario_model.bodega_id = inventario_dto.bodega_id
                if inventario_dto.pasillo is not None:
                    inventario_model.pasillo = inventario_dto.pasillo
                if inventario_dto.estante is not None:
                    inventario_model.estante = inventario_dto.estante
            else:
                # Crear un nuevo lote
                inventario_model = InventarioModel(
                    id=inventario_dto.id if inventario_dto.id else None,
                    producto_id=inventario_dto.producto_id,
                    cantidad_disponible=inventario_dto.cantidad_disponible,
                    cantidad_reservada=inventario_dto.cantidad_reservada,
                    fecha_vencimiento=inventario_dto.fecha_vencimiento,
                    bodega_id=inventario_dto.bodega_id if inventario_dto.bodega_id else None,
                    pasillo=inventario_dto.pasillo if inventario_dto.pasillo else None,
                    estante=inventario_dto.estante if inventario_dto.estante else None,
                    requiere_cadena_frio=inventario_dto.requiere_cadena_frio
                )
                db.session.add(inventario_model)
            
            db.session.commit()
            return inventario_dto
        except Exception as e:
            db.session.rollback()
            raise e
    
    def obtener_todos(self) -> list[InventarioDTO]:
        """Obtener todo el inventario."""
        inventarios_model = InventarioModel.query.all()
        inventarios_dto = []

        for inventario_model in inventarios_model:
            inventarios_dto.append(InventarioDTO(
                producto_id=inventario_model.producto_id,
                cantidad_disponible=inventario_model.cantidad_disponible,
                cantidad_reservada=inventario_model.cantidad_reservada,
                fecha_vencimiento=inventario_model.fecha_vencimiento,
                requiere_cadena_frio=inventario_model.requiere_cadena_frio
            ))

        return inventarios_dto

    def eliminar(self, producto_id: str) -> bool:
        """Eliminar todos los lotes de inventario de un producto específico."""
        try:
            inventarios_model = InventarioModel.query.filter_by(producto_id=producto_id).all()
            
            if not inventarios_model:
                return False
            
            for inventario_model in inventarios_model:
                db.session.delete(inventario_model)
            
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            return False