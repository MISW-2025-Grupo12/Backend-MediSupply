import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from seedwork.dominio.excepciones import ReglaNegocioExcepcion, ExcepcionFabrica


class TestExcepciones:
    """Test para excepciones de dominio"""
    
    def test_regla_negocio_excepcion_creacion(self):
        """Test creación de ReglaNegocioExcepcion"""
        # Arrange
        mensaje = "Regla de negocio violada"
        
        # Act
        excepcion = ReglaNegocioExcepcion(mensaje)
        
        # Assert
        assert str(excepcion) == mensaje
        assert isinstance(excepcion, Exception)
    
    def test_regla_negocio_excepcion_mensaje_vacio(self):
        """Test ReglaNegocioExcepcion con mensaje vacío"""
        # Arrange & Act
        excepcion = ReglaNegocioExcepcion("")
        
        # Assert
        assert str(excepcion) == ""
        assert isinstance(excepcion, Exception)
    
    def test_regla_negocio_excepcion_mensaje_none(self):
        """Test ReglaNegocioExcepcion con mensaje None"""
        # Arrange & Act
        excepcion = ReglaNegocioExcepcion(None)
        
        # Assert
        assert str(excepcion) == "None"
        assert isinstance(excepcion, Exception)
    
    def test_excepcion_fabrica_creacion(self):
        """Test creación de ExcepcionFabrica"""
        # Arrange
        mensaje = "Error en fábrica"
        
        # Act
        excepcion = ExcepcionFabrica(mensaje)
        
        # Assert
        assert str(excepcion) == mensaje
        assert isinstance(excepcion, Exception)
    
    def test_excepcion_fabrica_mensaje_vacio(self):
        """Test ExcepcionFabrica con mensaje vacío"""
        # Arrange & Act
        excepcion = ExcepcionFabrica("")
        
        # Assert
        assert str(excepcion) == ""
        assert isinstance(excepcion, Exception)
    
    def test_excepcion_fabrica_mensaje_none(self):
        """Test ExcepcionFabrica con mensaje None"""
        # Arrange & Act
        excepcion = ExcepcionFabrica(None)
        
        # Assert
        assert str(excepcion) == "None"
        assert isinstance(excepcion, Exception)
    
    def test_regla_negocio_excepcion_herencia(self):
        """Test que ReglaNegocioExcepcion hereda de Exception"""
        # Arrange & Act
        excepcion = ReglaNegocioExcepcion("Test")
        
        # Assert
        assert isinstance(excepcion, Exception)
        assert hasattr(excepcion, '__str__')
    
    def test_excepcion_fabrica_herencia(self):
        """Test que ExcepcionFabrica hereda de Exception"""
        # Arrange & Act
        excepcion = ExcepcionFabrica("Test")
        
        # Assert
        assert isinstance(excepcion, Exception)
        assert hasattr(excepcion, '__str__')
    
    def test_regla_negocio_excepcion_con_causa(self):
        """Test ReglaNegocioExcepcion con causa"""
        # Arrange
        causa = ValueError("Error original")
        mensaje = "Regla de negocio violada"
        
        # Act
        excepcion = ReglaNegocioExcepcion(mensaje)
        excepcion.__cause__ = causa
        
        # Assert
        assert str(excepcion) == mensaje
        assert excepcion.__cause__ == causa
    
    def test_excepcion_fabrica_con_causa(self):
        """Test ExcepcionFabrica con causa"""
        # Arrange
        causa = ValueError("Error original")
        mensaje = "Error en fábrica"
        
        # Act
        excepcion = ExcepcionFabrica(mensaje)
        excepcion.__cause__ = causa
        
        # Assert
        assert str(excepcion) == mensaje
        assert excepcion.__cause__ == causa
