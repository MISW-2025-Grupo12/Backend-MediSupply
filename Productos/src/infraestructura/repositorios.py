from config.db import db
from infraestructura.modelos import ProductoModel
from aplicacion.dto import ProductoDTO
from datetime import datetime
import uuid

class RepositorioProductoSQLite:
    def crear(self, producto_dto: ProductoDTO) -> ProductoDTO:
        """Crear un nuevo producto en SQLite"""
        producto_model = ProductoModel(
            id=str(producto_dto.id),
            nombre=producto_dto.nombre,
            descripcion=producto_dto.descripcion,
            precio=producto_dto.precio,
            stock=producto_dto.stock,
            fecha_vencimiento=producto_dto.fecha_vencimiento,
            categoria=producto_dto.categoria,
            proveedor=producto_dto.proveedor,
            categoria_id=producto_dto.categoria_id
        )
        
        db.session.add(producto_model)
        db.session.commit()
        
        return producto_dto
    
    def obtener_por_id(self, producto_id: str) -> ProductoDTO:
        """Obtener un producto por ID"""
        producto_model = ProductoModel.query.get(producto_id)
        if not producto_model:
            return None
            
        return ProductoDTO(
            id=uuid.UUID(producto_model.id),
            nombre=producto_model.nombre,
            descripcion=producto_model.descripcion,
            precio=producto_model.precio,
            stock=producto_model.stock,
            fecha_vencimiento=producto_model.fecha_vencimiento,
            categoria=producto_model.categoria,
            proveedor=producto_model.proveedor,
            categoria_id=producto_model.categoria_id
        )
    
    def obtener_todos(self) -> list[ProductoDTO]:
        """Obtener todos los productos"""
        productos_model = ProductoModel.query.all()
        productos_dto = []
        
        for producto_model in productos_model:
            productos_dto.append(ProductoDTO(
                id=uuid.UUID(producto_model.id),
                nombre=producto_model.nombre,
                descripcion=producto_model.descripcion,
                precio=producto_model.precio,
                stock=producto_model.stock,
                fecha_vencimiento=producto_model.fecha_vencimiento,
                categoria=producto_model.categoria,
                proveedor=producto_model.proveedor,
                categoria_id=producto_model.categoria_id
            ))
        
        return productos_dto
