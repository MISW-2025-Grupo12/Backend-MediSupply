import pytest
import sys
import os
import uuid
from datetime import datetime, timedelta
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from config.db import db
from infraestructura.repositorios import RepositorioProductoSQLite, RepositorioCategoriaSQLite
from aplicacion.dto import ProductoDTO, CategoriaDTO


class TestRepositorios:
    
    @pytest.fixture(autouse=True)
    def setup_db(self):
        self.app = Flask(__name__)
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        
        db.init_app(self.app)
        
        with self.app.app_context():
            db.create_all()
            yield
            db.drop_all()
    
    def test_crear_producto_en_db(self):
        fecha_futura = datetime.now() + timedelta(days=30)
        producto_dto = ProductoDTO(
            id=uuid.uuid4(),
            nombre="Paracetamol",
            descripcion="Analgésico",
            precio=25000.0,
            categoria="Medicamentos",
            categoria_id=str(uuid.uuid4()),
            proveedor_id=str(uuid.uuid4())
        )
        
        repositorio = RepositorioProductoSQLite()
        
        with self.app.app_context():
            resultado = repositorio.crear(producto_dto)
        
        assert resultado.nombre == "Paracetamol"
        assert resultado.precio == 25000.0
    
    def test_obtener_producto_por_id(self):
        """Test obtener producto por ID"""
        # Arrange
        fecha_futura = datetime.now() + timedelta(days=30)
        producto_id = uuid.uuid4()
        producto_dto = ProductoDTO(
            id=producto_id,
            nombre="Ibuprofeno",
            descripcion="Antiinflamatorio",
            precio=15000.0,
            categoria="Medicamentos",
            categoria_id=str(uuid.uuid4()),
            proveedor_id=str(uuid.uuid4())
        )
        
        repositorio = RepositorioProductoSQLite()
        
        with self.app.app_context():
            # Crear producto
            repositorio.crear(producto_dto)
            # Obtener producto
            resultado = repositorio.obtener_por_id(str(producto_id))
        
        assert resultado is not None
        assert resultado.nombre == "Ibuprofeno"
        assert resultado.precio == 15000.0
    
    def test_obtener_producto_por_id_no_existe(self):
        """Test obtener producto por ID que no existe"""
        # Arrange
        repositorio = RepositorioProductoSQLite()
        producto_id_inexistente = str(uuid.uuid4())
        
        with self.app.app_context():
            resultado = repositorio.obtener_por_id(producto_id_inexistente)
        
        assert resultado is None
    
    def test_obtener_todos_productos(self):
        """Test obtener todos los productos"""
        # Arrange
        fecha_futura = datetime.now() + timedelta(days=30)
        productos = [
            ProductoDTO(
                id=uuid.uuid4(),
                nombre="Paracetamol",
                descripcion="Analgésico",
                precio=25000.0,
                categoria="Medicamentos",
                categoria_id=str(uuid.uuid4()),
                proveedor_id=str(uuid.uuid4())
            ),
            ProductoDTO(
                id=uuid.uuid4(),
                nombre="Ibuprofeno",
                descripcion="Antiinflamatorio",
                precio=15000.0,
                categoria="Medicamentos",
                categoria_id=str(uuid.uuid4()),
                proveedor_id=str(uuid.uuid4())
            )
        ]
        
        repositorio = RepositorioProductoSQLite()
        
        with self.app.app_context():
            # Crear productos
            for producto in productos:
                repositorio.crear(producto)
            
            # Obtener todos
            resultado = repositorio.obtener_todos()
        
        assert len(resultado) == 2
        nombres = [p.nombre for p in resultado]
        assert "Paracetamol" in nombres
        assert "Ibuprofeno" in nombres
    
    def test_crear_categoria_en_db(self):
        """Test crear categoría en base de datos"""
        # Arrange
        categoria_dto = CategoriaDTO(
            id=uuid.uuid4(),
            nombre="Medicamentos",
            descripcion="Medicamentos generales"
        )
        
        repositorio = RepositorioCategoriaSQLite()
        
        with self.app.app_context():
            resultado = repositorio.crear(categoria_dto)
        
        assert resultado.nombre == "Medicamentos"
        assert resultado.descripcion == "Medicamentos generales"
    
    def test_obtener_categoria_por_id(self):
        """Test obtener categoría por ID"""
        # Arrange
        categoria_id = uuid.uuid4()
        categoria_dto = CategoriaDTO(
            id=categoria_id,
            nombre="Suplementos",
            descripcion="Suplementos vitamínicos"
        )
        
        repositorio = RepositorioCategoriaSQLite()
        
        with self.app.app_context():
            # Crear categoría
            repositorio.crear(categoria_dto)
            # Obtener categoría
            resultado = repositorio.obtener_por_id(str(categoria_id))
        
        assert resultado is not None
        assert resultado.nombre == "Suplementos"
        assert resultado.descripcion == "Suplementos vitamínicos"
    
    def test_obtener_categoria_por_id_no_existe(self):
        """Test obtener categoría por ID que no existe"""
        # Arrange
        repositorio = RepositorioCategoriaSQLite()
        categoria_id_inexistente = str(uuid.uuid4())
        
        with self.app.app_context():
            resultado = repositorio.obtener_por_id(categoria_id_inexistente)
        
        assert resultado is None
    
    def test_obtener_todas_categorias(self):
        """Test obtener todas las categorías"""
        # Arrange
        categorias = [
            CategoriaDTO(
                id=uuid.uuid4(),
                nombre="Medicamentos",
                descripcion="Medicamentos generales"
            ),
            CategoriaDTO(
                id=uuid.uuid4(),
                nombre="Suplementos",
                descripcion="Suplementos vitamínicos"
            )
        ]
        
        repositorio = RepositorioCategoriaSQLite()
        
        with self.app.app_context():
            # Crear categorías
            for categoria in categorias:
                repositorio.crear(categoria)
            
            # Obtener todas
            resultado = repositorio.obtener_todos()
        
        assert len(resultado) == 2
        nombres = [c.nombre for c in resultado]
        assert "Medicamentos" in nombres
        assert "Suplementos" in nombres
