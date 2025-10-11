import pytest
import sys
import os
import uuid
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from dominio.eventos import ClienteCreado, VendedorCreado, ProveedorCreado


class TestEventos:
    """Test para los eventos de dominio"""
    
    def test_cliente_creado_creacion(self):
        """Test creación de evento ClienteCreado"""
        # Arrange
        cliente_id = uuid.uuid4()
        nombre = "Juan Pérez"
        email = "juan@email.com"
        telefono = "1234567890"
        direccion = "Calle 123 #45-67"
        
        # Act
        evento = ClienteCreado(
            cliente_id=cliente_id,
            nombre=nombre,
            email=email,
            telefono=telefono,
            direccion=direccion
        )
        
        # Assert
        assert evento.cliente_id == cliente_id
        assert evento.nombre == nombre
        assert evento.email == email
        assert evento.telefono == telefono
        assert evento.direccion == direccion
    
    def test_cliente_creado_get_datos_evento(self):
        """Test conversión de ClienteCreado a diccionario"""
        # Arrange
        cliente_id = uuid.uuid4()
        evento = ClienteCreado(
            cliente_id=cliente_id,
            nombre="Juan Pérez",
            email="juan@email.com",
            telefono="1234567890",
            direccion="Calle 123 #45-67"
        )
        
        # Act
        dict_result = evento._get_datos_evento()
        
        # Assert
        assert isinstance(dict_result, dict)
        assert dict_result['cliente_id'] == str(cliente_id)
        assert dict_result['nombre'] == "Juan Pérez"
        assert dict_result['email'] == "juan@email.com"
        assert dict_result['telefono'] == "1234567890"
        assert dict_result['direccion'] == "Calle 123 #45-67"
    
    def test_vendedor_creado_creacion(self):
        """Test creación de evento VendedorCreado"""
        # Arrange
        vendedor_id = uuid.uuid4()
        nombre = "María García"
        email = "maria@email.com"
        telefono = "0987654321"
        direccion = "Avenida 456 #78-90"
        
        # Act
        evento = VendedorCreado(
            vendedor_id=vendedor_id,
            nombre=nombre,
            email=email,
            telefono=telefono,
            direccion=direccion
        )
        
        # Assert
        assert evento.vendedor_id == vendedor_id
        assert evento.nombre == nombre
        assert evento.email == email
        assert evento.telefono == telefono
        assert evento.direccion == direccion
    
    def test_vendedor_creado_get_datos_evento(self):
        """Test conversión de VendedorCreado a diccionario"""
        # Arrange
        vendedor_id = uuid.uuid4()
        evento = VendedorCreado(
            vendedor_id=vendedor_id,
            nombre="María García",
            email="maria@email.com",
            telefono="0987654321",
            direccion="Avenida 456 #78-90"
        )
        
        # Act
        dict_result = evento._get_datos_evento()
        
        # Assert
        assert isinstance(dict_result, dict)
        assert dict_result['vendedor_id'] == str(vendedor_id)
        assert dict_result['nombre'] == "María García"
        assert dict_result['email'] == "maria@email.com"
        assert dict_result['telefono'] == "0987654321"
        assert dict_result['direccion'] == "Avenida 456 #78-90"
    
    def test_proveedor_creado_creacion(self):
        """Test creación de evento ProveedorCreado"""
        # Arrange
        proveedor_id = uuid.uuid4()
        nombre = "Farmacia Central"
        email = "contacto@farmacia.com"
        direccion = "Calle Principal #100"
        
        # Act
        evento = ProveedorCreado(
            proveedor_id=proveedor_id,
            nombre=nombre,
            email=email,
            direccion=direccion
        )
        
        # Assert
        assert evento.proveedor_id == proveedor_id
        assert evento.nombre == nombre
        assert evento.email == email
        assert evento.direccion == direccion
    
    def test_proveedor_creado_get_datos_evento(self):
        """Test conversión de ProveedorCreado a diccionario"""
        # Arrange
        proveedor_id = uuid.uuid4()
        evento = ProveedorCreado(
            proveedor_id=proveedor_id,
            nombre="Farmacia Central",
            email="contacto@farmacia.com",
            direccion="Calle Principal #100"
        )
        
        # Act
        dict_result = evento._get_datos_evento()
        
        # Assert
        assert isinstance(dict_result, dict)
        assert dict_result['proveedor_id'] == str(proveedor_id)
        assert dict_result['nombre'] == "Farmacia Central"
        assert dict_result['email'] == "contacto@farmacia.com"
        assert dict_result['direccion'] == "Calle Principal #100"
    
    def test_eventos_valores_por_defecto(self):
        """Test eventos con valores por defecto"""
        # Arrange & Act
        cliente_evento = ClienteCreado(
            cliente_id=uuid.uuid4(),
            nombre="Test",
            email="test@test.com",
            telefono="0000000000",
            direccion="Test"
        )
        
        vendedor_evento = VendedorCreado(
            vendedor_id=uuid.uuid4(),
            nombre="Test",
            email="test@test.com",
            telefono="0000000000",
            direccion="Test"
        )
        
        proveedor_evento = ProveedorCreado(
            proveedor_id=uuid.uuid4(),
            nombre="Test",
            email="test@test.com",
            direccion="Test"
        )
        
        # Assert
        assert cliente_evento.nombre == "Test"
        assert vendedor_evento.nombre == "Test"
        assert proveedor_evento.nombre == "Test"