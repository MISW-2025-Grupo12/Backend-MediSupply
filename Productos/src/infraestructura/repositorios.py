from config.db import db
from infraestructura.modelos import ProductoModel, CategoriaModel
from aplicacion.dto import ProductoDTO, CategoriaDTO
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
            categoria_id=producto_dto.categoria_id,
            proveedor_id=producto_dto.proveedor_id
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
            categoria_id=producto_model.categoria_id,
            proveedor_id=producto_model.proveedor_id
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
                categoria_id=producto_model.categoria_id,
                proveedor_id=producto_model.proveedor_id
            ))
        
        return productos_dto

class RepositorioCategoriaSQLite:
    def crear(self, categoria_dto: CategoriaDTO) -> CategoriaDTO:
        """Crear una nueva categoría en SQLite"""
        categoria_model = CategoriaModel(
            id=str(categoria_dto.id),
            nombre=categoria_dto.nombre,
            descripcion=categoria_dto.descripcion
        )
        
        db.session.add(categoria_model)
        db.session.commit()
        
        return categoria_dto
    
    def obtener_por_id(self, categoria_id: str) -> CategoriaDTO:
        """Obtener una categoría por ID"""
        categoria_model = CategoriaModel.query.get(categoria_id)
        if not categoria_model:
            return None
            
        return CategoriaDTO(
            id=uuid.UUID(categoria_model.id),
            nombre=categoria_model.nombre,
            descripcion=categoria_model.descripcion
        )
    
    def obtener_todos(self) -> list[CategoriaDTO]:
        """Obtener todas las categorías"""
        categorias_model = CategoriaModel.query.all()
        categorias_dto = []
        
        for categoria_model in categorias_model:
            categorias_dto.append(CategoriaDTO(
                id=uuid.UUID(categoria_model.id),
                nombre=categoria_model.nombre,
                descripcion=categoria_model.descripcion
            ))
        
        return categorias_dto
