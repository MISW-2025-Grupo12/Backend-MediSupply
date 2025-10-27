import pytest
import sys
import os
import uuid
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from config.db import db
from infraestructura.repositorios import RepositorioProveedorSQLite
from aplicacion.dto import ProveedorDTO


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
    
    def test_crear_proveedor_en_db(self):
        proveedor_dto = ProveedorDTO(
            id=uuid.uuid4(),
            nombre="Farmacia Central",
            email="contacto@farmacia.com",
            direccion="Calle 123 #45-67",
            identificacion="9001234567",
            telefono="3001234567"
        )
        
        repositorio = RepositorioProveedorSQLite()
        
        with self.app.app_context():
            resultado = repositorio.crear(proveedor_dto)
        
        assert resultado.nombre == "Farmacia Central"
        assert resultado.email == "contacto@farmacia.com"
        assert resultado.direccion == "Calle 123 #45-67"
    
    def test_obtener_proveedor_por_id(self):
        """Test obtener proveedor por ID"""
        # Arrange
        proveedor_id = uuid.uuid4()
        proveedor_dto = ProveedorDTO(
            id=proveedor_id,
            nombre="Droguería Norte",
            email="info@drogueria.com",
            direccion="Avenida 456 #78-90",
            identificacion="9009876543",
            telefono="3009876543"
        )
        
        repositorio = RepositorioProveedorSQLite()
        
        with self.app.app_context():
            # Crear proveedor
            repositorio.crear(proveedor_dto)
            # Obtener proveedor
            resultado = repositorio.obtener_por_id(str(proveedor_id))
        
        assert resultado is not None
        assert resultado.nombre == "Droguería Norte"
        assert resultado.email == "info@drogueria.com"
    
    def test_obtener_proveedor_por_id_no_existe(self):
        """Test obtener proveedor por ID que no existe"""
        # Arrange
        repositorio = RepositorioProveedorSQLite()
        proveedor_id_inexistente = str(uuid.uuid4())
        
        with self.app.app_context():
            resultado = repositorio.obtener_por_id(proveedor_id_inexistente)
        
        assert resultado is None
    
    def test_obtener_todos_proveedores(self):
        """Test obtener todos los proveedores"""
        # Arrange
        proveedores = [
            ProveedorDTO(
                id=uuid.uuid4(),
                nombre="Farmacia Central",
                email="contacto@farmacia.com",
                direccion="Calle 123 #45-67",
                identificacion="9001234567",
                telefono="3001234567"
            ),
            ProveedorDTO(
                id=uuid.uuid4(),
                nombre="Droguería Norte",
                email="info@drogueria.com",
                direccion="Avenida 456 #78-90",
                identificacion="9009876543",
                telefono="3009876543"
            )
        ]
        
        repositorio = RepositorioProveedorSQLite()
        
        with self.app.app_context():
            # Crear proveedores
            for proveedor in proveedores:
                repositorio.crear(proveedor)
            
            # Obtener todos
            resultado = repositorio.obtener_todos()
        
        assert len(resultado) == 2
        nombres = [p.nombre for p in resultado]
        assert "Farmacia Central" in nombres
        assert "Droguería Norte" in nombres
