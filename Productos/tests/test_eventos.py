import pytest
import sys
import os
from datetime import datetime
import uuid

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from dominio.eventos import ProductoCreado, InventarioAsignado


class TestEventos:
    """Test para eventos de dominio"""
    
    def test_producto_creado_creacion_exitosa(self):
        """Test creación de evento ProductoCreado exitosa"""
        # Arrange
        producto_id = uuid.uuid4()
        nombre = "Paracetamol"
        descripcion = "Analgésico"
        precio = 25000.0
        categoria = "Medicamentos"
        categoria_id = str(uuid.uuid4())
        proveedor_id = str(uuid.uuid4())
        
        # Act
        evento = ProductoCreado(
            producto_id=producto_id,
            nombre=nombre,
            descripcion=descripcion,
            precio=precio,
            categoria=categoria,
            categoria_id=categoria_id,
            proveedor_id=proveedor_id
        )
        
        # Assert
        assert evento.producto_id == producto_id
        assert evento.nombre == nombre
        assert evento.descripcion == descripcion
        assert evento.precio == precio
        assert evento.categoria == categoria
        assert evento.categoria_id == categoria_id
        assert evento.proveedor_id == proveedor_id
    
    def test_producto_creado_to_dict(self):
        """Test conversión de ProductoCreado a diccionario"""
        # Arrange
        producto_id = uuid.uuid4()
        evento = ProductoCreado(
            producto_id=producto_id,
            nombre="Paracetamol",
            descripcion="Analgésico",
            precio=25000.0,
            categoria="Medicamentos",
            categoria_id=str(uuid.uuid4()),
            proveedor_id=str(uuid.uuid4())
        )
        
        # Act
        dict_result = evento.to_dict()
        
        # Assert
        assert isinstance(dict_result, dict)
        assert 'id' in dict_result
        assert 'fecha_evento' in dict_result
        assert 'version' in dict_result
        assert 'tipo_evento' in dict_result
        assert 'datos' in dict_result
        
        datos = dict_result['datos']
        assert datos['producto_id'] == str(producto_id)
        assert datos['nombre'] == "Paracetamol"
        assert datos['descripcion'] == "Analgésico"
        assert datos['precio'] == 25000.0
        assert datos['categoria'] == "Medicamentos"
        assert 'categoria_id' in datos
        assert 'proveedor_id' in datos
    
    def test_inventario_asignado_creacion_exitosa(self):
        """Test creación de evento InventarioAsignado exitosa"""
        # Arrange
        producto_id = uuid.uuid4()
        stock = 100
        fecha_vencimiento = "2024-12-31"
        
        # Act
        evento = InventarioAsignado(
            producto_id=producto_id,
            stock=stock,
            fecha_vencimiento=fecha_vencimiento
        )
        
        # Assert
        assert evento.producto_id == producto_id
        assert evento.stock == stock
        assert evento.fecha_vencimiento == fecha_vencimiento
    
    def test_inventario_asignado_to_dict(self):
        """Test conversión de InventarioAsignado a diccionario"""
        # Arrange
        producto_id = uuid.uuid4()
        evento = InventarioAsignado(
            producto_id=producto_id,
            stock=100,
            fecha_vencimiento="2024-12-31"
        )
        
        # Act
        dict_result = evento.to_dict()
        
        # Assert
        assert isinstance(dict_result, dict)
        assert 'id' in dict_result
        assert 'fecha_evento' in dict_result
        assert 'version' in dict_result
        assert 'tipo_evento' in dict_result
        assert 'datos' in dict_result
        
        datos = dict_result['datos']
        assert datos['producto_id'] == str(producto_id)
        assert datos['stock'] == 100
        assert datos['fecha_vencimiento'] == "2024-12-31"
    
    def test_producto_creado_valores_por_defecto(self):
        """Test ProductoCreado con valores por defecto"""
        # Arrange & Act
        evento = ProductoCreado(
            producto_id=uuid.uuid4(),
            nombre="Test",
            descripcion="Test",
            precio=0.0,
            categoria="Test",
            categoria_id="test",
            proveedor_id="test"
        )
        
        # Assert
        assert evento.precio == 0.0
        assert evento.nombre == "Test"
        assert evento.descripcion == "Test"
        assert evento.categoria == "Test"
        assert evento.categoria_id == "test"
        assert evento.proveedor_id == "test"
    
    def test_inventario_asignado_valores_por_defecto(self):
        """Test InventarioAsignado con valores por defecto"""
        # Arrange & Act
        evento = InventarioAsignado(
            producto_id=uuid.uuid4(),
            stock=0,
            fecha_vencimiento=""
        )
        
        # Assert
        assert evento.stock == 0
        assert evento.fecha_vencimiento == ""
