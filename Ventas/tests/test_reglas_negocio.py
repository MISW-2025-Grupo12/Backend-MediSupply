import pytest
import sys
import os
from datetime import datetime, timedelta, date, time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from dominio.reglas import (
    VendedorIdNoPuedeSerVacio, ClienteIdNoPuedeSerVacio, FechaProgramadaDebeSerFutura,
    EstadoVisitaDebeSerValido, DireccionNoPuedeSerVacia, TelefonoNoPuedeSerVacio,
    FechaRealizadaNoPuedeEstarVacia, FechaRealizadaFormatoISO, FechaRealizadaNoPuedeSerFutura,
    HoraRealizadaNoPuedeEstarVacia, HoraRealizadaFormatoISO, NovedadesMaximo500Caracteres,
    ClienteDebeEstarSeleccionado
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

    def test_fecha_realizada_no_puede_estar_vacia(self):
        regla = FechaRealizadaNoPuedeEstarVacia(date(2025, 10, 15))
        assert regla.es_valido() == True
        
        regla = FechaRealizadaNoPuedeEstarVacia(None)
        assert regla.es_valido() == False

    def test_fecha_realizada_formato_iso(self):
        regla = FechaRealizadaFormatoISO("2025-10-15")
        assert regla.es_valido() == True
        
        regla = FechaRealizadaFormatoISO("15/10/2025")
        assert regla.es_valido() == False
        
        regla = FechaRealizadaFormatoISO("fecha_invalida")
        assert regla.es_valido() == False

    def test_fecha_realizada_no_puede_ser_futura(self):
        regla = FechaRealizadaNoPuedeSerFutura(date.today())
        assert regla.es_valido() == True
        
        regla = FechaRealizadaNoPuedeSerFutura(date.today() - timedelta(days=1))
        assert regla.es_valido() == True
        
        regla = FechaRealizadaNoPuedeSerFutura(date.today() + timedelta(days=1))
        assert regla.es_valido() == False

    def test_hora_realizada_no_puede_estar_vacia(self):
        regla = HoraRealizadaNoPuedeEstarVacia(time(14, 30, 0))
        assert regla.es_valido() == True
        
        regla = HoraRealizadaNoPuedeEstarVacia(None)
        assert regla.es_valido() == False

    def test_hora_realizada_formato_iso(self):
        regla = HoraRealizadaFormatoISO("14:30:00")
        assert regla.es_valido() == True
        
        regla = HoraRealizadaFormatoISO("14:30")
        assert regla.es_valido() == True
        
        regla = HoraRealizadaFormatoISO("2:30 PM")
        assert regla.es_valido() == False
        
        regla = HoraRealizadaFormatoISO("hora_invalida")
        assert regla.es_valido() == False

    def test_novedades_maximo_500_caracteres(self):
        regla = NovedadesMaximo500Caracteres("Novedades cortas")
        assert regla.es_valido() == True
        
        regla = NovedadesMaximo500Caracteres("x" * 500)
        assert regla.es_valido() == True
        
        regla = NovedadesMaximo500Caracteres("x" * 501)
        assert regla.es_valido() == False
        
        regla = NovedadesMaximo500Caracteres(None)
        assert regla.es_valido() == True

    def test_cliente_debe_estar_seleccionado(self):
        regla = ClienteDebeEstarSeleccionado("cliente-123")
        assert regla.es_valido() == True
        
        regla = ClienteDebeEstarSeleccionado("")
        assert regla.es_valido() == False
        
        regla = ClienteDebeEstarSeleccionado(None)
        assert regla.es_valido() == False
        
        regla = ClienteDebeEstarSeleccionado("   ")
        assert regla.es_valido() == False
