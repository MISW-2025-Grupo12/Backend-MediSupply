import pytest
import sys
import os
from unittest.mock import Mock, patch
from flask import Flask
import uuid

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from infraestructura.repositorios import RepositorioVendedorSQLite
from aplicacion.dto import VendedorDTO


class TestRepositorioVendedor:
    """Test para repositorio de vendedor"""
    
    def setup_method(self):
        self.app = Flask(__name__)
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        self.app.config['TESTING'] = True
        from config.db import db
        self.db = db
        self.db.init_app(self.app)
        with self.app.app_context():
            self.db.create_all()
        self.client = self.app.test_client()
    
    def teardown_method(self):
        if self.app and self.db:
            with self.app.app_context():
                self.db.session.rollback()
                self.db.drop_all()
    
    def test_crear_vendedor_en_db(self):
        """Test crear vendedor en base de datos"""
        # Arrange
        vendedor_dto = VendedorDTO(
            id=uuid.uuid4(),
            nombre="María García",
            email="maria@email.com",
            telefono="0987654321",
            direccion="Avenida 456 #78-90"
        )
        
        repositorio = RepositorioVendedorSQLite()
        
        with self.app.app_context():
            # Act
            resultado = repositorio.crear(vendedor_dto)
            
            # Assert
            assert resultado is not None
            assert resultado.nombre == "María García"
            assert resultado.email == "maria@email.com"
    
    def test_obtener_vendedor_por_id(self):
        """Test obtener vendedor por ID"""
        # Arrange
        vendedor_id = uuid.uuid4()
        vendedor_dto = VendedorDTO(
            id=vendedor_id,
            nombre="María García",
            email="maria@email.com",
            telefono="0987654321",
            direccion="Avenida 456 #78-90"
        )
        
        repositorio = RepositorioVendedorSQLite()
        
        with self.app.app_context():
            # Crear vendedor
            repositorio.crear(vendedor_dto)
            
            # Act
            resultado = repositorio.obtener_por_id(str(vendedor_id))
            
            # Assert
            assert resultado is not None
            assert resultado.id == vendedor_id
            assert resultado.nombre == "María García"
    
    def test_obtener_vendedor_por_id_no_existe(self):
        """Test obtener vendedor por ID que no existe"""
        # Arrange
        vendedor_id = str(uuid.uuid4())
        repositorio = RepositorioVendedorSQLite()
        
        with self.app.app_context():
            # Act
            resultado = repositorio.obtener_por_id(vendedor_id)
            
            # Assert
            assert resultado is None
    
    def test_obtener_todos_vendedores(self):
        """Test obtener todos los vendedores"""
        # Arrange
        vendedores = [
            VendedorDTO(
                id=uuid.uuid4(),
                nombre="María García",
                email="maria@email.com",
                telefono="0987654321",
                direccion="Avenida 456 #78-90"
            ),
            VendedorDTO(
                id=uuid.uuid4(),
                nombre="Carlos Ruiz",
                email="carlos@email.com",
                telefono="1122334455",
                direccion="Carrera 789 #12-34"
            )
        ]
        
        repositorio = RepositorioVendedorSQLite()
        
        with self.app.app_context():
            # Crear vendedores
            for vendedor in vendedores:
                repositorio.crear(vendedor)
            
            # Act
            resultado = repositorio.obtener_todos()
            
            # Assert
            assert resultado is not None
            assert len(resultado) == 2
            assert any(v.nombre == "María García" for v in resultado)
            assert any(v.nombre == "Carlos Ruiz" for v in resultado)
    
    def test_obtener_todos_vendedores_vacio(self):
        """Test obtener todos los vendedores cuando no hay vendedores"""
        # Arrange
        repositorio = RepositorioVendedorSQLite()
        
        with self.app.app_context():
            # Act
            resultado = repositorio.obtener_todos()
            
            # Assert
            assert resultado is not None
            assert len(resultado) == 0
