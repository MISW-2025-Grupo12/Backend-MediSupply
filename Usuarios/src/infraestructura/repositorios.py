from config.db import db
from infraestructura.modelos import ProveedorModel, VendedorModel, ClienteModel, AdministradorModel, RepartidorModel, UsuarioModel, TipoUsuario
from aplicacion.dto import ProveedorDTO, VendedorDTO, ClienteDTO, AdministradorDTO, RepartidorDTO
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
        proveedor_model = db.session.get(ProveedorModel, proveedor_id)
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
        vendedor_model = db.session.get(VendedorModel, vendedor_id)
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
            direccion=cliente_dto.direccion,
            estado=cliente_dto.estado
        )
        db.session.add(cliente_model)
        db.session.commit()
        return cliente_dto
    
    def obtener_por_id(self, cliente_id: str) -> ClienteDTO:
        """Obtener un cliente por ID"""
        cliente_model = db.session.get(ClienteModel, cliente_id)
        if not cliente_model:
            return None
            
        return ClienteDTO(
            id=uuid.UUID(cliente_model.id),
            nombre=cliente_model.nombre,
            email=cliente_model.email,
            identificacion=cliente_model.identificacion,
            telefono=cliente_model.telefono,
            direccion=cliente_model.direccion,
            estado=cliente_model.estado
        )
    
    def obtener_todos(self, *, sort_by: Optional[str] = None, order: Optional[str] = None) -> list[ClienteDTO]:
        # Normalizar parámetros
        allowed_fields = {
            'nombre': ClienteModel.nombre,
            'email': ClienteModel.email,
            'identificacion': ClienteModel.identificacion,
            'created_at': ClienteModel.created_at
        }

        # Valores por defecto
        sort_field = allowed_fields.get((sort_by or 'nombre').lower(), ClienteModel.nombre)
        sort_order_desc = (order or 'asc').lower() == 'desc'

        query = ClienteModel.query
        query = query.order_by(sort_field.desc() if sort_order_desc else sort_field.asc())
        clientes_model = query.all()
        return [
            ClienteDTO(
                id=uuid.UUID(c.id),
                nombre=c.nombre,
                email=c.email,
                identificacion=c.identificacion,
                telefono=c.telefono,
                direccion=c.direccion,
                estado=c.estado
            ) for c in clientes_model
        ]

class RepositorioAdministradorSQLite:
    def crear(self, administrador_dto: AdministradorDTO) -> AdministradorDTO:
        administrador_model = AdministradorModel(
            id=str(administrador_dto.id),
            nombre=administrador_dto.nombre,
            email=administrador_dto.email
        )
        db.session.add(administrador_model)
        db.session.commit()
        return administrador_dto
    
    def obtener_por_id(self, administrador_id: str) -> AdministradorDTO:
        """Obtener un administrador por ID"""
        administrador_model = db.session.get(AdministradorModel, administrador_id)
        if not administrador_model:
            return None
            
        return AdministradorDTO(
            id=uuid.UUID(administrador_model.id),
            nombre=administrador_model.nombre,
            email=administrador_model.email
        )
    
    def obtener_todos(self) -> list[AdministradorDTO]:
        administradores_model = AdministradorModel.query.all()
        return [
            AdministradorDTO(
                id=uuid.UUID(a.id),
                nombre=a.nombre,
                email=a.email
            ) for a in administradores_model
        ]

class RepositorioRepartidorSQLite:
    def crear(self, repartidor_dto: RepartidorDTO) -> RepartidorDTO:
        repartidor_model = RepartidorModel(
            id=str(repartidor_dto.id),
            nombre=repartidor_dto.nombre,
            email=repartidor_dto.email,
            identificacion=repartidor_dto.identificacion,
            telefono=repartidor_dto.telefono
        )
        db.session.add(repartidor_model)
        db.session.commit()
        return repartidor_dto
    
    def obtener_por_id(self, repartidor_id: str) -> RepartidorDTO:
        """Obtener un repartidor por ID"""
        repartidor_model = db.session.get(RepartidorModel, repartidor_id)
        if not repartidor_model:
            return None
            
        return RepartidorDTO(
            id=uuid.UUID(repartidor_model.id),
            nombre=repartidor_model.nombre,
            email=repartidor_model.email,
            identificacion=repartidor_model.identificacion,
            telefono=repartidor_model.telefono
        )
    
    def obtener_todos(self) -> list[RepartidorDTO]:
        repartidores_model = RepartidorModel.query.all()
        return [
            RepartidorDTO(
                id=uuid.UUID(r.id),
                nombre=r.nombre,
                email=r.email,
                identificacion=r.identificacion,
                telefono=r.telefono
            ) for r in repartidores_model
        ]


class RepositorioUsuario:
    """Repositorio para el manejo de usuarios (autenticación)"""
    
    def crear(self, email: str, password: str, tipo_usuario: str, entidad_id: str, identificacion: Optional[str] = None) -> UsuarioModel:
        """Crea un nuevo usuario con autenticación. identificacion es opcional para ADMINISTRADOR"""
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
        return db.session.get(UsuarioModel, usuario_id)
    
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
