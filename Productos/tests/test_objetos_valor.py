import pytest
import sys
import os
from datetime import datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from dominio.objetos_valor import Nombre, Descripcion, Precio, Stock, FechaVencimiento, Categoria


class TestObjetosValor:
    
    def test_nombre_creacion_exitosa(self):
        """Test creación exitosa de objeto Nombre"""
        # Arrange & Act
        nombre = Nombre("Paracetamol")
        
        # Assert
        assert nombre.nombre == "Paracetamol"
    
    def test_descripcion_creacion_exitosa(self):
        """Test creación exitosa de objeto Descripcion"""
        # Arrange & Act
        descripcion = Descripcion("Analgésico para el dolor")
        
        # Assert
        assert descripcion.descripcion == "Analgésico para el dolor"
    
    def test_precio_creacion_exitosa(self):
        """Test creación exitosa de objeto Precio"""
        # Arrange & Act
        precio = Precio(25000.0)
        
        # Assert
        assert precio.precio == 25000.0
    
    def test_stock_creacion_exitosa(self):
        """Test creación exitosa de objeto Stock"""
        # Arrange & Act
        stock = Stock(100)
        
        # Assert
        assert stock.stock == 100
    
    def test_fecha_vencimiento_creacion_exitosa(self):
        """Test creación exitosa de objeto FechaVencimiento"""
        # Arrange
        fecha_futura = datetime.now() + timedelta(days=30)
        
        # Act
        fecha_vencimiento = FechaVencimiento(fecha_futura)
        
        # Assert
        assert fecha_vencimiento.fecha == fecha_futura
    
    def test_categoria_creacion_exitosa(self):
        """Test creación exitosa de objeto Categoria"""
        # Arrange & Act
        categoria = Categoria("Medicamentos")
        
        # Assert
        assert categoria.nombre == "Medicamentos"
