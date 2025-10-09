import pytest
import sys
import os
import uuid
from datetime import datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from aplicacion.mapeadores import MapeadorProducto
from aplicacion.dto import ProductoDTO
from dominio.entidades import Producto
from dominio.objetos_valor import Nombre, Descripcion, Precio, Stock, FechaVencimiento, Categoria


class TestMapeadorProducto:
    
    def test_entidad_a_dto(self):
        """Test convertir entidad Producto a ProductoDTO"""
        # Arrange
        producto_id = uuid.uuid4()
        categoria_id = "123e4567-e89b-12d3-a456-426614174000"
        proveedor_id = "456e7890-e89b-12d3-a456-426614174001"
        
        producto_entidad = Producto(
            id=producto_id,
            nombre=Nombre("Paracetamol"),
            descripcion=Descripcion("Analgésico"),
            precio=Precio(25000.0),
            stock=Stock(100),
            fecha_vencimiento=FechaVencimiento(datetime.now() + timedelta(days=30)),
            categoria=Categoria("Medicamentos"),
            categoria_id=categoria_id,
            proveedor_id=proveedor_id
        )
        
        mapeador = MapeadorProducto()
        
        # Act
        producto_dto = mapeador.entidad_a_dto(producto_entidad)
        
        # Assert
        assert producto_dto.id == producto_id
        assert producto_dto.nombre == "Paracetamol"
        assert producto_dto.descripcion == "Analgésico"
        assert producto_dto.precio == 25000.0
        assert producto_dto.stock == 100
        assert producto_dto.categoria == "Medicamentos"
        assert producto_dto.categoria_id == categoria_id
        assert producto_dto.proveedor_id == proveedor_id
    
    def test_dto_a_entidad(self):
        """Test convertir ProductoDTO a entidad Producto"""
        # Arrange
        producto_id = uuid.uuid4()
        categoria_id = "123e4567-e89b-12d3-a456-426614174000"
        proveedor_id = "456e7890-e89b-12d3-a456-426614174001"
        
        producto_dto = ProductoDTO(
            id=producto_id,
            nombre="Paracetamol",
            descripcion="Analgésico",
            precio=25000.0,
            stock=100,
            fecha_vencimiento=datetime.now() + timedelta(days=30),
            categoria="Medicamentos",
            categoria_id=categoria_id,
            proveedor_id=proveedor_id
        )
        
        mapeador = MapeadorProducto()
        
        # Act
        producto_entidad = mapeador.dto_a_entidad(producto_dto)
        
        # Assert
        assert producto_entidad.id == producto_id
        assert producto_entidad.nombre.nombre == "Paracetamol"
        assert producto_entidad.descripcion.descripcion == "Analgésico"
        assert producto_entidad.precio.precio == 25000.0
        assert producto_entidad.stock.stock == 100
        assert producto_entidad.categoria.nombre == "Medicamentos"
        assert producto_entidad.categoria_id == categoria_id
        assert producto_entidad.proveedor_id == proveedor_id
