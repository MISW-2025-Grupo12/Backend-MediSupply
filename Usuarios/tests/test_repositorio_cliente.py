import pytest
import sys
import os
from unittest.mock import Mock, patch
from flask import Flask
import uuid

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from infraestructura.repositorios import RepositorioClienteSQLite
from aplicacion.dto import ClienteDTO


class TestRepositorioCliente:
    """Test para repositorio de cliente"""
    
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
    
    def test_crear_cliente_en_db(self):
        """Test crear cliente en base de datos"""
        # Arrange
        cliente_dto = ClienteDTO(
            id=uuid.uuid4(),
            nombre="Juan Pérez",
            email="juan@email.com",
            telefono="1234567890",
            direccion="Calle 123 #45-67"
        )
        
        repositorio = RepositorioClienteSQLite()
        
        with self.app.app_context():
            # Act
            resultado = repositorio.crear(cliente_dto)
            
            # Assert
            assert resultado is not None
            assert resultado.nombre == "Juan Pérez"
            assert resultado.email == "juan@email.com"
    
    def test_obtener_cliente_por_id(self):
        """Test obtener cliente por ID"""
        # Arrange
        cliente_id = uuid.uuid4()
        cliente_dto = ClienteDTO(
            id=cliente_id,
            nombre="Juan Pérez",
            email="juan@email.com",
            telefono="1234567890",
            direccion="Calle 123 #45-67"
        )
        
        repositorio = RepositorioClienteSQLite()
        
        with self.app.app_context():
            # Crear cliente
            repositorio.crear(cliente_dto)
            
            # Act
            resultado = repositorio.obtener_por_id(str(cliente_id))
            
            # Assert
            assert resultado is not None
            assert resultado.id == cliente_id
            assert resultado.nombre == "Juan Pérez"
    
    def test_obtener_cliente_por_id_no_existe(self):
        """Test obtener cliente por ID que no existe"""
        # Arrange
        cliente_id = str(uuid.uuid4())
        repositorio = RepositorioClienteSQLite()
        
        with self.app.app_context():
            # Act
            resultado = repositorio.obtener_por_id(cliente_id)
            
            # Assert
            assert resultado is None
    
    def test_obtener_todos_clientes(self):
        """Test obtener todos los clientes"""
        # Arrange
        clientes = [
            ClienteDTO(
                id=uuid.uuid4(),
                nombre="Juan Pérez",
                email="juan@email.com",
                telefono="1234567890",
                direccion="Calle 123 #45-67"
            ),
            ClienteDTO(
                id=uuid.uuid4(),
                nombre="Ana López",
                email="ana@email.com",
                telefono="0987654321",
                direccion="Avenida 456 #78-90"
            )
        ]
        
        repositorio = RepositorioClienteSQLite()
        
        with self.app.app_context():
            # Crear clientes
            for cliente in clientes:
                repositorio.crear(cliente)
            
            # Act
            resultado = repositorio.obtener_todos()
            
            # Assert
            assert resultado is not None
            assert len(resultado) == 2
            assert any(c.nombre == "Juan Pérez" for c in resultado)
            assert any(c.nombre == "Ana López" for c in resultado)
    
    def test_obtener_todos_clientes_vacio(self):
        """Test obtener todos los clientes cuando no hay clientes"""
        # Arrange
        repositorio = RepositorioClienteSQLite()
        
        with self.app.app_context():
            # Act
            resultado = repositorio.obtener_todos()
            
            # Assert
            assert resultado is not None
            assert len(resultado) == 0
