import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from dominio.reglas import (
    NombreProveedorNoPuedeSerVacio,
    EmailProveedorNoPuedeSerVacio,
    DireccionProveedorNoPuedeSerVacia
)
from dominio.objetos_valor import Nombre, Email, Direccion


class TestReglasNegocio:
    
    def test_nombre_proveedor_no_puede_ser_vacio_valido(self):
        """Test regla nombre válido"""
        nombre = Nombre("Farmacia Central")
        regla = NombreProveedorNoPuedeSerVacio(nombre)
        
        assert regla.es_valido() is True
    
    def test_nombre_proveedor_no_puede_ser_vacio_invalido(self):
        """Test regla nombre inválido"""
        nombre = Nombre("")
        regla = NombreProveedorNoPuedeSerVacio(nombre)
        
        assert regla.es_valido() is False
    
    def test_nombre_proveedor_no_puede_ser_vacio_none(self):
        """Test regla nombre None"""
        regla = NombreProveedorNoPuedeSerVacio(None)
        
        assert regla.es_valido() is False
    
    def test_nombre_proveedor_no_puede_ser_vacio_espacios(self):
        """Test regla nombre solo espacios"""
        nombre = Nombre("   ")
        regla = NombreProveedorNoPuedeSerVacio(nombre)
        
        assert regla.es_valido() is False
    
    def test_email_proveedor_no_puede_ser_vacio_valido(self):
        """Test regla email válido"""
        email = Email("contacto@farmacia.com")
        regla = EmailProveedorNoPuedeSerVacio(email)
        
        assert regla.es_valido() is True
    
    def test_email_proveedor_no_puede_ser_vacio_invalido(self):
        """Test regla email inválido"""
        email = Email("")
        regla = EmailProveedorNoPuedeSerVacio(email)
        
        assert regla.es_valido() is False
    
    def test_email_proveedor_no_puede_ser_vacio_none(self):
        """Test regla email None"""
        regla = EmailProveedorNoPuedeSerVacio(None)
        
        assert regla.es_valido() is False
    
    def test_email_proveedor_no_puede_ser_vacio_espacios(self):
        """Test regla email solo espacios"""
        email = Email("   ")
        regla = EmailProveedorNoPuedeSerVacio(email)
        
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
