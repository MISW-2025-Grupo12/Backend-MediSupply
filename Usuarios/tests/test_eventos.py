import pytest
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from dominio.eventos import ProveedorCreado


class TestEventos:
    
    def test_proveedor_creado_get_datos_evento(self):
        """Test obtener datos del evento ProveedorCreado"""
        # Arrange
        proveedor_id = "123e4567-e89b-12d3-a456-426614174000"
        evento = ProveedorCreado(
            proveedor_id=proveedor_id,
            nombre="Farmacia Central",
            email="contacto@farmacia.com",
            direccion="Calle 123 #45-67"
        )
        
        # Act
        datos = evento._get_datos_evento()
        
        # Assert
        assert datos['proveedor_id'] == proveedor_id
        assert datos['nombre'] == "Farmacia Central"
        assert datos['email'] == "contacto@farmacia.com"
        assert datos['direccion'] == "Calle 123 #45-67"
