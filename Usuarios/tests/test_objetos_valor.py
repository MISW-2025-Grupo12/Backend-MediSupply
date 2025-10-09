import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from dominio.objetos_valor import Nombre, Email, Direccion


class TestObjetosValor:
    
    def test_nombre_creacion_exitosa(self):
        """Test creación exitosa de objeto Nombre"""
        # Arrange & Act
        nombre = Nombre("Farmacia Central")
        
        # Assert
        assert nombre.nombre == "Farmacia Central"
    
    def test_email_creacion_exitosa(self):
        """Test creación exitosa de objeto Email"""
        # Arrange & Act
        email = Email("contacto@farmacia.com")
        
        # Assert
        assert email.email == "contacto@farmacia.com"
    
    def test_direccion_creacion_exitosa(self):
        """Test creación exitosa de objeto Direccion"""
        # Arrange & Act
        direccion = Direccion("Calle 123 #45-67")
        
        # Assert
        assert direccion.direccion == "Calle 123 #45-67"
