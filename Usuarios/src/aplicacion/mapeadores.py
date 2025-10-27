from aplicacion.dto import ProveedorDTO, VendedorDTO, ClienteDTO
from dominio.entidades import Proveedor, Vendedor, Cliente
from dominio.objetos_valor import Nombre, Email, Direccion, Telefono, Identificacion

class MapeadorProveedorDTOJson:
    def dto_a_externo(self, dto: ProveedorDTO) -> dict:
        return {
            'id': str(dto.id),
            'nombre': dto.nombre,
            'email': dto.email,
            'identificacion': dto.identificacion,
            'telefono': dto.telefono,
            'direccion': dto.direccion
        }
    
    def externo_a_dto(self, externo: dict) -> ProveedorDTO:
        return ProveedorDTO(
            id=externo.get('id'),
            nombre=externo.get('nombre', ''),
            email=externo.get('email', ''),
            identificacion=externo.get('identificacion', ''),
            telefono=externo.get('telefono', ''),
            direccion=externo.get('direccion', '')
        )

class MapeadorProveedor:
    def entidad_a_dto(self, entidad: Proveedor) -> ProveedorDTO:
        return ProveedorDTO(
            id=entidad._id, 
            nombre=entidad.nombre.nombre,
            email=entidad.email.email,
            identificacion=entidad.identificacion.identificacion,
            telefono=entidad.telefono.telefono,
            direccion=entidad.direccion.direccion
        )

class MapeadorVendedorDTOJson:
    def dto_a_externo(self, dto: VendedorDTO) -> dict:
        return {
            'id': str(dto.id),
            'nombre': dto.nombre,
            'email': dto.email,
            'identificacion': dto.identificacion,
            'telefono': dto.telefono,
            'direccion': dto.direccion
        }
    
    def externo_a_dto(self, externo: dict) -> VendedorDTO:
        return VendedorDTO(
            id=externo.get('id'),
            nombre=externo.get('nombre', ''),
            email=externo.get('email', ''),
            identificacion=externo.get('identificacion', ''),
            telefono=externo.get('telefono', ''),
            direccion=externo.get('direccion', '')
        )
    
    def dtos_a_externo(self, dtos: list[VendedorDTO]) -> list[dict]:
        return [self.dto_a_externo(dto) for dto in dtos]

class MapeadorVendedor:
    def entidad_a_dto(self, entidad: Vendedor) -> VendedorDTO:
        return VendedorDTO(
            id=entidad._id, 
            nombre=entidad.nombre.nombre,
            email=entidad.email.email,
            identificacion=entidad.identificacion.identificacion,
            telefono=entidad.telefono.telefono,
            direccion=entidad.direccion.direccion
        )

class MapeadorClienteDTOJson:
    def dto_a_externo(self, dto: ClienteDTO) -> dict:
        return {
            'id': str(dto.id),
            'nombre': dto.nombre,
            'email': dto.email,
            'identificacion': dto.identificacion,
            'telefono': dto.telefono,
            'direccion': dto.direccion,
            'estado': dto.estado
        }
    
    def externo_a_dto(self, externo: dict) -> ClienteDTO:
        return ClienteDTO(
            id=externo.get('id'),
            nombre=externo.get('nombre', ''),
            email=externo.get('email', ''),
            identificacion=externo.get('identificacion', ''),
            telefono=externo.get('telefono', ''),
            direccion=externo.get('direccion', ''),
            estado=externo.get('estado', 'ACTIVO')
        )
    
    def dtos_a_externo(self, dtos: list[ClienteDTO]) -> list[dict]:
        return [self.dto_a_externo(dto) for dto in dtos]

class MapeadorCliente:
    def entidad_a_dto(self, entidad: Cliente) -> ClienteDTO:
        return ClienteDTO(
            id=entidad._id,
            nombre=entidad.nombre.nombre,
            email=entidad.email.email,
            identificacion=entidad.identificacion.identificacion,
            telefono=entidad.telefono.telefono,
            direccion=entidad.direccion.direccion,
            estado=entidad.estado.estado
        )
