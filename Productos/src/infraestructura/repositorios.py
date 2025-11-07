from config.db import db
from infraestructura.modelos import ProductoModel, CategoriaModel, CargaMasivaJobModel
from aplicacion.dto import ProductoDTO, CategoriaDTO, CargaMasivaJobDTO
from datetime import datetime
import uuid
import re
import logging

logger = logging.getLogger(__name__)

class RepositorioProductoSQLite:
    def crear(self, producto_dto: ProductoDTO) -> ProductoDTO:
        """Crear un nuevo producto en SQLite"""
        producto_model = ProductoModel(
            id=str(producto_dto.id),
            nombre=producto_dto.nombre,
            descripcion=producto_dto.descripcion,
            precio=producto_dto.precio,
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
                categoria=producto_model.categoria,
                categoria_id=producto_model.categoria_id,
                proveedor_id=producto_model.proveedor_id
            ))
        
        return productos_dto
    
    def obtener_por_nombre(self, nombre: str) -> ProductoDTO:
        """Obtener un producto por nombre (comparación normalizada)"""
        nombre_normalizado = self._normalizar_nombre(nombre)
        productos = ProductoModel.query.all()
        
        for producto_model in productos:
            if self._normalizar_nombre(producto_model.nombre) == nombre_normalizado:
                return ProductoDTO(
                    id=uuid.UUID(producto_model.id),
                    nombre=producto_model.nombre,
                    descripcion=producto_model.descripcion,
                    precio=producto_model.precio,
                    categoria=producto_model.categoria,
                    categoria_id=producto_model.categoria_id,
                    proveedor_id=producto_model.proveedor_id
                )
        
        return None
    
    def actualizar(self, producto_dto: ProductoDTO) -> ProductoDTO:
        """Actualizar un producto existente"""
        producto_model = ProductoModel.query.get(str(producto_dto.id))
        if not producto_model:
            raise ValueError(f"Producto {producto_dto.id} no encontrado")
        
        producto_model.nombre = producto_dto.nombre
        producto_model.descripcion = producto_dto.descripcion
        producto_model.precio = producto_dto.precio
        producto_model.categoria = producto_dto.categoria
        producto_model.categoria_id = producto_dto.categoria_id
        producto_model.proveedor_id = producto_dto.proveedor_id
        producto_model.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return producto_dto
    
    def _normalizar_nombre(self, nombre: str) -> str:
        """Normaliza un nombre para comparación: lowercase y sin espacios"""
        if not nombre:
            return ""
        return re.sub(r'\s+', '', nombre.lower().strip())

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
    
    def obtener_por_nombre(self, nombre: str) -> CategoriaDTO:
        """Obtener una categoría por nombre (comparación normalizada)"""
        nombre_normalizado = self._normalizar_nombre(nombre)
        categorias = CategoriaModel.query.all()
        
        for categoria_model in categorias:
            if self._normalizar_nombre(categoria_model.nombre) == nombre_normalizado:
                return CategoriaDTO(
                    id=uuid.UUID(categoria_model.id),
                    nombre=categoria_model.nombre,
                    descripcion=categoria_model.descripcion
                )
        
        return None
    
    def _normalizar_nombre(self, nombre: str) -> str:
        """Normaliza un nombre para comparación: lowercase y sin espacios"""
        if not nombre:
            return ""
        return re.sub(r'\s+', '', nombre.lower().strip())

class RepositorioJobSQLite:
    def crear(self, job_dto: CargaMasivaJobDTO) -> CargaMasivaJobDTO:
        """Crear un nuevo job en BD"""
        job_model = CargaMasivaJobModel(
            id=str(job_dto.id),
            status=job_dto.status,
            total_filas=job_dto.total_filas,
            filas_procesadas=job_dto.filas_procesadas,
            filas_exitosas=job_dto.filas_exitosas,
            filas_error=job_dto.filas_error,
            filas_rechazadas=job_dto.filas_rechazadas,
            result_url=job_dto.result_url,
            error=job_dto.error
        )
        
        db.session.add(job_model)
        db.session.commit()
        
        return job_dto
    
    def obtener_por_id(self, job_id: str) -> CargaMasivaJobDTO:
        """Obtener un job por ID"""
        job_model = CargaMasivaJobModel.query.get(job_id)
        if not job_model:
            return None
        
        return CargaMasivaJobDTO(
            id=uuid.UUID(job_model.id),
            status=job_model.status,
            total_filas=job_model.total_filas,
            filas_procesadas=job_model.filas_procesadas,
            filas_exitosas=job_model.filas_exitosas,
            filas_error=job_model.filas_error,
            filas_rechazadas=job_model.filas_rechazadas,
            result_url=job_model.result_url,
            error=job_model.error,
            created_at=job_model.created_at,
            updated_at=job_model.updated_at
        )
    
    def actualizar(self, job_dto: CargaMasivaJobDTO) -> CargaMasivaJobDTO:
        """Actualizar un job existente"""
        job_model = CargaMasivaJobModel.query.get(str(job_dto.id))
        if not job_model:
            raise ValueError(f"Job {job_dto.id} no encontrado")
        
        job_model.status = job_dto.status
        job_model.filas_procesadas = job_dto.filas_procesadas
        job_model.filas_exitosas = job_dto.filas_exitosas
        job_model.filas_error = job_dto.filas_error
        job_model.filas_rechazadas = job_dto.filas_rechazadas
        job_model.result_url = job_dto.result_url
        job_model.error = job_dto.error
        job_model.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return job_dto
    
    def obtener_pendientes(self, limit: int = 1) -> list[CargaMasivaJobDTO]:
        """Obtener jobs pendientes (para procesamiento) con bloqueo atómico"""
        try:
            # Obtener el primer job pendiente
            job_model = CargaMasivaJobModel.query.filter_by(status='pending').first()
            
            if not job_model:
                return []
            
            # Actualizar atómicamente a processing
            job_model.status = 'processing'
            job_model.updated_at = datetime.utcnow()
            db.session.commit()
            
            # Retornar como DTO
            job_dto = CargaMasivaJobDTO(
                id=uuid.UUID(job_model.id),
                status=job_model.status,
                total_filas=job_model.total_filas,
                filas_procesadas=job_model.filas_procesadas,
                filas_exitosas=job_model.filas_exitosas,
                filas_error=job_model.filas_error,
                filas_rechazadas=job_model.filas_rechazadas,
                result_url=job_model.result_url,
                error=job_model.error,
                created_at=job_model.created_at,
                updated_at=job_model.updated_at
            )
            
            return [job_dto]
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error obteniendo jobs pendientes: {e}")
            return []
    
    def obtener_todos(self, status: str = None, ordenar_por: str = 'created_at', orden: str = 'desc') -> list[CargaMasivaJobDTO]:
        """
        Obtener todos los jobs, opcionalmente filtrados por status
        Args:
            status: Filtrar por status (pending, processing, completed, failed). None para obtener todos.
            ordenar_por: Campo por el cual ordenar (created_at, updated_at, status). Default: 'created_at'
            orden: Orden de clasificación ('asc' o 'desc'). Default: 'desc'
        Returns:
            Lista de CargaMasivaJobDTO
        """
        try:
            query = CargaMasivaJobModel.query
            
            # Filtrar por status si se proporciona
            if status:
                query = query.filter_by(status=status)
            
            # Ordenar
            orden_attr = getattr(CargaMasivaJobModel, ordenar_por, CargaMasivaJobModel.created_at)
            if orden.lower() == 'asc':
                query = query.order_by(orden_attr.asc())
            else:
                query = query.order_by(orden_attr.desc())
            
            # Obtener todos los resultados
            job_models = query.all()
            
            # Convertir a DTOs
            jobs = []
            for job_model in job_models:
                porcentaje = (job_model.filas_procesadas / job_model.total_filas * 100) if job_model.total_filas > 0 else 0.0
                job_dto = CargaMasivaJobDTO(
                    id=uuid.UUID(job_model.id),
                    status=job_model.status,
                    total_filas=job_model.total_filas,
                    filas_procesadas=job_model.filas_procesadas,
                    filas_exitosas=job_model.filas_exitosas,
                    filas_error=job_model.filas_error,
                    filas_rechazadas=job_model.filas_rechazadas,
                    result_url=job_model.result_url,
                    error=job_model.error,
                    created_at=job_model.created_at,
                    updated_at=job_model.updated_at
                )
                jobs.append(job_dto)
            
            return jobs
            
        except Exception as e:
            logger.error(f"Error obteniendo todos los jobs: {e}")
            return []
