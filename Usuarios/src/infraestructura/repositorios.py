from config.db import db
from infraestructura.modelos import ProveedorModel, VendedorModel, ClienteModel, UsuarioModel, TipoUsuario
from aplicacion.dto import ProveedorDTO, VendedorDTO, ClienteDTO
import uuid
from typing import Optional

class RepositorioProveedorSQLite:
    def crear(self, proveedor_dto: ProveedorDTO) -> ProveedorDTO:
        proveedor_model = ProveedorModel(
            id=str(proveedor_dto.id),
            nombre=proveedor_dto.nombre,
            email=proveedor_dto.email,
            identificacion=proveedor_dto.identificacion,
            telefono=proveedor_dto.telefono,
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
            identificacion=proveedor_model.identificacion,
            telefono=proveedor_model.telefono,
            direccion=proveedor_model.direccion
        )
    
    def obtener_todos(self) -> list[ProveedorDTO]:
        proveedores_model = ProveedorModel.query.all()
        return [
            ProveedorDTO(
                id=uuid.UUID(p.id),
                nombre=p.nombre,
                email=p.email,
                identificacion=p.identificacion,
                telefono=p.telefono,
                direccion=p.direccion
            ) for p in proveedores_model
        ]

class RepositorioVendedorSQLite:
    def crear(self, vendedor_dto: VendedorDTO) -> VendedorDTO:
        vendedor_model = VendedorModel(
            id=str(vendedor_dto.id),
            nombre=vendedor_dto.nombre,
            email=vendedor_dto.email,
            identificacion=vendedor_dto.identificacion,
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
            identificacion=vendedor_model.identificacion,
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
                identificacion=v.identificacion,
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
            identificacion=cliente_dto.identificacion,
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
            identificacion=cliente_model.identificacion,
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
                identificacion=c.identificacion,
                telefono=c.telefono,
                direccion=c.direccion
            ) for c in clientes_model
        ]


class RepositorioUsuario:
    """Repositorio para el manejo de usuarios (autenticación)"""
    
    def crear(self, email: str, password: str, tipo_usuario: str, identificacion: str, entidad_id: str) -> UsuarioModel:
        """Crea un nuevo usuario con autenticación"""
        usuario = UsuarioModel(
            email=email,
            tipo_usuario=tipo_usuario,
            identificacion=identificacion,
            entidad_id=entidad_id,
            is_active=True
        )
        usuario.set_password(password)
        
        db.session.add(usuario)
        db.session.commit()
        
        return usuario
    
    def obtener_por_email(self, email: str) -> Optional[UsuarioModel]:
        """Obtiene un usuario por su email"""
        return UsuarioModel.query.filter_by(email=email).first()
    
    def obtener_por_identificacion(self, identificacion: str) -> Optional[UsuarioModel]:
        """Obtiene un usuario por su identificación"""
        return UsuarioModel.query.filter_by(identificacion=identificacion).first()
    
    def obtener_por_id(self, usuario_id: str) -> Optional[UsuarioModel]:
        """Obtiene un usuario por su ID"""
        return UsuarioModel.query.get(usuario_id)
    
    def existe_email(self, email: str) -> bool:
        """Verifica si un email ya está registrado"""
        return UsuarioModel.query.filter_by(email=email).first() is not None
    
    def existe_identificacion(self, identificacion: str) -> bool:
        """Verifica si una identificación ya está registrada"""
        return UsuarioModel.query.filter_by(identificacion=identificacion).first() is not None
    
    def actualizar(self, usuario: UsuarioModel):
        """Actualiza un usuario existente"""
        db.session.commit()
    
    def desactivar(self, usuario_id: str):
        """Desactiva un usuario"""
        usuario = self.obtener_por_id(usuario_id)
        if usuario:
            usuario.is_active = False
            db.session.commit()
