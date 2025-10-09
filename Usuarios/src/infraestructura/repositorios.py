from config.db import db
from infraestructura.modelos import ProveedorModel, VendedorModel, ClienteModel
from aplicacion.dto import ProveedorDTO, VendedorDTO, ClienteDTO
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

class RepositorioVendedorSQLite:
    def crear(self, vendedor_dto: VendedorDTO) -> VendedorDTO:
        vendedor_model = VendedorModel(
            id=str(vendedor_dto.id),
            nombre=vendedor_dto.nombre,
            email=vendedor_dto.email,
            telefono=vendedor_dto.telefono,
            direccion=vendedor_dto.direccion
        )
        db.session.add(vendedor_model)
        db.session.commit()
        return vendedor_dto
    
    def obtener_por_id(self, vendedor_id: str) -> VendedorDTO:
        """Obtener un vendedor por ID"""
        vendedor_model = VendedorModel.query.get(vendedor_id)
        if not vendedor_model:
            return None
            
        return VendedorDTO(
            id=uuid.UUID(vendedor_model.id),
            nombre=vendedor_model.nombre,
            email=vendedor_model.email,
            telefono=vendedor_model.telefono,
            direccion=vendedor_model.direccion
        )
    
    def obtener_todos(self) -> list[VendedorDTO]:
        vendedores_model = VendedorModel.query.all()
        return [
            VendedorDTO(
                id=uuid.UUID(v.id),
                nombre=v.nombre,
                email=v.email,
                telefono=v.telefono,
                direccion=v.direccion
            ) for v in vendedores_model
        ]

class RepositorioClienteSQLite:
    def crear(self, cliente_dto: ClienteDTO) -> ClienteDTO:
        cliente_model = ClienteModel(
            id=str(cliente_dto.id),
            nombre=cliente_dto.nombre,
            email=cliente_dto.email,
            telefono=cliente_dto.telefono,
            direccion=cliente_dto.direccion
        )
        db.session.add(cliente_model)
        db.session.commit()
        return cliente_dto
    
    def obtener_por_id(self, cliente_id: str) -> ClienteDTO:
        """Obtener un cliente por ID"""
        cliente_model = ClienteModel.query.get(cliente_id)
        if not cliente_model:
            return None
            
        return ClienteDTO(
            id=uuid.UUID(cliente_model.id),
            nombre=cliente_model.nombre,
            email=cliente_model.email,
            telefono=cliente_model.telefono,
            direccion=cliente_model.direccion
        )
    
    def obtener_todos(self) -> list[ClienteDTO]:
        clientes_model = ClienteModel.query.all()
        return [
            ClienteDTO(
                id=uuid.UUID(c.id),
                nombre=c.nombre,
                email=c.email,
                telefono=c.telefono,
                direccion=c.direccion
            ) for c in clientes_model
        ]
