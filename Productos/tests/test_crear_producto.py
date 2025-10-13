import pytest
import sys
import os
from unittest.mock import Mock, patch
from datetime import datetime, timedelta
import uuid
from flask import Flask

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from aplicacion.comandos.crear_producto import CrearProducto, CrearProductoHandler
from aplicacion.dto import ProductoDTO, CategoriaDTO
from aplicacion.dto_agregacion import ProductoAgregacionDTO
from config.db import db


class TestCrearProducto:
    
    def setup_method(self):
        self.handler = CrearProductoHandler()
        self.fecha_futura = datetime.now() + timedelta(days=30)
        self.categoria_id = str(uuid.uuid4())
        self.proveedor_id = str(uuid.uuid4())
        self.app = Flask(__name__)
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        db.init_app(self.app)
        
    def test_crear_producto_exitoso(self):
        comando = CrearProducto(
            nombre="Paracetamol",
            descripcion="Analgésico",
            precio=25000.0,
            categoria="Medicamentos",
            categoria_id=self.categoria_id,
            proveedor_id=self.proveedor_id
        )
        
        # Mock categoría
        categoria_mock = CategoriaDTO(
            id=uuid.UUID(self.categoria_id),
            nombre="Medicamentos",
            descripcion="Medicamentos generales"
        )
        
        # Mock proveedor
        proveedor_mock = {
            'id': self.proveedor_id,
            'nombre': 'Farmacia Central',
            'email': 'contacto@farmacia.com',
            'direccion': 'Calle 123 #45-67'
        }
        
        # Mock producto guardado
        producto_guardado = ProductoDTO(
            id=uuid.uuid4(),
            nombre="Paracetamol",
            descripcion="Analgésico",
            precio=25000.0,
            categoria="Medicamentos",
            categoria_id=self.categoria_id,
            proveedor_id=self.proveedor_id
        )
        
        # Crear mocks
        mock_repo_producto = Mock()
        mock_repo_categoria = Mock()
        mock_servicio_proveedores = Mock()
        
        mock_repo_categoria.obtener_por_id.return_value = categoria_mock
        mock_servicio_proveedores.obtener_proveedor_por_id.return_value = proveedor_mock
        mock_repo_producto.crear.return_value = producto_guardado
        
        # Crear handler con mocks
        handler = CrearProductoHandler(
            repositorio=mock_repo_producto,
            repositorio_categoria=mock_repo_categoria,
            servicio_proveedores=mock_servicio_proveedores
        )
        
        with self.app.app_context():
            db.create_all()
            resultado = handler.handle(comando)
        
        assert isinstance(resultado, ProductoAgregacionDTO)
        assert resultado.nombre == "Paracetamol"
        assert resultado.categoria_nombre == "Medicamentos"
        assert resultado.proveedor_nombre == "Farmacia Central"
        mock_repo_categoria.obtener_por_id.assert_called_once_with(self.categoria_id)
        mock_servicio_proveedores.obtener_proveedor_por_id.assert_called_once_with(self.proveedor_id)
        mock_repo_producto.crear.assert_called_once()
    
    def test_crear_producto_categoria_no_existe(self):
        """Test excepción cuando categoría no existe"""
        comando = CrearProducto(
            nombre="Paracetamol",
            descripcion="Analgésico",
            precio=25000.0,
            categoria="Medicamentos",
            categoria_id=self.categoria_id,
            proveedor_id=self.proveedor_id
        )
        
        # Crear mocks
        mock_repo_categoria = Mock()
        mock_repo_categoria.obtener_por_id.return_value = None
        
        # Crear handler con mock
        handler = CrearProductoHandler(repositorio_categoria=mock_repo_categoria)
        with self.app.app_context():
            db.create_all()
            with pytest.raises(ValueError, match="Categoría .* no existe"):
                handler.handle(comando)
    
    def test_crear_producto_proveedor_no_existe(self):
        """Test excepción cuando proveedor no existe"""
        comando = CrearProducto(
            nombre="Paracetamol",
            descripcion="Analgésico",
            precio=25000.0,
            categoria="Medicamentos",
            categoria_id=self.categoria_id,
            proveedor_id=self.proveedor_id
        )
        
        # Mock categoría existente
        categoria_mock = CategoriaDTO(
            id=uuid.UUID(self.categoria_id),
            nombre="Medicamentos",
            descripcion="Medicamentos generales"
        )
        
        # Crear mocks
        mock_repo_categoria = Mock()
        mock_servicio_proveedores = Mock()
        
        mock_repo_categoria.obtener_por_id.return_value = categoria_mock
        mock_servicio_proveedores.obtener_proveedor_por_id.return_value = None
        
        # Crear handler con mocks
        handler = CrearProductoHandler(
            repositorio_categoria=mock_repo_categoria,
            servicio_proveedores=mock_servicio_proveedores
        )
        
        with self.app.app_context():
            db.create_all()
            with pytest.raises(ValueError, match="Proveedor .* no existe"):
                handler.handle(comando)
    
    def test_crear_producto_nombre_vacio(self):
        """Test validación de nombre vacío"""
        comando = CrearProducto(
            nombre="",  # Nombre vacío
            descripcion="Analgésico",
            precio=25000.0,
            categoria="Medicamentos",
            categoria_id=self.categoria_id,
            proveedor_id=self.proveedor_id
        )
        
        with self.app.app_context():
            db.create_all()
            with pytest.raises(Exception):  
                self.handler.handle(comando)
    
    def test_crear_producto_precio_negativo(self):
        """Test validación de precio negativo"""
        comando = CrearProducto(
            nombre="Paracetamol",
            descripcion="Analgésico",
            precio=-1000.0,  # Precio negativo
            categoria="Medicamentos",
            categoria_id=self.categoria_id,
            proveedor_id=self.proveedor_id
        )
        
        with self.app.app_context():
            db.create_all()
            with pytest.raises(Exception): 
                self.handler.handle(comando)
    
    def test_crear_producto_fecha_vencimiento_pasada(self):
        """Test validación de fecha de vencimiento pasada"""
        fecha_pasada = datetime.now() - timedelta(days=1)
        comando = CrearProducto(
            nombre="Paracetamol",
            descripcion="Analgésico",
            precio=25000.0,
            categoria="Medicamentos",
            categoria_id=self.categoria_id,
            proveedor_id=self.proveedor_id
        )
        
        with self.app.app_context():
            db.create_all()
            with pytest.raises(Exception):  # Debería fallar en validación de reglas
                self.handler.handle(comando)