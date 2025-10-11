import pytest
import sys
import os
from unittest.mock import Mock, patch
from flask import Flask

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from aplicacion.consultas.obtener_producto_por_id import ObtenerProductoPorIdHandler, ObtenerProductoPorId
from aplicacion.dto_agregacion import ProductoAgregacionDTO


class TestObtenerProductoPorId:
    """Test para obtener producto por ID"""
    
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
    
    def test_obtener_producto_por_id_exitoso(self):
        """Test obtener producto por ID exitoso"""
        # Arrange
        producto_id = "123e4567-e89b-12d3-a456-426614174000"
        mock_producto = Mock()
        mock_producto.id = producto_id
        mock_producto.nombre = "Paracetamol"
        mock_producto.descripcion = "Analgésico"
        mock_producto.precio = 25000.0
        mock_producto.categoria_id = "456e7890-e89b-12d3-a456-426614174001"
        
        mock_categoria = Mock()
        mock_categoria.id = "456e7890-e89b-12d3-a456-426614174001"
        mock_categoria.nombre = "Medicamentos"
        mock_categoria.descripcion = "Medicamentos generales"
        
        mock_proveedor = {
            'id': "789e0123-e89b-12d3-a456-426614174002",
            'nombre': "Farmacia Central",
            'email': "contacto@farmacia.com",
            'direccion': "Calle 123 #45-67"
        }
        
        with patch('aplicacion.consultas.obtener_producto_por_id.RepositorioProductoSQLite') as mock_repo_class, \
             patch('aplicacion.consultas.obtener_producto_por_id.RepositorioCategoriaSQLite') as mock_cat_class, \
             patch('aplicacion.consultas.obtener_producto_por_id.ServicioProveedores') as mock_serv_class:
            
            mock_repo = Mock()
            mock_repo_class.return_value = mock_repo
            mock_repo.obtener_por_id.return_value = mock_producto
            
            mock_cat_repo = Mock()
            mock_cat_class.return_value = mock_cat_repo
            mock_cat_repo.obtener_por_id.return_value = mock_categoria
            
            mock_serv = Mock()
            mock_serv_class.return_value = mock_serv
            mock_serv.obtener_proveedor_por_id.return_value = mock_proveedor
            
            handler = ObtenerProductoPorIdHandler()
            
            # Act
            consulta = ObtenerProductoPorId(producto_id=producto_id)
            resultado = handler.handle(consulta)
            
            # Assert
            assert resultado is not None
            assert resultado['id'] == producto_id
            assert resultado['nombre'] == "Paracetamol"
            assert resultado['descripcion'] == "Analgésico"
            assert resultado['precio'] == 25000.0
            mock_repo.obtener_por_id.assert_called_once_with(producto_id)
    
    def test_obtener_producto_por_id_no_existe(self):
        """Test obtener producto por ID que no existe"""
        # Arrange
        producto_id = "123e4567-e89b-12d3-a456-426614174000"
        
        with patch('aplicacion.consultas.obtener_producto_por_id.RepositorioProductoSQLite') as mock_repo_class:
            mock_repo = Mock()
            mock_repo_class.return_value = mock_repo
            mock_repo.obtener_por_id.return_value = None
            
            handler = ObtenerProductoPorIdHandler()
            
            # Act
            consulta = ObtenerProductoPorId(producto_id=producto_id)
            resultado = handler.handle(consulta)
            
            # Assert
            assert resultado is None
            mock_repo.obtener_por_id.assert_called_once_with(producto_id)
    
    def test_obtener_producto_por_id_error(self):
        """Test obtener producto por ID con error"""
        # Arrange
        producto_id = "123e4567-e89b-12d3-a456-426614174000"
        
        with patch('aplicacion.consultas.obtener_producto_por_id.RepositorioProductoSQLite') as mock_repo_class:
            mock_repo = Mock()
            mock_repo_class.return_value = mock_repo
            mock_repo.obtener_por_id.side_effect = Exception("Error de base de datos")
            
            handler = ObtenerProductoPorIdHandler()
            
            # Act
            consulta = ObtenerProductoPorId(producto_id=producto_id)
            resultado = handler.handle(consulta)
            
            # Assert - El handler maneja la excepción y retorna None
            assert resultado is None
    
    def test_obtener_producto_por_id_con_repositorio_personalizado(self):
        """Test obtener producto por ID con repositorio personalizado"""
        # Arrange
        producto_id = "123e4567-e89b-12d3-a456-426614174000"
        mock_repo = Mock()
        mock_repo.obtener_por_id.return_value = None
        
        handler = ObtenerProductoPorIdHandler(repositorio=mock_repo)
        
        # Act
        consulta = ObtenerProductoPorId(producto_id=producto_id)
        resultado = handler.handle(consulta)
        
        # Assert
        assert resultado is None
        mock_repo.obtener_por_id.assert_called_once_with(producto_id)