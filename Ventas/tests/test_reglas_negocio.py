import pytest
import sys
import os
from datetime import datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from dominio.reglas import (
    VendedorIdNoPuedeSerVacio, ClienteIdNoPuedeSerVacio, FechaProgramadaDebeSerFutura,
    EstadoVisitaDebeSerValido, DireccionNoPuedeSerVacia, TelefonoNoPuedeSerVacio
)


class TestReglasNegocio:
    
    def test_vendedor_id_no_puede_ser_vacio(self):
        regla = VendedorIdNoPuedeSerVacio("123")
        assert regla.es_valido() == True
        
        regla = VendedorIdNoPuedeSerVacio("")
        assert regla.es_valido() == False
        
        regla = VendedorIdNoPuedeSerVacio(None)
        assert regla.es_valido() == False
        
        regla = VendedorIdNoPuedeSerVacio("   ")
        assert regla.es_valido() == False
    
    def test_cliente_id_no_puede_ser_vacio(self):
        regla = ClienteIdNoPuedeSerVacio("123")
        assert regla.es_valido() == True
        
        regla = ClienteIdNoPuedeSerVacio("")
        assert regla.es_valido() == False
        
        regla = ClienteIdNoPuedeSerVacio(None)
        assert regla.es_valido() == False
        
        regla = ClienteIdNoPuedeSerVacio("   ")
        assert regla.es_valido() == False
    
    def test_fecha_programada_debe_ser_futura(self):
        fecha_futura = (datetime.now() + timedelta(days=1)).isoformat()
        regla = FechaProgramadaDebeSerFutura(fecha_futura)
        assert regla.es_valido() == True
        
        fecha_pasada = (datetime.now() - timedelta(days=1)).isoformat()
        regla = FechaProgramadaDebeSerFutura(fecha_pasada)
        assert regla.es_valido() == False
        
        regla = FechaProgramadaDebeSerFutura("fecha_invalida")
        assert regla.es_valido() == False
    
    def test_estado_visita_debe_ser_valido(self):
        regla = EstadoVisitaDebeSerValido("pendiente")
        assert regla.es_valido() == True
        
        regla = EstadoVisitaDebeSerValido("completada")
        assert regla.es_valido() == True
        
        regla = EstadoVisitaDebeSerValido("invalido")
        assert regla.es_valido() == False
    
    def test_direccion_no_puede_ser_vacia(self):
        regla = DireccionNoPuedeSerVacia("Calle 123")
        assert regla.es_valido() == True
        
        regla = DireccionNoPuedeSerVacia("")
        assert regla.es_valido() == False
        
        regla = DireccionNoPuedeSerVacia(None)
        assert regla.es_valido() == False
        
        regla = DireccionNoPuedeSerVacia("   ")
        assert regla.es_valido() == False
    
    def test_telefono_no_puede_ser_vacio(self):
        regla = TelefonoNoPuedeSerVacio("3001234567")
        assert regla.es_valido() == True
        
        regla = TelefonoNoPuedeSerVacio("")
        assert regla.es_valido() == False
        
        regla = TelefonoNoPuedeSerVacio(None)
        assert regla.es_valido() == False
        
        regla = TelefonoNoPuedeSerVacio("   ")
        assert regla.es_valido() == False
