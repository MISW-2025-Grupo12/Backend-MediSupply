import pytest
import sys
import os
import uuid
from unittest.mock import Mock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from aplicacion.mapeadores import MapeadorProductoDTOJson, MapeadorCategoriaDTOJson, MapeadorProductoAgregacionDTOJson
from aplicacion.dto import ProductoDTO, CategoriaDTO
from aplicacion.dto_agregacion import ProductoAgregacionDTO


class TestMapeadores:
    
    def test_mapeador_producto_dto_json_a_json(self):
        """Test convertir ProductoDTO a JSON"""
        # Arrange
        producto_id = uuid.uuid4()
        categoria_id = uuid.uuid4()
        proveedor_id = str(uuid.uuid4())
        
        from datetime import datetime
        
        producto_dto = ProductoDTO(
            id=producto_id,
            nombre="Paracetamol",
            descripcion="Analgésico",
            precio=25000.0,
            stock=100,
            fecha_vencimiento=datetime(2025, 12, 31),
            categoria="Medicamentos",
            categoria_id=str(categoria_id),
            proveedor_id=proveedor_id
        )
        
        mapeador = MapeadorProductoDTOJson()
        
        # Act
        json_result = mapeador.dto_a_externo(producto_dto)
        
        # Assert
        assert json_result['id'] == str(producto_id)
        assert json_result['nombre'] == "Paracetamol"
        assert json_result['descripcion'] == "Analgésico"
        assert json_result['precio'] == 25000.0
        assert json_result['stock'] == 100
        assert json_result['categoria'] == "Medicamentos"
        assert json_result['categoria_id'] == str(categoria_id)
        assert json_result['proveedor_id'] == proveedor_id
    
    def test_mapeador_producto_dto_json_a_dto(self):
        """Test convertir JSON a ProductoDTO"""
        # Arrange
        producto_id = str(uuid.uuid4())
        categoria_id = str(uuid.uuid4())
        proveedor_id = str(uuid.uuid4())
        
        json_data = {
            'id': producto_id,
            'nombre': "Paracetamol",
            'descripcion': "Analgésico",
            'precio': 25000.0,
            'stock': 100,
            'fecha_vencimiento': "2025-12-31",
            'categoria': "Medicamentos",
            'categoria_id': categoria_id,
            'proveedor_id': proveedor_id
        }
        
        mapeador = MapeadorProductoDTOJson()
        
        # Act
        producto_dto = mapeador.externo_a_dto(json_data)
        
        # Assert
        assert str(producto_dto.id) == producto_id
        assert producto_dto.nombre == "Paracetamol"
        assert producto_dto.descripcion == "Analgésico"
        assert producto_dto.precio == 25000.0
        assert producto_dto.stock == 100
        assert producto_dto.categoria == "Medicamentos"
        assert producto_dto.categoria_id == categoria_id
        assert producto_dto.proveedor_id == proveedor_id
    
    def test_mapeador_categoria_dto_json_a_json(self):
        """Test convertir CategoriaDTO a JSON"""
        # Arrange
        categoria_id = uuid.uuid4()
        
        categoria_dto = CategoriaDTO(
            id=categoria_id,
            nombre="Medicamentos",
            descripcion="Medicamentos generales"
        )
        
        mapeador = MapeadorCategoriaDTOJson()
        
        # Act
        json_result = mapeador.dto_a_externo(categoria_dto)
        
        # Assert
        assert json_result['id'] == str(categoria_id)
        assert json_result['nombre'] == "Medicamentos"
        assert json_result['descripcion'] == "Medicamentos generales"
    
    def test_mapeador_categoria_dto_json_a_dto(self):
        """Test convertir JSON a CategoriaDTO"""
        # Arrange
        categoria_id = str(uuid.uuid4())
        
        json_data = {
            'id': categoria_id,
            'nombre': "Medicamentos",
            'descripcion': "Medicamentos generales"
        }
        
        mapeador = MapeadorCategoriaDTOJson()
        
        # Act
        categoria_dto = mapeador.externo_a_dto(json_data)
        
        # Assert
        assert str(categoria_dto.id) == categoria_id
        assert categoria_dto.nombre == "Medicamentos"
        assert categoria_dto.descripcion == "Medicamentos generales"
    
    def test_mapeador_producto_agregacion_dto_json_a_json(self):
        """Test convertir ProductoAgregacionDTO a JSON"""
        # Arrange
        producto_id = uuid.uuid4()
        categoria_id = uuid.uuid4()
        proveedor_id = str(uuid.uuid4())
        
        from datetime import datetime
        
        producto_agregacion = ProductoAgregacionDTO(
            id=producto_id,
            nombre="Paracetamol",
            descripcion="Analgésico",
            precio=25000.0,
            stock=100,
            fecha_vencimiento=datetime(2025, 12, 31),
            categoria_id=str(categoria_id),
            proveedor_id=proveedor_id,
            categoria_nombre="Medicamentos",
            categoria_descripcion="Medicamentos generales",
            proveedor_nombre="Farmacia Central",
            proveedor_email="contacto@farmacia.com",
            proveedor_direccion="Calle 123 #45-67"
        )
        
        mapeador = MapeadorProductoAgregacionDTOJson()
        
        # Act
        json_result = mapeador.agregacion_a_externo(producto_agregacion)
        
        # Assert
        assert json_result['id'] == str(producto_id)
        assert json_result['nombre'] == "Paracetamol"
        assert json_result['precio'] == 25000.0
        assert json_result['categoria']['nombre'] == "Medicamentos"
        assert json_result['proveedor']['nombre'] == "Farmacia Central"
        assert json_result['proveedor']['email'] == "contacto@farmacia.com"
