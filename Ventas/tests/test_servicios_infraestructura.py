import pytest
import uuid
from unittest.mock import patch, Mock
import requests

# Configurar el path para importar los módulos
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from infraestructura.servicio_usuarios import ServicioUsuarios
from infraestructura.servicio_logistica import ServicioLogistica
from infraestructura.servicio_productos import ServicioProductos

class TestServicioUsuarios:
    """Pruebas para el servicio de usuarios"""
    
    def test_obtener_vendedor_por_id_exitoso(self):
        """Test obtener vendedor por ID exitosamente"""
        vendedor_id = str(uuid.uuid4())
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'id': vendedor_id,
            'nombre': 'Juan Pérez',
            'email': 'juan@example.com'
        }
        
        with patch('requests.get', return_value=mock_response):
            servicio = ServicioUsuarios()
            resultado = servicio.obtener_vendedor_por_id(vendedor_id)
            
            assert resultado is not None
            assert resultado['id'] == vendedor_id
            assert resultado['nombre'] == 'Juan Pérez'
    
    def test_obtener_vendedor_por_id_no_existe(self):
        """Test obtener vendedor que no existe"""
        vendedor_id = str(uuid.uuid4())
        mock_response = Mock()
        mock_response.status_code = 404
        
        with patch('requests.get', return_value=mock_response):
            servicio = ServicioUsuarios()
            resultado = servicio.obtener_vendedor_por_id(vendedor_id)
            
            assert resultado is None
    
    def test_obtener_vendedor_por_id_error_servidor(self):
        """Test obtener vendedor con error de servidor"""
        vendedor_id = str(uuid.uuid4())
        mock_response = Mock()
        mock_response.status_code = 500
        
        with patch('requests.get', return_value=mock_response):
            servicio = ServicioUsuarios()
            resultado = servicio.obtener_vendedor_por_id(vendedor_id)
            
            assert resultado is None
    
    def test_obtener_vendedor_por_id_exception(self):
        """Test obtener vendedor con excepción"""
        vendedor_id = str(uuid.uuid4())
        
        with patch('requests.get', side_effect=requests.RequestException("Error de conexión")):
            servicio = ServicioUsuarios()
            resultado = servicio.obtener_vendedor_por_id(vendedor_id)
            
            assert resultado is None
    
    def test_obtener_cliente_por_id_exitoso(self):
        """Test obtener cliente por ID exitosamente"""
        cliente_id = str(uuid.uuid4())
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'id': cliente_id,
            'nombre': 'María García',
            'email': 'maria@example.com'
        }
        
        with patch('requests.get', return_value=mock_response):
            servicio = ServicioUsuarios()
            resultado = servicio.obtener_cliente_por_id(cliente_id)
            
            assert resultado is not None
            assert resultado['id'] == cliente_id
            assert resultado['nombre'] == 'María García'
    
    def test_obtener_cliente_por_id_no_existe(self):
        """Test obtener cliente que no existe"""
        cliente_id = str(uuid.uuid4())
        mock_response = Mock()
        mock_response.status_code = 404
        
        with patch('requests.get', return_value=mock_response):
            servicio = ServicioUsuarios()
            resultado = servicio.obtener_cliente_por_id(cliente_id)
            
            assert resultado is None
    
    def test_obtener_cliente_por_id_error_servidor(self):
        """Test obtener cliente con error de servidor"""
        cliente_id = str(uuid.uuid4())
        mock_response = Mock()
        mock_response.status_code = 500
        
        with patch('requests.get', return_value=mock_response):
            servicio = ServicioUsuarios()
            resultado = servicio.obtener_cliente_por_id(cliente_id)
            
            assert resultado is None
    
    def test_obtener_cliente_por_id_exception(self):
        """Test obtener cliente con excepción"""
        cliente_id = str(uuid.uuid4())
        
        with patch('requests.get', side_effect=requests.RequestException("Error de conexión")):
            servicio = ServicioUsuarios()
            resultado = servicio.obtener_cliente_por_id(cliente_id)
            
            assert resultado is None

class TestServicioLogistica:
    """Pruebas para el servicio de logística"""
    
    def test_buscar_productos_exitoso(self):
        """Test buscar productos exitosamente"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                'id': str(uuid.uuid4()),
                'nombre': 'Paracetamol',
                'precio': 5.50,
                'stock': 100
            },
            {
                'id': str(uuid.uuid4()),
                'nombre': 'Ibuprofeno',
                'precio': 8.75,
                'stock': 50
            }
        ]
        
        with patch('requests.get', return_value=mock_response):
            servicio = ServicioLogistica()
            resultado = servicio.buscar_productos("Paracetamol")
            
            assert resultado is not None
            assert len(resultado) == 2
            assert resultado[0]['nombre'] == 'Paracetamol'
    
    def test_buscar_productos_error_servidor(self):
        """Test buscar productos con error de servidor"""
        mock_response = Mock()
        mock_response.status_code = 500
        
        with patch('requests.get', return_value=mock_response):
            servicio = ServicioLogistica()
            resultado = servicio.buscar_productos("Paracetamol")
            
            assert resultado == []
    
    def test_buscar_productos_exception(self):
        """Test buscar productos con excepción"""
        with patch('requests.get', side_effect=requests.RequestException("Error de conexión")):
            servicio = ServicioLogistica()
            resultado = servicio.buscar_productos("Paracetamol")
            
            assert resultado == []

class TestServicioProductos:
    """Pruebas para el servicio de productos"""
    
    def test_obtener_producto_por_id_exitoso(self):
        """Test obtener producto por ID exitosamente"""
        producto_id = str(uuid.uuid4())
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'id': producto_id,
            'nombre': 'Paracetamol',
            'precio': 5.50,
            'stock': 100
        }
        
        with patch('requests.get', return_value=mock_response):
            servicio = ServicioProductos()
            resultado = servicio.obtener_producto_por_id(producto_id)
            
            assert resultado is not None
            assert resultado['id'] == producto_id
            assert resultado['nombre'] == 'Paracetamol'
    
    def test_obtener_producto_por_id_no_existe(self):
        """Test obtener producto que no existe"""
        producto_id = str(uuid.uuid4())
        mock_response = Mock()
        mock_response.status_code = 404
        
        with patch('requests.get', return_value=mock_response):
            servicio = ServicioProductos()
            resultado = servicio.obtener_producto_por_id(producto_id)
            
            assert resultado is None
    
    def test_obtener_producto_por_id_error_servidor(self):
        """Test obtener producto con error de servidor"""
        producto_id = str(uuid.uuid4())
        mock_response = Mock()
        mock_response.status_code = 500
        
        with patch('requests.get', return_value=mock_response):
            servicio = ServicioProductos()
            resultado = servicio.obtener_producto_por_id(producto_id)
            
            assert resultado is None
    
    def test_obtener_producto_por_id_exception(self):
        """Test obtener producto con excepción"""
        producto_id = str(uuid.uuid4())
        
        with patch('requests.get', side_effect=requests.RequestException("Error de conexión")):
            servicio = ServicioProductos()
            resultado = servicio.obtener_producto_por_id(producto_id)
            
            assert resultado is None
