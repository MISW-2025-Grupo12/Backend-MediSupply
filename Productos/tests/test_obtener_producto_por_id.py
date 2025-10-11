import pytest
import sys
import os
from unittest.mock import Mock, patch
from flask import Flask

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from aplicacion.consultas.obtener_producto_por_id import ObtenerProductoPorIdHandler
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
        mock_producto = ProductoAgregacionDTO(
            id=producto_id,
            nombre="Paracetamol",
            descripcion="Analgésico",
            precio=25000.0,
            categoria_id="456e7890-e89b-12d3-a456-426614174001",
            categoria_nombre="Medicamentos",
            categoria_descripcion="Medicamentos generales",
            proveedor_id="789e0123-e89b-12d3-a456-426614174002",
            proveedor_nombre="Farmacia Central",
            proveedor_email="contacto@farmacia.com",
            proveedor_direccion="Calle 123 #45-67"
        )
        
        with patch('aplicacion.consultas.obtener_producto_por_id.RepositorioProductoSQLite') as mock_repo_class:
            mock_repo = Mock()
            mock_repo_class.return_value = mock_repo
            mock_repo.obtener_por_id.return_value = mock_producto
            
            handler = ObtenerProductoPorIdHandler()
            
            # Act
            resultado = handler.handle(producto_id)
            
            # Assert
            assert resultado is not None
            assert resultado.id == producto_id
            assert resultado.nombre == "Paracetamol"
            assert resultado.descripcion == "Analgésico"
            assert resultado.precio == 25000.0
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
            resultado = handler.handle(producto_id)
            
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
            
            # Act & Assert
            with pytest.raises(Exception, match="Error de base de datos"):
                handler.handle(producto_id)
    
    def test_obtener_producto_por_id_con_repositorio_personalizado(self):
        """Test obtener producto por ID con repositorio personalizado"""
        # Arrange
        producto_id = "123e4567-e89b-12d3-a456-426614174000"
        mock_repo = Mock()
        mock_repo.obtener_por_id.return_value = None
        
        handler = ObtenerProductoPorIdHandler(repositorio=mock_repo)
        
        # Act
        resultado = handler.handle(producto_id)
        
        # Assert
        assert resultado is None
        mock_repo.obtener_por_id.assert_called_once_with(producto_id)