import pytest
import sys
import os
from unittest.mock import Mock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from seedwork.dominio.excepciones import (
    ExcepcionDominio, 
    IdDebeSerInmutableExcepcion, 
    ReglaNegocioExcepcion, 
    ExcepcionFabrica
)
from seedwork.dominio.reglas import ReglaNegocio


class TestExcepcionesDominio:
    """Test para excepciones de dominio"""
    
    def test_excepcion_dominio_herencia(self):
        """Test que ExcepcionDominio hereda de Exception"""
        # Arrange & Act
        excepcion = ExcepcionDominio("Test error")
        
        # Assert
        assert isinstance(excepcion, Exception)
        assert str(excepcion) == "Test error"
    
    def test_id_debe_ser_inmutable_excepcion_mensaje_por_defecto(self):
        """Test IdDebeSerInmutableExcepcion con mensaje por defecto"""
        # Arrange & Act
        excepcion = IdDebeSerInmutableExcepcion()
        
        # Assert
        assert isinstance(excepcion, ExcepcionDominio)
        assert str(excepcion) == "El identificador debe ser inmutable"
        assert excepcion._IdDebeSerInmutableExcepcion__mensaje == "El identificador debe ser inmutable"
    
    def test_id_debe_ser_inmutable_excepcion_mensaje_personalizado(self):
        """Test IdDebeSerInmutableExcepcion con mensaje personalizado"""
        # Arrange
        mensaje = "ID no puede ser modificado"
        
        # Act
        excepcion = IdDebeSerInmutableExcepcion(mensaje)
        
        # Assert
        assert isinstance(excepcion, ExcepcionDominio)
        assert str(excepcion) == mensaje
        assert excepcion._IdDebeSerInmutableExcepcion__mensaje == mensaje
    
    def test_regla_negocio_excepcion(self):
        """Test ReglaNegocioExcepcion"""
        # Arrange
        regla = Mock(spec=ReglaNegocio)
        regla.__str__ = Mock(return_value="Regla de negocio violada")
        
        # Act
        excepcion = ReglaNegocioExcepcion(regla)
        
        # Assert
        assert isinstance(excepcion, ExcepcionDominio)
        assert excepcion.regla == regla
        assert str(excepcion) == "Regla de negocio violada"
    
    def test_excepcion_fabrica(self):
        """Test ExcepcionFabrica"""
        # Arrange
        mensaje = "Error en fábrica"
        
        # Act
        excepcion = ExcepcionFabrica(mensaje)
        
        # Assert
        assert isinstance(excepcion, ExcepcionDominio)
        assert str(excepcion) == mensaje
        assert excepcion._ExcepcionFabrica__mensaje == mensaje
    
    def test_excepcion_fabrica_con_mensaje_vacio(self):
        """Test ExcepcionFabrica con mensaje vacío"""
        # Arrange & Act
        excepcion = ExcepcionFabrica("")
        
        # Assert
        assert isinstance(excepcion, ExcepcionDominio)
        assert str(excepcion) == ""
        assert excepcion._ExcepcionFabrica__mensaje == ""
