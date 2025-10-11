import pytest
import sys
import os
import json
from unittest.mock import Mock, patch
from datetime import datetime, timedelta
from flask import Flask

# Agregar el directorio de utilidades de prueba al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
sys.path.insert(0, os.path.dirname(__file__))

from test_utils import BaseTestHelper
from aplicacion.dto import ProductoDTO, CategoriaDTO
from aplicacion.dto_agregacion import ProductoAgregacionDTO


class TestAPIProducto:
    
    def setup_method(self):
        """Setup para cada test"""
        # Crear aplicación Flask para pruebas con SQLite
        self.app = Flask(__name__)
        
        # Usar SQLite en memoria para pruebas
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        self.app.config['TESTING'] = True
        
        # Importar y configurar la base de datos
        from config.db import db
        self.db = db
        self.db.init_app(self.app)
        
        # Crear tablas
        with self.app.app_context():
            self.db.create_all()
        
        # Crear cliente de prueba
        self.client = self.app.test_client()
    
    def test_crear_producto_exitoso(self):
        """Test crear producto exitoso via API"""
        # Arrange
        producto_data = {
            "nombre": "Paracetamol",
            "descripcion": "Analgésico",
            "precio": 25000.0,
            "categoria": "Medicamentos",
            "categoria_id": "123e4567-e89b-12d3-a456-426614174000",
            "proveedor_id": "456e7890-e89b-12d3-a456-426614174001"
        }
        
        with patch('aplicacion.comandos.crear_producto.CrearProductoHandler') as mock_handler_class:
            mock_handler = Mock()
            mock_handler_class.return_value = mock_handler
            
            # Mock del resultado
            mock_resultado = ProductoAgregacionDTO(
                id="789e0123-e89b-12d3-a456-426614174002",
                nombre="Paracetamol",
                descripcion="Analgésico",
                precio=25000.0,
                categoria_id="123e4567-e89b-12d3-a456-426614174000",
                categoria_nombre="Medicamentos",
                categoria_descripcion="Medicamentos generales",
                proveedor_id="456e7890-e89b-12d3-a456-426614174001",
                proveedor_nombre="Farmacia Central",
                proveedor_email="contacto@farmacia.com",
                proveedor_direccion="Calle 123 #45-67"
            )
            mock_handler.handle.return_value = mock_resultado
            
            # Act
            response = self.client.post('/api/productos/', 
                                      data=json.dumps(producto_data),
                                      content_type='application/json')
            
            # Assert
            assert response.status_code == 201
            data = json.loads(response.data)
            assert data['nombre'] == "Paracetamol"
    
    def test_crear_producto_datos_invalidos(self):
        """Test crear producto con datos inválidos"""
        # Arrange
        producto_data = {
            "nombre": "",  # Nombre vacío
            "descripcion": "Analgésico",
            "precio": -1000.0,  # Precio negativo
            "categoria": "Medicamentos",
            "categoria_id": "123e4567-e89b-12d3-a456-426614174000",
            "proveedor_id": "456e7890-e89b-12d3-a456-426614174001"
        }
        
        with patch('aplicacion.comandos.crear_producto.CrearProductoHandler') as mock_handler_class:
            mock_handler = Mock()
            mock_handler_class.return_value = mock_handler
            mock_handler.handle.side_effect = ValueError("Datos inválidos")
            
            # Act
            response = self.client.post('/api/productos/', 
                                      data=json.dumps(producto_data),
                                      content_type='application/json')
            
            # Assert
            assert response.status_code == 400
            data = json.loads(response.data)
            assert 'error' in data
    
    def test_obtener_productos_exitoso(self):
        """Test obtener todos los productos via API"""
        # Arrange
        with patch('aplicacion.consultas.obtener_productos.ObtenerProductosHandler') as mock_handler_class:
            mock_handler = Mock()
            mock_handler_class.return_value = mock_handler
            
            # Mock del resultado
            mock_productos = [
                ProductoAgregacionDTO(
                    id="789e0123-e89b-12d3-a456-426614174002",
                    nombre="Paracetamol",
                    descripcion="Analgésico",
                    precio=25000.0,
                    categoria_id="123e4567-e89b-12d3-a456-426614174000",
                    categoria_nombre="Medicamentos",
                    categoria_descripcion="Medicamentos generales",
                    proveedor_id="456e7890-e89b-12d3-a456-426614174001",
                    proveedor_nombre="Farmacia Central",
                    proveedor_email="contacto@farmacia.com",
                    proveedor_direccion="Calle 123 #45-67"
                )
            ]
            mock_handler.handle.return_value = mock_productos
            
            # Act
            response = self.client.get('/api/productos/')
            
            # Assert
            assert response.status_code == 200
            data = json.loads(response.data)
            assert len(data) == 1
            assert data[0]['nombre'] == "Paracetamol"
    
    def test_obtener_productos_vacio(self):
        """Test obtener productos cuando no hay productos"""
        # Arrange
        with patch('aplicacion.consultas.obtener_productos.ObtenerProductosHandler') as mock_handler_class:
            mock_handler = Mock()
            mock_handler_class.return_value = mock_handler
            mock_handler.handle.return_value = []
            
            # Act
            response = self.client.get('/api/productos/')
            
            # Assert
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data == []
    
