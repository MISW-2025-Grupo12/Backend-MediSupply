import pytest
import sys
import os
from unittest.mock import Mock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from dominio.reglas import (
    NombreProveedorNoPuedeSerVacio,
    EmailProveedorNoPuedeSerVacio,
    DireccionProveedorNoPuedeSerVacia
)
from dominio.objetos_valor import Nombre, Email, Direccion
from seedwork.dominio.reglas import ReglaNegocio, IdEntidadEsInmutable


class TestReglasNegocio:
    
    def test_nombre_proveedor_no_puede_ser_vacio_valido(self):
        """Test regla nombre válido"""
        nombre = Nombre("Farmacia Central")
        regla = NombreProveedorNoPuedeSerVacio(nombre)
        
        assert regla.es_valido() is True
    
    def test_nombre_proveedor_no_puede_ser_vacio_invalido(self):
        """Test regla nombre inválido"""
        # El objeto Nombre("") lanza excepción en su creación
        # Probamos la regla con None para simular nombre vacío
        regla = NombreProveedorNoPuedeSerVacio(None)
        
        assert regla.es_valido() is False
    
    def test_nombre_proveedor_no_puede_ser_vacio_none(self):
        """Test regla nombre None"""
        regla = NombreProveedorNoPuedeSerVacio(None)
        
        assert regla.es_valido() is False
    
    def test_nombre_proveedor_no_puede_ser_vacio_espacios(self):
        """Test regla nombre solo espacios"""
        # El objeto Nombre("   ") lanza excepción en su creación
        # Probamos la regla con None para simular nombre solo espacios
        regla = NombreProveedorNoPuedeSerVacio(None)
        
        assert regla.es_valido() is False
    
    def test_email_proveedor_no_puede_ser_vacio_valido(self):
        """Test regla email válido"""
        email = Email("contacto@farmacia.com")
        regla = EmailProveedorNoPuedeSerVacio(email)
        
        assert regla.es_valido() is True
    
    def test_email_proveedor_no_puede_ser_vacio_invalido(self):
        """Test regla email inválido"""
        # El objeto Email("") lanza excepción en su creación
        # Probamos la regla con None para simular email vacío
        regla = EmailProveedorNoPuedeSerVacio(None)
        
        assert regla.es_valido() is False
    
    def test_email_proveedor_no_puede_ser_vacio_none(self):
        """Test regla email None"""
        regla = EmailProveedorNoPuedeSerVacio(None)
        
        assert regla.es_valido() is False
    
    def test_email_proveedor_no_puede_ser_vacio_espacios(self):
        """Test regla email solo espacios"""
        # El objeto Email("   ") lanza excepción en su creación
        # Probamos la regla con None para simular email solo espacios
        regla = EmailProveedorNoPuedeSerVacio(None)
        
        assert regla.es_valido() is False
    
    def test_direccion_proveedor_no_puede_ser_vacia_valida(self):
        """Test regla dirección válida"""
        direccion = Direccion("Calle 123 #45-67")
        regla = DireccionProveedorNoPuedeSerVacia(direccion)
        
        assert regla.es_valido() is True
    
    def test_direccion_proveedor_no_puede_ser_vacia_invalida(self):
        """Test regla dirección inválida"""
        direccion = Direccion("")
        regla = DireccionProveedorNoPuedeSerVacia(direccion)
        
        assert regla.es_valido() is False
    
    def test_direccion_proveedor_no_puede_ser_vacia_none(self):
        """Test regla dirección None"""
        regla = DireccionProveedorNoPuedeSerVacia(None)
        
        assert regla.es_valido() is False
    
    def test_direccion_proveedor_no_puede_ser_vacia_espacios(self):
        """Test regla dirección solo espacios"""
        direccion = Direccion("   ")
        regla = DireccionProveedorNoPuedeSerVacia(direccion)
        
        assert regla.es_valido() is False


class TestReglaNegocio:
    """Test para ReglaNegocio"""
    
    def test_regla_negocio_mensaje_por_defecto(self):
        """Test ReglaNegocio con mensaje por defecto"""
        # Arrange
        class ReglaTest(ReglaNegocio):
            def es_valido(self) -> bool:
                return True
        
        # Act
        regla = ReglaTest("Mensaje personalizado")
        
        # Assert
        assert regla.mensaje_error() == "Mensaje personalizado"
        assert str(regla) == "ReglaTest - Mensaje personalizado"
        assert regla.es_valido() is True
    
    def test_regla_negocio_mensaje_vacio(self):
        """Test ReglaNegocio con mensaje vacío"""
        # Arrange
        class ReglaTest(ReglaNegocio):
            def es_valido(self) -> bool:
                return False
        
        # Act
        regla = ReglaTest("")
        
        # Assert
        assert regla.mensaje_error() == ""
        assert str(regla) == "ReglaTest - "
        assert regla.es_valido() is False
    
    def test_regla_negocio_abstracta(self):
        """Test que ReglaNegocio es abstracta"""
        # Arrange & Act & Assert
        with pytest.raises(TypeError):
            ReglaNegocio("Test")


class TestIdEntidadEsInmutable:
    """Test para IdEntidadEsInmutable"""
    
    def test_entidad_sin_id_es_valida(self):
        """Test entidad sin _id es válida"""
        # Arrange
        entidad = Mock()
        del entidad._id  # Asegurar que no tiene _id
        
        # Act
        regla = IdEntidadEsInmutable(entidad)
        
        # Assert
        assert regla.es_valido() is True
        assert regla.entidad == entidad
    
    def test_entidad_con_id_none_es_valida(self):
        """Test entidad con _id None es válida"""
        # Arrange
        entidad = Mock()
        entidad._id = None
        
        # Act
        regla = IdEntidadEsInmutable(entidad)
        
        # Assert
        assert regla.es_valido() is True
        assert regla.entidad == entidad
    
    def test_entidad_con_id_asignado_no_es_valida(self):
        """Test entidad con _id asignado no es válida"""
        # Arrange
        entidad = Mock()
        entidad._id = "123"
        
        # Act
        regla = IdEntidadEsInmutable(entidad)
        
        # Assert
        assert regla.es_valido() is False
        assert regla.entidad == entidad
    
    def test_entidad_sin_atributo_id_es_valida(self):
        """Test entidad sin atributo _id es válida"""
        # Arrange
        entidad = Mock()
        # Asegurar que no tiene _id
        if hasattr(entidad, '_id'):
            delattr(entidad, '_id')
        
        # Act
        regla = IdEntidadEsInmutable(entidad)
        
        # Assert
        assert regla.es_valido() is True
        assert regla.entidad == entidad
    
    def test_mensaje_personalizado(self):
        """Test IdEntidadEsInmutable con mensaje personalizado"""
        # Arrange
        entidad = Mock()
        mensaje = "ID no puede ser modificado"
        
        # Act
        regla = IdEntidadEsInmutable(entidad, mensaje)
        
        # Assert
        assert regla.mensaje_error() == mensaje
        assert str(regla) == f"IdEntidadEsInmutable - {mensaje}"
    
    def test_mensaje_por_defecto(self):
        """Test IdEntidadEsInmutable con mensaje por defecto"""
        # Arrange
        entidad = Mock()
        
        # Act
        regla = IdEntidadEsInmutable(entidad)
        
        # Assert
        assert regla.mensaje_error() == "El identificador de la entidad debe ser Inmutable"
        assert str(regla) == "IdEntidadEsInmutable - El identificador de la entidad debe ser Inmutable"
