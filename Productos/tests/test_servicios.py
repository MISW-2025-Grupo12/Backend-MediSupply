import pytest
import sys
import os
from unittest.mock import Mock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from seedwork.aplicacion.servicios import Servicio


class TestServicios:
    """Test para servicios de aplicación"""
    
    def test_servicio_es_abstracto(self):
        """Test que Servicio es una clase abstracta"""
        # Arrange & Act & Assert
        with pytest.raises(TypeError):
            Servicio()
    
    def test_servicio_herencia(self):
        """Test que Servicio puede ser heredado"""
        # Arrange
        class ServicioConcreto(Servicio):
            def __init__(self):
                pass
        
        # Act
        servicio = ServicioConcreto()
        
        # Assert
        assert isinstance(servicio, Servicio)
        assert isinstance(servicio, ServicioConcreto)
    
    def test_servicio_metodos_abstractos(self):
        """Test que Servicio tiene métodos abstractos"""
        # Arrange
        class ServicioIncompleto(Servicio):
            def __init__(self):
                pass
        
        # Act & Assert
        with pytest.raises(TypeError):
            ServicioIncompleto()
    
    def test_servicio_implementacion_completa(self):
        """Test implementación completa de Servicio"""
        # Arrange
        class ServicioCompleto(Servicio):
            def __init__(self):
                self.nombre = "Test"
            
            def ejecutar(self, parametros=None):
                return f"Ejecutando {self.nombre}"
        
        # Act
        servicio = ServicioCompleto()
        resultado = servicio.ejecutar()
        
        # Assert
        assert isinstance(servicio, Servicio)
        assert resultado == "Ejecutando Test"
        assert servicio.nombre == "Test"
    
    def test_servicio_con_parametros(self):
        """Test Servicio con parámetros"""
        # Arrange
        class ServicioConParametros(Servicio):
            def __init__(self, configuracion):
                self.configuracion = configuracion
            
            def ejecutar(self, parametros=None):
                return f"Config: {self.configuracion}, Params: {parametros}"
        
        # Act
        servicio = ServicioConParametros("test_config")
        resultado = servicio.ejecutar({"key": "value"})
        
        # Assert
        assert isinstance(servicio, Servicio)
        assert resultado == "Config: test_config, Params: {'key': 'value'}"
        assert servicio.configuracion == "test_config"
    
    def test_servicio_metodo_abstracto_no_implementado(self):
        """Test que Servicio requiere implementación de métodos abstractos"""
        # Arrange
        class ServicioParcial(Servicio):
            def __init__(self):
                pass
            
            def ejecutar(self, parametros=None):
                return "Ejecutado"
        
        # Act & Assert
        # Si no hay métodos abstractos definidos, esto debería funcionar
        servicio = ServicioParcial()
        assert isinstance(servicio, Servicio)
        assert servicio.ejecutar() == "Ejecutado"
