from aplicacion.dto import ProductoDTO
from dominio.entidades import Producto
from dominio.objetos_valor import Nombre, Descripcion, Precio, Stock, FechaVencimiento, Categoria, Proveedor
from datetime import datetime

class MapeadorProductoDTOJson:
    def externo_a_dto(self, externo: dict) -> ProductoDTO:
        """Convierte JSON externo a ProductoDTO"""
        return ProductoDTO(
            nombre=externo.get('nombre', ''),
            descripcion=externo.get('descripcion', ''),
            precio=float(externo.get('precio', 0)),
            stock=int(externo.get('stock', 0)),
            fecha_vencimiento=datetime.fromisoformat(externo.get('fecha_vencimiento', datetime.now().isoformat())),
            categoria=externo.get('categoria', ''),
            proveedor=externo.get('proveedor', ''),
            categoria_id=externo.get('categoria_id', ''),
            id=externo.get('id')
        )
    
    def dto_a_externo(self, dto: ProductoDTO) -> dict:
        """Convierte ProductoDTO a JSON externo"""
        return {
            'id': str(dto.id),
            'nombre': dto.nombre,
            'descripcion': dto.descripcion,
            'precio': dto.precio,
            'stock': dto.stock,
            'fecha_vencimiento': dto.fecha_vencimiento.isoformat(),
            'categoria': dto.categoria,
            'proveedor': dto.proveedor,
            'categoria_id': dto.categoria_id
        }

class MapeadorProducto:
    def entidad_a_dto(self, entidad: Producto) -> ProductoDTO:
        """Convierte entidad Producto a ProductoDTO"""
        return ProductoDTO(
            id=entidad.id,
            nombre=entidad.nombre.nombre,
            descripcion=entidad.descripcion.descripcion,
            precio=entidad.precio.precio,
            stock=entidad.stock.stock,
            fecha_vencimiento=entidad.fecha_vencimiento.fecha,
            categoria=entidad.categoria.nombre,
            proveedor=entidad.proveedor.nombre,
            categoria_id=entidad.categoria_id
        )
    
    def dto_a_entidad(self, dto: ProductoDTO) -> Producto:
        """Convierte ProductoDTO a entidad Producto"""
        return Producto(
            id=dto.id,
            nombre=Nombre(dto.nombre),
            descripcion=Descripcion(dto.descripcion),
            precio=Precio(dto.precio),
            stock=Stock(dto.stock),
            fecha_vencimiento=FechaVencimiento(dto.fecha_vencimiento),
            categoria=Categoria(dto.categoria),
            proveedor=Proveedor(dto.proveedor, "", ""),
            categoria_id=dto.categoria_id
        )

