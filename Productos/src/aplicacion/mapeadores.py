from aplicacion.dto import ProductoDTO, CategoriaDTO
from aplicacion.dto_agregacion import ProductoAgregacionDTO
from dominio.entidades import Producto
from dominio.objetos_valor import Nombre, Descripcion, Precio, Categoria, Proveedor
from datetime import datetime

class MapeadorProductoDTOJson:
    def externo_a_dto(self, externo: dict) -> ProductoDTO:
        """Convierte JSON externo a ProductoDTO"""
        return ProductoDTO(
            nombre=externo.get('nombre', ''),
            descripcion=externo.get('descripcion', ''),
            precio=float(externo.get('precio', 0)),
            categoria=externo.get('categoria', ''),
            categoria_id=externo.get('categoria_id', ''),
            proveedor_id=externo.get('proveedor_id', ''),
            id=externo.get('id')
        )
    
    def dto_a_externo(self, dto: ProductoDTO) -> dict:
        """Convierte ProductoDTO a JSON externo"""
        return {
            'id': str(dto.id),
            'nombre': dto.nombre,
            'descripcion': dto.descripcion,
            'precio': dto.precio,
            'categoria': dto.categoria,
            'categoria_id': dto.categoria_id,
            'proveedor_id': dto.proveedor_id
        }

class MapeadorProducto:
    def entidad_a_dto(self, entidad: Producto) -> ProductoDTO:
        """Convierte entidad Producto a ProductoDTO"""
        return ProductoDTO(
            id=entidad.id,
            nombre=entidad.nombre.nombre,
            descripcion=entidad.descripcion.descripcion,
            precio=entidad.precio.precio,
            categoria=entidad.categoria.nombre,
            categoria_id=entidad.categoria_id,
            proveedor_id=entidad.proveedor_id
        )
    
    def dto_a_entidad(self, dto: ProductoDTO) -> Producto:
        """Convierte ProductoDTO a entidad Producto"""
        return Producto(
            id=dto.id,
            nombre=Nombre(dto.nombre),
            descripcion=Descripcion(dto.descripcion),
            precio=Precio(dto.precio),
            categoria=Categoria(dto.categoria),
            categoria_id=dto.categoria_id,
            proveedor_id=dto.proveedor_id
        )

class MapeadorCategoriaDTOJson:
    def externo_a_dto(self, externo: dict) -> CategoriaDTO:
        """Convierte JSON externo a CategoriaDTO"""
        return CategoriaDTO(
            nombre=externo.get('nombre', ''),
            descripcion=externo.get('descripcion', ''),
            id=externo.get('id')
        )
    
    def dto_a_externo(self, dto: CategoriaDTO) -> dict:
        """Convierte CategoriaDTO a JSON externo"""
        return {
            'id': str(dto.id),
            'nombre': dto.nombre,
            'descripcion': dto.descripcion
        }

class MapeadorProductoAgregacionDTOJson:
    """Mapeador para agregación completa de productos optimizada"""
    
    def agregacion_a_externo(self, agregacion: ProductoAgregacionDTO) -> dict:
        """Convierte ProductoAgregacionDTO a JSON externo con datos completos"""
        return {
            'id': str(agregacion.id),
            'nombre': agregacion.nombre,
            'descripcion': agregacion.descripcion,
            'precio': agregacion.precio,
            'categoria': {
                'id': str(agregacion.categoria_id),
                'nombre': agregacion.categoria_nombre,
                'descripcion': agregacion.categoria_descripcion
            },
            'proveedor': {
                'id': agregacion.proveedor_id,
                'nombre': agregacion.proveedor_nombre,
                'email': agregacion.proveedor_email,
                'direccion': agregacion.proveedor_direccion
            }
        }
    
    def agregaciones_a_externo(self, agregaciones: list[ProductoAgregacionDTO]) -> list[dict]:
        """Convierte lista de ProductoAgregacionDTO a lista de JSON externo"""
        return [self.agregacion_a_externo(agregacion) for agregacion in agregaciones]

