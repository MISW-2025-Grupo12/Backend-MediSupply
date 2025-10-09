import pytest
import sys
import os
import uuid

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from aplicacion.mapeadores import MapeadorProveedorDTOJson
from aplicacion.dto import ProveedorDTO


class TestMapeadores:
    
    def test_mapeador_proveedor_dto_json_a_json(self):
        """Test convertir ProveedorDTO a JSON"""
        # Arrange
        proveedor_id = uuid.uuid4()
        
        proveedor_dto = ProveedorDTO(
            id=proveedor_id,
            nombre="Farmacia Central",
            email="contacto@farmacia.com",
            direccion="Calle 123 #45-67"
        )
        
        mapeador = MapeadorProveedorDTOJson()
        
        # Act
        json_result = mapeador.dto_a_externo(proveedor_dto)
        
        # Assert
        assert json_result['id'] == str(proveedor_id)
        assert json_result['nombre'] == "Farmacia Central"
        assert json_result['email'] == "contacto@farmacia.com"
        assert json_result['direccion'] == "Calle 123 #45-67"
    
    def test_mapeador_proveedor_dto_json_a_dto(self):
        """Test convertir JSON a ProveedorDTO"""
        # Arrange
        proveedor_id = str(uuid.uuid4())
        
        json_data = {
            'id': proveedor_id,
            'nombre': "Farmacia Central",
            'email': "contacto@farmacia.com",
            'direccion': "Calle 123 #45-67"
        }
        
        mapeador = MapeadorProveedorDTOJson()
        
        # Act
        proveedor_dto = mapeador.externo_a_dto(json_data)
        
        # Assert
        assert str(proveedor_dto.id) == proveedor_id
        assert proveedor_dto.nombre == "Farmacia Central"
        assert proveedor_dto.email == "contacto@farmacia.com"
        assert proveedor_dto.direccion == "Calle 123 #45-67"
