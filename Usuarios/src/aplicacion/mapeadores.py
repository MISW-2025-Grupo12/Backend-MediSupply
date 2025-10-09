from aplicacion.dto import ProveedorDTO
from dominio.entidades import Proveedor
from dominio.objetos_valor import Nombre, Email, Direccion

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
