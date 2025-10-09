import pytest
import sys
import os
from datetime import datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from dominio.objetos_valor import EstadoVisita, FechaProgramada, Direccion, Telefono, Descripcion


class TestObjetosValor:
    
    def test_estado_visita_valido(self):
        estado = EstadoVisita("pendiente")
        assert estado.estado == "pendiente"
        
        estado = EstadoVisita("completada")
        assert estado.estado == "completada"
    
    def test_estado_visita_invalido(self):
        with pytest.raises(ValueError, match="Estado debe ser 'pendiente' o 'completada'"):
            EstadoVisita("invalido")
    
    def test_fecha_programada_futura(self):
        fecha_futura = datetime.now() + timedelta(days=1)
        fecha = FechaProgramada(fecha_futura)
        assert fecha.fecha == fecha_futura
    
    def test_fecha_programada_pasada(self):
        fecha_pasada = datetime.now() - timedelta(days=1)
        with pytest.raises(ValueError, match="La fecha programada debe ser futura"):
            FechaProgramada(fecha_pasada)
    
    def test_direccion(self):
        direccion = Direccion("Calle 123 #45-67")
        assert direccion.direccion == "Calle 123 #45-67"
    
    def test_telefono(self):
        telefono = Telefono("3001234567")
        assert telefono.telefono == "3001234567"
    
    def test_descripcion(self):
        descripcion = Descripcion("Visita programada")
        assert descripcion.descripcion == "Visita programada"
