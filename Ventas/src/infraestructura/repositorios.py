from config.db import db
from infraestructura.modelos import VisitaModel
from aplicacion.dto import VisitaDTO
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
            descripcion=visita_model.descripcion
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
                descripcion=visita_model.descripcion
            ))
        
        return visitas_dto
