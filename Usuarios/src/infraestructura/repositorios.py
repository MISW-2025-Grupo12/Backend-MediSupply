from config.db import db
from infraestructura.modelos import ProveedorModel
from aplicacion.dto import ProveedorDTO
import uuid

class RepositorioProveedorSQLite:
    def crear(self, proveedor_dto: ProveedorDTO) -> ProveedorDTO:
        proveedor_model = ProveedorModel(
            id=str(proveedor_dto.id),
            nombre=proveedor_dto.nombre,
            email=proveedor_dto.email,
            direccion=proveedor_dto.direccion
        )
        db.session.add(proveedor_model)
        db.session.commit()
        return proveedor_dto
    
    def obtener_por_id(self, proveedor_id: str) -> ProveedorDTO:
        """Obtener un proveedor por ID"""
        proveedor_model = ProveedorModel.query.get(proveedor_id)
        if not proveedor_model:
            return None
            
        return ProveedorDTO(
            id=uuid.UUID(proveedor_model.id),
            nombre=proveedor_model.nombre,
            email=proveedor_model.email,
            direccion=proveedor_model.direccion
        )
    
    def obtener_todos(self) -> list[ProveedorDTO]:
        proveedores_model = ProveedorModel.query.all()
        return [
            ProveedorDTO(
                id=uuid.UUID(p.id),
                nombre=p.nombre,
                email=p.email,
                direccion=p.direccion
            ) for p in proveedores_model
        ]
