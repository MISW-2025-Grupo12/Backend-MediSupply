import pytest
import sys
import os
from datetime import datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from dominio.objetos_valor import Cantidad, FechaVencimiento

class TestCantidad:
    def test_crear_cantidad_valida(self):
        cantidad = Cantidad(10)
        assert cantidad.valor == 10

    def test_crear_cantidad_cero(self):
        cantidad = Cantidad(0)
        assert cantidad.valor == 0

    def test_crear_cantidad_negativa_raise_error(self):
        with pytest.raises(ValueError, match="La cantidad no puede ser negativa"):
            Cantidad(-5)

    def test_cantidad_inmutable(self):
        cantidad = Cantidad(10)
        with pytest.raises(AttributeError):
            cantidad.valor = 20

    def test_cantidad_igualdad(self):
        cantidad1 = Cantidad(10)
        cantidad2 = Cantidad(10)
        cantidad3 = Cantidad(20)
        
        assert cantidad1 == cantidad2
        assert cantidad1 != cantidad3

    def test_cantidad_repr(self):
        cantidad = Cantidad(15)
        assert "Cantidad(valor=15)" in repr(cantidad)

class TestFechaVencimiento:
    def test_crear_fecha_vencimiento_futura(self):
        fecha_futura = datetime.now() + timedelta(days=30)
        fecha_vencimiento = FechaVencimiento(fecha_futura)
        assert fecha_vencimiento.valor == fecha_futura

    def test_crear_fecha_vencimiento_hoy(self):
        fecha_hoy = datetime.now()
        fecha_vencimiento = FechaVencimiento(fecha_hoy)
        assert fecha_vencimiento.valor == fecha_hoy

    def test_crear_fecha_vencimiento_pasado_raise_error(self):
        fecha_pasado = datetime.now() - timedelta(days=1)
        with pytest.raises(ValueError, match="La fecha de vencimiento no puede ser en el pasado"):
            FechaVencimiento(fecha_pasado)

    def test_fecha_vencimiento_inmutable(self):
        fecha_futura = datetime.now() + timedelta(days=30)
        fecha_vencimiento = FechaVencimiento(fecha_futura)
        with pytest.raises(AttributeError):
            fecha_vencimiento.valor = datetime.now() + timedelta(days=60)

    def test_fecha_vencimiento_igualdad(self):
        fecha1 = datetime.now() + timedelta(days=30)
        fecha2 = datetime.now() + timedelta(days=30)
        fecha3 = datetime.now() + timedelta(days=60)
        
        fv1 = FechaVencimiento(fecha1)
        fv2 = FechaVencimiento(fecha2)
        fv3 = FechaVencimiento(fecha3)
        
        assert fv1 == fv2
        assert fv1 != fv3

    def test_fecha_vencimiento_repr(self):
        fecha = datetime.now() + timedelta(days=30)
        fecha_vencimiento = FechaVencimiento(fecha)
        assert "FechaVencimiento" in repr(fecha_vencimiento)
        assert "valor=" in repr(fecha_vencimiento)

    def test_fecha_vencimiento_con_microsegundos(self):
        # Test con fecha que incluye microsegundos (futura)
        fecha_exacta = datetime.now() + timedelta(days=30, hours=1, minutes=30, seconds=45, microseconds=123456)
        fecha_vencimiento = FechaVencimiento(fecha_exacta)
        assert fecha_vencimiento.valor == fecha_exacta

    def test_fecha_vencimiento_limite_actual(self):
        # Test con fecha exactamente ahora (debería ser válida)
        ahora = datetime.now()
        fecha_vencimiento = FechaVencimiento(ahora)
        assert fecha_vencimiento.valor == ahora

    def test_fecha_vencimiento_muy_futura(self):
        # Test con fecha muy lejana en el futuro
        fecha_muy_futura = datetime.now() + timedelta(days=3650)  # 10 años
        fecha_vencimiento = FechaVencimiento(fecha_muy_futura)
        assert fecha_vencimiento.valor == fecha_muy_futura
