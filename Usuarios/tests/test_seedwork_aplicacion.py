import pytest
import sys
import os
from unittest.mock import Mock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from seedwork.aplicacion.comandos import Comando, ejecutar_comando
from seedwork.aplicacion.consultas import Consulta, ejecutar_consulta


class ComandoTest(Comando):
    
    def __init__(self, valor):
        self.valor = valor


class ConsultaTest(Consulta):
    
    def __init__(self, valor):
        self.valor = valor


class TestComandoCoverage:
    
    def test_comando_puede_ser_instanciado(self):
        """Test que Comando puede ser instanciado"""
        # Arrange & Act
        comando = ComandoTest("test")
        
        # Assert
        assert isinstance(comando, Comando)
        assert comando.valor == "test"
    
    def test_ejecutar_comando_sin_manejador(self):
        """Test ejecutar_comando sin manejador registrado"""
        # Arrange
        comando = ComandoTest("test")
        
        # Act & Assert - Debe lanzar excepción si no hay manejador
        with pytest.raises(Exception):
            ejecutar_comando(comando)


class TestConsultaCoverage:
    
    def test_consulta_puede_ser_instanciada(self):
        """Test que Consulta puede ser instanciada"""
        # Arrange & Act
        consulta = ConsultaTest("test")
        
        # Assert
        assert isinstance(consulta, Consulta)
        assert consulta.valor == "test"
    
    def test_ejecutar_consulta_sin_manejador(self):
        # Arrange
        consulta = ConsultaTest("test")
        
        # Act & Assert - Debe lanzar excepción si no hay manejador
        with pytest.raises(Exception):
            ejecutar_consulta(consulta)
