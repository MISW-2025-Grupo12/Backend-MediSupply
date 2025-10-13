import pytest
import sys
import os
from unittest.mock import Mock, patch
import uuid
from flask import Flask

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from aplicacion.consultas.obtener_productos import ObtenerProductos, ObtenerProductosHandler
from aplicacion.dto import ProductoDTO, CategoriaDTO
from aplicacion.dto_agregacion import ProductoAgregacionDTO
from config.db import db


class TestObtenerProductos:
    
    def setup_method(self):
        """Setup para cada test"""
        self.handler = ObtenerProductosHandler()
        self.categoria_id = str(uuid.uuid4())
        self.proveedor_id = str(uuid.uuid4())

        self.app = Flask(__name__)
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        db.init_app(self.app)
    
    def test_obtener_productos_exitoso(self):
        """Test obtener productos exitoso con agregación completa"""
        # Arrange
        consulta = ObtenerProductos()
        
        # Mock productos
        productos = [
            ProductoDTO(
                id=uuid.uuid4(),
                nombre="Paracetamol",
                descripcion="Analgésico",
                precio=25000.0,
                categoria="Medicamentos",
                categoria_id=self.categoria_id,
                proveedor_id=self.proveedor_id
            )
        ]
        
        # Mock categoría
        categoria = CategoriaDTO(
            id=uuid.UUID(self.categoria_id),
            nombre="Medicamentos",
            descripcion="Medicamentos generales"
        )
        
        # Mock proveedor
        proveedor = {
            'id': self.proveedor_id,
            'nombre': 'Farmacia Central',
            'email': 'contacto@farmacia.com',
            'direccion': 'Calle 123 #45-67'
        }
        
        # Crear mocks
        mock_repo_producto = Mock()
        mock_repo_categoria = Mock()
        mock_servicio_proveedores = Mock()
        
        mock_repo_producto.obtener_todos.return_value = productos
        mock_repo_categoria.obtener_por_id.return_value = categoria
        mock_servicio_proveedores.obtener_proveedor_por_id.return_value = proveedor
        
        # Crear handler con mocks
        handler = ObtenerProductosHandler(
            repositorio=mock_repo_producto,
            repositorio_categoria=mock_repo_categoria,
            servicio_proveedores=mock_servicio_proveedores
        )
        
        # Act
        with self.app.app_context():
            db.create_all()
            resultado = handler.handle(consulta)
        
        # Assert
        assert isinstance(resultado, list)
        assert len(resultado) == 1
        assert isinstance(resultado[0], ProductoAgregacionDTO)
        assert resultado[0].nombre == "Paracetamol"
        assert resultado[0].categoria_nombre == "Medicamentos"
        assert resultado[0].proveedor_nombre == "Farmacia Central"
    
    def test_obtener_productos_vacio(self):
        """Test obtener productos cuando no hay productos"""
        # Arrange
        consulta = ObtenerProductos()
        
        # Crear mock del repositorio
        mock_repo_producto = Mock()
        mock_repo_producto.obtener_todos.return_value = []
        
        # Crear handler con mock
        handler = ObtenerProductosHandler(repositorio=mock_repo_producto)
        
        # Act
        with self.app.app_context():
            db.create_all()
            resultado = handler.handle(consulta)
        
        # Assert
        assert isinstance(resultado, list)
        assert len(resultado) == 0
    
    @patch('aplicacion.consultas.obtener_productos.ServicioProveedores')
    @patch('aplicacion.consultas.obtener_productos.RepositorioCategoriaSQLite')
    @patch('aplicacion.consultas.obtener_productos.RepositorioProductoSQLite')
    def test_obtener_productos_con_categoria_no_encontrada(self, mock_repo_producto, mock_repo_categoria, mock_servicio_proveedores):
        """Test que skip productos con categoría inexistente"""
        # Arrange
        consulta = ObtenerProductos()
        
        # Mock productos
        productos = [
            ProductoDTO(
                id=uuid.uuid4(),
                nombre="Paracetamol",
                descripcion="Analgésico",
                precio=25000.0,
                categoria="Medicamentos",
                categoria_id=self.categoria_id,
                proveedor_id=self.proveedor_id
            )
        ]
        mock_repo_producto.return_value.obtener_todos.return_value = productos
        
        # Mock categoría no encontrada
        mock_repo_categoria.return_value.obtener_por_id.return_value = None
        
        # Act
        with self.app.app_context():
            db.create_all()
            resultado = self.handler.handle(consulta)
        
        # Assert
        assert isinstance(resultado, list)
        assert len(resultado) == 0  # Debería estar vacío porque se skip el producto
    
    @patch('aplicacion.consultas.obtener_productos.ServicioProveedores')
    @patch('aplicacion.consultas.obtener_productos.RepositorioCategoriaSQLite')
    @patch('aplicacion.consultas.obtener_productos.RepositorioProductoSQLite')
    def test_obtener_productos_con_proveedor_no_encontrado(self, mock_repo_producto, mock_repo_categoria, mock_servicio_proveedores):
        """Test que skip productos con proveedor inexistente"""
        # Arrange
        consulta = ObtenerProductos()
        
        # Mock productos
        productos = [
            ProductoDTO(
                id=uuid.uuid4(),
                nombre="Paracetamol",
                descripcion="Analgésico",
                precio=25000.0,
                categoria="Medicamentos",
                categoria_id=self.categoria_id,
                proveedor_id=self.proveedor_id
            )
        ]
        mock_repo_producto.return_value.obtener_todos.return_value = productos
        
        # Mock categoría existente
        categoria = CategoriaDTO(
            id=uuid.UUID(self.categoria_id),
            nombre="Medicamentos",
            descripcion="Medicamentos generales"
        )
        mock_repo_categoria.return_value.obtener_por_id.return_value = categoria
        
        # Mock proveedor no encontrado
        mock_servicio_proveedores.return_value.obtener_proveedor_por_id.return_value = None
        
        # Act
        with self.app.app_context():
            db.create_all()
            resultado = self.handler.handle(consulta)
        
        # Assert
        assert isinstance(resultado, list)
        assert len(resultado) == 0  # Debería estar vacío porque se skip el producto