import pytest
import sys
import os
from unittest.mock import Mock, patch
from flask import Flask
import uuid

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from aplicacion.comandos.crear_producto_con_inventario import CrearProductoConInventario, CrearProductoConInventarioHandler
from aplicacion.dto_agregacion import ProductoAgregacionDTO
from aplicacion.dto import CategoriaDTO


class TestCrearProductoConInventario:
    """Test para crear producto con inventario"""
    
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
    
    def test_crear_producto_con_inventario_exitoso(self):
        """Test crear producto con inventario exitoso"""
        # Arrange
        comando = CrearProductoConInventario(
            nombre="Paracetamol",
            descripcion="Analgésico",
            precio=25000.0,
            stock=100,
            fecha_vencimiento="2024-12-31",
            categoria="Medicamentos",
            categoria_id="123e4567-e89b-12d3-a456-426614174000",
            proveedor_id="456e7890-e89b-12d3-a456-426614174001"
        )
        
        mock_categoria = CategoriaDTO(
            id="123e4567-e89b-12d3-a456-426614174000",
            nombre="Medicamentos",
            descripcion="Medicamentos generales"
        )
        
        mock_proveedor = {
            'id': '456e7890-e89b-12d3-a456-426614174001',
            'nombre': 'Farmacia Central',
            'email': 'contacto@farmacia.com',
            'direccion': 'Calle 123 #45-67'
        }
        
        with patch('aplicacion.comandos.crear_producto_con_inventario.RepositorioProductoSQLite') as mock_repo_class, \
             patch('aplicacion.comandos.crear_producto_con_inventario.RepositorioCategoriaSQLite') as mock_cat_repo_class, \
             patch('aplicacion.comandos.crear_producto_con_inventario.ServicioProveedores') as mock_prov_service_class, \
             patch('aplicacion.comandos.crear_producto_con_inventario.despachador_eventos') as mock_despachador:
            
            mock_repo = Mock()
            mock_repo_class.return_value = mock_repo
            mock_repo.crear.return_value = Mock(id=uuid.uuid4(), nombre="Paracetamol", descripcion="Analgésico", precio=25000.0)
            
            mock_cat_repo = Mock()
            mock_cat_repo_class.return_value = mock_cat_repo
            mock_cat_repo.obtener_por_id.return_value = mock_categoria
            
            mock_prov_service = Mock()
            mock_prov_service_class.return_value = mock_prov_service
            mock_prov_service.obtener_proveedor_por_id.return_value = mock_proveedor
            
            handler = CrearProductoConInventarioHandler()
            
            # Act
            resultado = handler.handle(comando)
            
            # Assert
            assert resultado is not None
            assert isinstance(resultado, ProductoAgregacionDTO)
            assert resultado.nombre == "Paracetamol"
            assert resultado.descripcion == "Analgésico"
            assert resultado.precio == 25000.0
            assert resultado.categoria_nombre == "Medicamentos"
            assert resultado.proveedor_nombre == "Farmacia Central"
            
            # Verificar que se llamaron los métodos correctos
            mock_cat_repo.obtener_por_id.assert_called_once_with(comando.categoria_id)
            mock_prov_service.obtener_proveedor_por_id.assert_called_once_with(comando.proveedor_id)
            mock_repo.crear.assert_called_once()
            
            # Verificar que se publicaron los eventos
            assert mock_despachador.publicar_evento.call_count == 2
    
    def test_crear_producto_con_inventario_categoria_no_existe(self):
        """Test crear producto con inventario cuando la categoría no existe"""
        # Arrange
        comando = CrearProductoConInventario(
            nombre="Paracetamol",
            descripcion="Analgésico",
            precio=25000.0,
            stock=100,
            fecha_vencimiento="2024-12-31",
            categoria="Medicamentos",
            categoria_id="123e4567-e89b-12d3-a456-426614174000",
            proveedor_id="456e7890-e89b-12d3-a456-426614174001"
        )
        
        with patch('aplicacion.comandos.crear_producto_con_inventario.RepositorioCategoriaSQLite') as mock_cat_repo_class:
            mock_cat_repo = Mock()
            mock_cat_repo_class.return_value = mock_cat_repo
            mock_cat_repo.obtener_por_id.return_value = None
            
            handler = CrearProductoConInventarioHandler()
            
            # Act & Assert
            with pytest.raises(ValueError, match="Categoría .* no existe"):
                handler.handle(comando)
    
    def test_crear_producto_con_inventario_proveedor_no_existe(self):
        """Test crear producto con inventario cuando el proveedor no existe"""
        # Arrange
        comando = CrearProductoConInventario(
            nombre="Paracetamol",
            descripcion="Analgésico",
            precio=25000.0,
            stock=100,
            fecha_vencimiento="2024-12-31",
            categoria="Medicamentos",
            categoria_id="123e4567-e89b-12d3-a456-426614174000",
            proveedor_id="456e7890-e89b-12d3-a456-426614174001"
        )
        
        mock_categoria = CategoriaDTO(
            id="123e4567-e89b-12d3-a456-426614174000",
            nombre="Medicamentos",
            descripcion="Medicamentos generales"
        )
        
        with patch('aplicacion.comandos.crear_producto_con_inventario.RepositorioCategoriaSQLite') as mock_cat_repo_class, \
             patch('aplicacion.comandos.crear_producto_con_inventario.ServicioProveedores') as mock_prov_service_class:
            
            mock_cat_repo = Mock()
            mock_cat_repo_class.return_value = mock_cat_repo
            mock_cat_repo.obtener_por_id.return_value = mock_categoria
            
            mock_prov_service = Mock()
            mock_prov_service_class.return_value = mock_prov_service
            mock_prov_service.obtener_proveedor_por_id.return_value = None
            
            handler = CrearProductoConInventarioHandler()
            
            # Act & Assert
            with pytest.raises(ValueError, match="Proveedor .* no existe"):
                handler.handle(comando)
    
    def test_crear_producto_con_inventario_error_general(self):
        """Test crear producto con inventario con error general"""
        # Arrange
        comando = CrearProductoConInventario(
            nombre="Paracetamol",
            descripcion="Analgésico",
            precio=25000.0,
            stock=100,
            fecha_vencimiento="2024-12-31",
            categoria="Medicamentos",
            categoria_id="123e4567-e89b-12d3-a456-426614174000",
            proveedor_id="456e7890-e89b-12d3-a456-426614174001"
        )
        
        with patch('aplicacion.comandos.crear_producto_con_inventario.RepositorioCategoriaSQLite') as mock_cat_repo_class:
            mock_cat_repo = Mock()
            mock_cat_repo_class.return_value = mock_cat_repo
            mock_cat_repo.obtener_por_id.side_effect = Exception("Error de base de datos")
            
            handler = CrearProductoConInventarioHandler()
            
            # Act & Assert
            with pytest.raises(Exception, match="Error de base de datos"):
                handler.handle(comando)
