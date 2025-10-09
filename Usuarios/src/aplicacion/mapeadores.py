from aplicacion.dto import ProveedorDTO, VendedorDTO, ClienteDTO
from dominio.entidades import Proveedor, Vendedor, Cliente
from dominio.objetos_valor import Nombre, Email, Direccion, Telefono

class MapeadorProveedorDTOJson:
    def dto_a_externo(self, dto: ProveedorDTO) -> dict:
        return {
            'id': str(dto.id),
            'nombre': dto.nombre,
            'email': dto.email,
            'direccion': dto.direccion
        }
    
    def externo_a_dto(self, externo: dict) -> ProveedorDTO:
        return ProveedorDTO(
            id=externo.get('id'),
            nombre=externo.get('nombre', ''),
            email=externo.get('email', ''),
            direccion=externo.get('direccion', '')
        )

class MapeadorProveedor:
    def entidad_a_dto(self, entidad: Proveedor) -> ProveedorDTO:
        return ProveedorDTO(
            id=entidad.id,
            nombre=entidad.nombre.nombre,
            email=entidad.email.email,
            direccion=entidad.direccion.direccion
        )

class MapeadorVendedorDTOJson:
    def dto_a_externo(self, dto: VendedorDTO) -> dict:
        return {
            'id': str(dto.id),
            'nombre': dto.nombre,
            'email': dto.email,
            'telefono': dto.telefono,
            'direccion': dto.direccion
        }
    
    def externo_a_dto(self, externo: dict) -> VendedorDTO:
        return VendedorDTO(
            id=externo.get('id'),
            nombre=externo.get('nombre', ''),
            email=externo.get('email', ''),
            telefono=externo.get('telefono', ''),
            direccion=externo.get('direccion', '')
        )
    
    def dtos_a_externo(self, dtos: list[VendedorDTO]) -> list[dict]:
        return [self.dto_a_externo(dto) for dto in dtos]

class MapeadorVendedor:
    def entidad_a_dto(self, entidad: Vendedor) -> VendedorDTO:
        return VendedorDTO(
            id=entidad.id,
            nombre=entidad.nombre.nombre,
            email=entidad.email.email,
            telefono=entidad.telefono.telefono,
            direccion=entidad.direccion.direccion
        )

class MapeadorClienteDTOJson:
    def dto_a_externo(self, dto: ClienteDTO) -> dict:
        return {
            'id': str(dto.id),
            'nombre': dto.nombre,
            'email': dto.email,
            'telefono': dto.telefono,
            'direccion': dto.direccion
        }
    
    def externo_a_dto(self, externo: dict) -> ClienteDTO:
        return ClienteDTO(
            id=externo.get('id'),
            nombre=externo.get('nombre', ''),
            email=externo.get('email', ''),
            telefono=externo.get('telefono', ''),
            direccion=externo.get('direccion', '')
        )
    
    def dtos_a_externo(self, dtos: list[ClienteDTO]) -> list[dict]:
        return [self.dto_a_externo(dto) for dto in dtos]

class MapeadorCliente:
    def entidad_a_dto(self, entidad: Cliente) -> ClienteDTO:
        return ClienteDTO(
            id=entidad.id,
            nombre=entidad.nombre.nombre,
            email=entidad.email.email,
            telefono=entidad.telefono.telefono,
            direccion=entidad.direccion.direccion
        )
