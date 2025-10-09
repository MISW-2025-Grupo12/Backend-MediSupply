import pytest
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from dominio.entidades import Proveedor
from dominio.objetos_valor import Nombre, Email, Direccion


class TestEntidades:
    
    def test_proveedor_creacion_exitosa(self):
        """Test creación exitosa de entidad Proveedor"""
        # Arrange
        nombre = Nombre("Farmacia Central")
        email = Email("contacto@farmacia.com")
        direccion = Direccion("Calle 123 #45-67")
        
        # Act
        proveedor = Proveedor(
            nombre=nombre,
            email=email,
            direccion=direccion
        )
        
        # Assert
        assert proveedor.nombre == nombre
        assert proveedor.email == email
        assert proveedor.direccion == direccion
        assert proveedor.id is not None
    
    def test_proveedor_disparar_evento_creacion(self):
        """Test disparar evento de creación"""
        # Arrange
        nombre = Nombre("Farmacia Central")
        email = Email("contacto@farmacia.com")
        direccion = Direccion("Calle 123 #45-67")
        
        proveedor = Proveedor(
            nombre=nombre,
            email=email,
            direccion=direccion
        )
        
        # Act
        evento = proveedor.disparar_evento_creacion()
        
        # Assert
        assert evento is not None
        assert evento.proveedor_id is not None
        assert evento.nombre == "Farmacia Central"
        assert evento.email == "contacto@farmacia.com"
        assert evento.direccion == "Calle 123 #45-67"
