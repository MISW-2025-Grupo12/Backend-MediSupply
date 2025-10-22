import pytest
import sys
import os
import uuid
from unittest.mock import Mock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from aplicacion.mapeadores import (
    MapeadorProveedorDTOJson, 
    MapeadorProveedor,
    MapeadorVendedorDTOJson,
    MapeadorClienteDTOJson
)
from aplicacion.dto import ProveedorDTO, VendedorDTO, ClienteDTO
from dominio.entidades import Proveedor, Vendedor, Cliente
from dominio.objetos_valor import Nombre, Email, Direccion, Telefono, Identificacion


class TestMapeadores:
    
    def test_mapeador_proveedor_dto_json_a_json(self):
        """Test convertir ProveedorDTO a JSON"""
        # Arrange
        proveedor_id = uuid.uuid4()
        
        proveedor_dto = ProveedorDTO(
            id=proveedor_id,
            nombre="Farmacia Central",
            email="contacto@farmacia.com",
            direccion="Calle 123 #45-67",
            identificacion="9001234567",
            telefono="3001234567"
        )
        
        mapeador = MapeadorProveedorDTOJson()
        
        # Act
        json_result = mapeador.dto_a_externo(proveedor_dto)
        
        # Assert
        assert json_result['id'] == str(proveedor_id)
        assert json_result['nombre'] == "Farmacia Central"
        assert json_result['email'] == "contacto@farmacia.com"
        assert json_result['direccion'] == "Calle 123 #45-67"
        assert json_result['identificacion'] == "9001234567"
        assert json_result['telefono'] == "3001234567"
    
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


class TestMapeadorProveedorDTOJson:
    """Test para MapeadorProveedorDTOJson"""
    
    def test_dto_a_externo(self):
        """Test conversión de DTO a formato externo"""
        # Arrange
        proveedor_id = str(uuid.uuid4())
        dto = ProveedorDTO(
            id=proveedor_id,
            nombre="Farmacia Central",
            email="contacto@farmacia.com",
            direccion="Calle 123 #45-67",
            identificacion="9001234567",
            telefono="3001234567"
        )
        mapeador = MapeadorProveedorDTOJson()
        
        # Act
        resultado = mapeador.dto_a_externo(dto)
        
        # Assert
        assert resultado['id'] == proveedor_id
        assert resultado['nombre'] == "Farmacia Central"
        assert resultado['email'] == "contacto@farmacia.com"
        assert resultado['direccion'] == "Calle 123 #45-67"
        assert resultado['identificacion'] == "9001234567"
        assert resultado['telefono'] == "3001234567"
    
    def test_externo_a_dto(self):
        """Test conversión de formato externo a DTO"""
        # Arrange
        proveedor_id = str(uuid.uuid4())
        externo = {
            'id': proveedor_id,
            'nombre': "Farmacia Central",
            'email': "contacto@farmacia.com",
            'direccion': "Calle 123 #45-67"
        }
        mapeador = MapeadorProveedorDTOJson()
        
        # Act
        resultado = mapeador.externo_a_dto(externo)
        
        # Assert
        assert resultado.id == proveedor_id
        assert resultado.nombre == "Farmacia Central"
        assert resultado.email == "contacto@farmacia.com"
        assert resultado.direccion == "Calle 123 #45-67"
    
    def test_externo_a_dto_con_valores_por_defecto(self):
        """Test conversión con valores por defecto"""
        # Arrange
        externo = {
            'id': str(uuid.uuid4())
        }
        mapeador = MapeadorProveedorDTOJson()
        
        # Act
        resultado = mapeador.externo_a_dto(externo)
        
        # Assert
        assert resultado.nombre == ""
        assert resultado.email == ""
        assert resultado.direccion == ""


class TestMapeadorProveedor:
    """Test para MapeadorProveedor"""
    
    def test_entidad_a_dto(self):
        """Test conversión de entidad a DTO"""
        # Arrange
        proveedor_id = str(uuid.uuid4())
        entidad = Proveedor(
            id=proveedor_id,
            nombre=Nombre("Farmacia Central"),
            email=Email("contacto@farmacia.com"),
            direccion=Direccion("Calle 123 #45-67"),
            telefono=Telefono("3001234567"),
            identificacion=Identificacion("9001234567")
        )
        mapeador = MapeadorProveedor()
        
        # Act
        resultado = mapeador.entidad_a_dto(entidad)
        
        # Assert
        assert resultado.id == proveedor_id
        assert resultado.nombre == "Farmacia Central"
        assert resultado.email == "contacto@farmacia.com"
        assert resultado.direccion == "Calle 123 #45-67"


class TestMapeadorVendedorDTOJsonCoverage:
    """Test adicionales para MapeadorVendedorDTOJson para mejorar coverage"""
    
    def test_dtos_a_externo_lista_vacia(self):
        """Test dtos_a_externo con lista vacía"""
        # Arrange
        mapeador = MapeadorVendedorDTOJson()
        
        # Act
        resultado = mapeador.dtos_a_externo([])
        
        # Assert
        assert resultado == []
    
    def test_dtos_a_externo_lista_con_elementos(self):
        """Test dtos_a_externo con lista con elementos"""
        # Arrange
        vendedor_id1 = str(uuid.uuid4())
        vendedor_id2 = str(uuid.uuid4())
        
        dto1 = VendedorDTO(
            id=vendedor_id1,
            nombre="Vendedor 1",
            email="vendedor1@test.com",
            telefono="1234567890",
            direccion="Dirección 1",
            identificacion="1001234567"
        )
        
        dto2 = VendedorDTO(
            id=vendedor_id2,
            nombre="Vendedor 2",
            email="vendedor2@test.com",
            telefono="0987654321",
            direccion="Dirección 2",
            identificacion="1009876543"
        )
        
        mapeador = MapeadorVendedorDTOJson()
        
        # Act
        resultado = mapeador.dtos_a_externo([dto1, dto2])
        
        # Assert
        assert len(resultado) == 2
        assert resultado[0]['id'] == vendedor_id1
        assert resultado[0]['nombre'] == "Vendedor 1"
        assert resultado[1]['id'] == vendedor_id2
        assert resultado[1]['nombre'] == "Vendedor 2"


class TestMapeadorClienteDTOJsonCoverage:
    """Test adicionales para MapeadorClienteDTOJson para mejorar coverage"""
    
    def test_dtos_a_externo_lista_vacia(self):
        """Test dtos_a_externo con lista vacía"""
        # Arrange
        mapeador = MapeadorClienteDTOJson()
        
        # Act
        resultado = mapeador.dtos_a_externo([])
        
        # Assert
        assert resultado == []
    
    def test_dtos_a_externo_lista_con_elementos(self):
        """Test dtos_a_externo con lista con elementos"""
        # Arrange
        cliente_id1 = str(uuid.uuid4())
        cliente_id2 = str(uuid.uuid4())
        
        dto1 = ClienteDTO(
            id=cliente_id1,
            nombre="Cliente 1",
            email="cliente1@test.com",
            telefono="1234567890",
            direccion="Dirección 1",
            identificacion="1001234567"
        )
        
        dto2 = ClienteDTO(
            id=cliente_id2,
            nombre="Cliente 2",
            email="cliente2@test.com",
            telefono="0987654321",
            direccion="Dirección 2",
            identificacion="1009876543"
        )
        
        mapeador = MapeadorClienteDTOJson()
        
        # Act
        resultado = mapeador.dtos_a_externo([dto1, dto2])
        
        # Assert
        assert len(resultado) == 2
        assert resultado[0]['id'] == cliente_id1
        assert resultado[0]['nombre'] == "Cliente 1"
        assert resultado[1]['id'] == cliente_id2
        assert resultado[1]['nombre'] == "Cliente 2"
