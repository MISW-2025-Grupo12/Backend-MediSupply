import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from seedwork.aplicacion.servicios import Servicio
from seedwork.dominio.servicios import Servicio as ServicioDominio


class TestServicios:
    """Test para servicios del seedwork"""
    
    def test_servicio_aplicacion_puede_ser_instanciado(self):
        """Test que Servicio de aplicación puede ser instanciado"""
        # Arrange & Act
        servicio = Servicio()
        
        # Assert
        assert isinstance(servicio, Servicio)
    
    def test_servicio_dominio_puede_ser_instanciado(self):
        """Test que Servicio de dominio puede ser instanciado"""
        # Arrange & Act
        servicio = ServicioDominio()
        
        # Assert
        assert isinstance(servicio, ServicioDominio)
