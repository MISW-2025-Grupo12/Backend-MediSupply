from config.db import db
from infraestructura.modelos import EntregaModel, InventarioModel
from aplicacion.dto import EntregaDTO, InventarioDTO
from datetime import datetime
import uuid

class RepositorioEntregaSQLite:
    """Repositorio para acceder a las entregas programadas (SQLite)."""

    def crear(self, entrega_dto: EntregaDTO) -> EntregaDTO:
        """Crear una nueva entrega en SQLite."""
        entrega_model = EntregaModel(
            id=str(entrega_dto.id),
            direccion=entrega_dto.direccion,
            fecha_entrega=entrega_dto.fecha_entrega,
            producto_id=entrega_dto.producto_id,
            cliente_id=entrega_dto.cliente_id
        )

        db.session.add(entrega_model)
        db.session.commit()
        return entrega_dto

    def obtener_todos(self) -> list[EntregaDTO]:
        """Obtener todas las entregas programadas."""
        entregas_model = EntregaModel.query.all()
        entregas_dto = []

        for entrega_model in entregas_model:
            entregas_dto.append(EntregaDTO(
                id=uuid.UUID(entrega_model.id),
                direccion=entrega_model.direccion,
                fecha_entrega=entrega_model.fecha_entrega,
                producto_id=entrega_model.producto_id,
                cliente_id=entrega_model.cliente_id
            ))

        return entregas_dto

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
                fecha_vencimiento=inventario_model.fecha_vencimiento
            ))
        
        return inventarios_dto

    def crear_lote(self, inventario_dto: InventarioDTO) -> InventarioDTO:
        """Crear un nuevo lote de inventario."""
        inventario_model = InventarioModel(
            producto_id=inventario_dto.producto_id,
            cantidad_disponible=inventario_dto.cantidad_disponible,
            cantidad_reservada=inventario_dto.cantidad_reservada,
            fecha_vencimiento=inventario_dto.fecha_vencimiento
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
        """Crear o actualizar un lote de inventario basado en producto_id y fecha_vencimiento."""
        try:
            # Buscar si ya existe un lote con el mismo producto_id y fecha_vencimiento
            inventario_model = InventarioModel.query.filter_by(
                producto_id=inventario_dto.producto_id,
                fecha_vencimiento=inventario_dto.fecha_vencimiento
            ).first()
            
            if inventario_model:
                # Actualizar el lote existente
                inventario_model.cantidad_disponible = inventario_dto.cantidad_disponible
                inventario_model.cantidad_reservada = inventario_dto.cantidad_reservada
            else:
                # Crear un nuevo lote
                inventario_model = InventarioModel(
                    producto_id=inventario_dto.producto_id,
                    cantidad_disponible=inventario_dto.cantidad_disponible,
                    cantidad_reservada=inventario_dto.cantidad_reservada,
                    fecha_vencimiento=inventario_dto.fecha_vencimiento
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
                fecha_vencimiento=inventario_model.fecha_vencimiento
            ))

        return inventarios_dto
