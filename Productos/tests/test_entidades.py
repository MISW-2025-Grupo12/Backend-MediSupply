import pytest
import sys
import os
from datetime import datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from dominio.entidades import Producto, CategoriaEntidad
from dominio.objetos_valor import Nombre, Descripcion, Precio, Stock, FechaVencimiento, Categoria


class TestEntidades:
    
    def test_producto_creacion_exitosa(self):
        """Test creación exitosa de entidad Producto"""
        # Arrange
        nombre = Nombre("Paracetamol")
        descripcion = Descripcion("Analgésico")
        precio = Precio(25000.0)
        stock = Stock(100)
        fecha_vencimiento = FechaVencimiento(datetime.now() + timedelta(days=30))
        categoria = Categoria("Medicamentos")
        categoria_id = "123e4567-e89b-12d3-a456-426614174000"
        proveedor_id = "456e7890-e89b-12d3-a456-426614174001"
        
        # Act
        producto = Producto(
            nombre=nombre,
            descripcion=descripcion,
            precio=precio,
            categoria=categoria,
            categoria_id=categoria_id,
            proveedor_id=proveedor_id
        )
        
        # Assert
        assert producto.nombre == nombre
        assert producto.descripcion == descripcion
        assert producto.precio == precio
        assert producto.categoria == categoria
        assert producto.categoria_id == categoria_id
        assert producto.proveedor_id == proveedor_id
        assert producto.id is not None
    
    def test_producto_disparar_evento_creacion(self):
        """Test disparar evento de creación"""
        # Arrange
        nombre = Nombre("Paracetamol")
        descripcion = Descripcion("Analgésico")
        precio = Precio(25000.0)
        stock = Stock(100)
        fecha_vencimiento = FechaVencimiento(datetime.now() + timedelta(days=30))
        categoria = Categoria("Medicamentos")
        categoria_id = "123e4567-e89b-12d3-a456-426614174000"
        proveedor_id = "456e7890-e89b-12d3-a456-426614174001"
        
        producto = Producto(
            nombre=nombre,
            descripcion=descripcion,
            precio=precio,
            categoria=categoria,
            categoria_id=categoria_id,
            proveedor_id=proveedor_id
        )
        
        # Act
        evento = producto.disparar_evento_creacion()
        
        # Assert
        assert evento is not None
        assert evento.proveedor_id == proveedor_id
        assert evento.nombre == "Paracetamol"
        assert evento.descripcion == "Analgésico"
        assert evento.precio == 25000.0
        assert evento.categoria == "Medicamentos"
        assert evento.categoria_id == categoria_id
    
    def test_categoria_entidad_creacion_exitosa(self):
        """Test creación exitosa de entidad CategoriaEntidad"""
        # Arrange
        nombre = Nombre("Medicamentos")
        descripcion = Descripcion("Medicamentos generales")
        
        # Act
        categoria = CategoriaEntidad(
            nombre=nombre,
            descripcion=descripcion
        )
        
        # Assert
        assert categoria.nombre == nombre
        assert categoria.descripcion == descripcion
        assert categoria.id is not None
