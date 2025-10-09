from config.db import db
from infraestructura.modelos import EntregaModel
from aplicacion.dto import EntregaDTO
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
