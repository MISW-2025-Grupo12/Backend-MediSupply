import pytest
import sys
import os
from datetime import datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from dominio.entidades import Inventario
from dominio.objetos_valor import ProductoID, Cantidad, FechaVencimiento

class TestInventario:
    def setup_method(self):
        self.fecha_vencimiento = datetime.now() + timedelta(days=30)

    def test_crear_inventario_basico(self):
        inventario = Inventario(
            fecha_vencimiento=FechaVencimiento(self.fecha_vencimiento)
        )
        assert inventario.id is not None
        assert isinstance(inventario.producto_id, ProductoID)
        assert isinstance(inventario.cantidad_disponible, Cantidad)
        assert isinstance(inventario.cantidad_reservada, Cantidad)
        assert isinstance(inventario.fecha_vencimiento, FechaVencimiento)

    def test_crear_inventario_con_datos(self):
        inventario = Inventario(
            producto_id=ProductoID("prod-123"),
            cantidad_disponible=Cantidad(100),
            cantidad_reservada=Cantidad(10),
            fecha_vencimiento=FechaVencimiento(self.fecha_vencimiento)
        )
        
        assert inventario.producto_id.valor == "prod-123"
        assert inventario.cantidad_disponible.valor == 100
        assert inventario.cantidad_reservada.valor == 10
        assert inventario.fecha_vencimiento.valor == self.fecha_vencimiento

    def test_reservar_cantidad_exitoso(self):
        inventario = Inventario(
            producto_id=ProductoID("prod-123"),
            cantidad_disponible=Cantidad(100),
            cantidad_reservada=Cantidad(10),
            fecha_vencimiento=FechaVencimiento(self.fecha_vencimiento)
        )
        
        resultado = inventario.reservar_cantidad(20)
        
        assert resultado == True
        assert inventario.cantidad_disponible.valor == 80  # 100 - 20
        assert inventario.cantidad_reservada.valor == 30   # 10 + 20

    def test_reservar_cantidad_cero(self):
        inventario = Inventario(
            producto_id=ProductoID("prod-123"),
            cantidad_disponible=Cantidad(100),
            cantidad_reservada=Cantidad(10),
            fecha_vencimiento=FechaVencimiento(self.fecha_vencimiento)
        )
        
        resultado = inventario.reservar_cantidad(0)
        
        assert resultado == False
        assert inventario.cantidad_disponible.valor == 100
        assert inventario.cantidad_reservada.valor == 10

    def test_reservar_cantidad_negativa(self):
        inventario = Inventario(
            producto_id=ProductoID("prod-123"),
            cantidad_disponible=Cantidad(100),
            cantidad_reservada=Cantidad(10),
            fecha_vencimiento=FechaVencimiento(self.fecha_vencimiento)
        )
        
        resultado = inventario.reservar_cantidad(-5)
        
        assert resultado == False
        assert inventario.cantidad_disponible.valor == 100
        assert inventario.cantidad_reservada.valor == 10

    def test_reservar_cantidad_insuficiente(self):
        inventario = Inventario(
            producto_id=ProductoID("prod-123"),
            cantidad_disponible=Cantidad(10),
            cantidad_reservada=Cantidad(5),
            fecha_vencimiento=FechaVencimiento(datetime.now() + timedelta(days=30))
        )
        
        resultado = inventario.reservar_cantidad(20)
        
        assert resultado == False
        assert inventario.cantidad_disponible.valor == 10
        assert inventario.cantidad_reservada.valor == 5

    def test_reservar_cantidad_exacta(self):
        inventario = Inventario(
            producto_id=ProductoID("prod-123"),
            cantidad_disponible=Cantidad(50),
            cantidad_reservada=Cantidad(0),
            fecha_vencimiento=FechaVencimiento(self.fecha_vencimiento)
        )
        
        resultado = inventario.reservar_cantidad(50)
        
        assert resultado == True
        assert inventario.cantidad_disponible.valor == 0
        assert inventario.cantidad_reservada.valor == 50

    def test_descontar_cantidad_exitoso(self):
        inventario = Inventario(
            producto_id=ProductoID("prod-123"),
            cantidad_disponible=Cantidad(100),
            cantidad_reservada=Cantidad(30),
            fecha_vencimiento=FechaVencimiento(self.fecha_vencimiento)
        )
        
        resultado = inventario.descontar_cantidad(15)
        
        assert resultado == True
        assert inventario.cantidad_disponible.valor == 100  # No cambia
        assert inventario.cantidad_reservada.valor == 15   # 30 - 15

    def test_descontar_cantidad_cero(self):
        inventario = Inventario(
            producto_id=ProductoID("prod-123"),
            cantidad_disponible=Cantidad(100),
            cantidad_reservada=Cantidad(30),
            fecha_vencimiento=FechaVencimiento(self.fecha_vencimiento)
        )
        
        resultado = inventario.descontar_cantidad(0)
        
        assert resultado == False
        assert inventario.cantidad_disponible.valor == 100
        assert inventario.cantidad_reservada.valor == 30

    def test_descontar_cantidad_negativa(self):
        inventario = Inventario(
            producto_id=ProductoID("prod-123"),
            cantidad_disponible=Cantidad(100),
            cantidad_reservada=Cantidad(30),
            fecha_vencimiento=FechaVencimiento(self.fecha_vencimiento)
        )
        
        resultado = inventario.descontar_cantidad(-5)
        
        assert resultado == False
        assert inventario.cantidad_disponible.valor == 100
        assert inventario.cantidad_reservada.valor == 30

    def test_descontar_cantidad_insuficiente(self):
        inventario = Inventario(
            producto_id=ProductoID("prod-123"),
            cantidad_disponible=Cantidad(100),
            cantidad_reservada=Cantidad(10),
            fecha_vencimiento=FechaVencimiento(self.fecha_vencimiento)
        )
        
        resultado = inventario.descontar_cantidad(20)
        
        assert resultado == False
        assert inventario.cantidad_disponible.valor == 100
        assert inventario.cantidad_reservada.valor == 10

    def test_descontar_cantidad_exacta(self):
        inventario = Inventario(
            producto_id=ProductoID("prod-123"),
            cantidad_disponible=Cantidad(100),
            cantidad_reservada=Cantidad(25),
            fecha_vencimiento=FechaVencimiento(self.fecha_vencimiento)
        )
        
        resultado = inventario.descontar_cantidad(25)
        
        assert resultado == True
        assert inventario.cantidad_disponible.valor == 100  # No cambia
        assert inventario.cantidad_reservada.valor == 0    # 25 - 25

    def test_reservar_y_descontar_secuencia(self):
        inventario = Inventario(
            producto_id=ProductoID("prod-123"),
            cantidad_disponible=Cantidad(100),
            cantidad_reservada=Cantidad(0),
            fecha_vencimiento=FechaVencimiento(self.fecha_vencimiento)
        )
        
        # Reservar 30 unidades
        resultado_reserva = inventario.reservar_cantidad(30)
        assert resultado_reserva == True
        assert inventario.cantidad_disponible.valor == 70
        assert inventario.cantidad_reservada.valor == 30
        
        # Descontar 20 unidades
        resultado_descuento = inventario.descontar_cantidad(20)
        assert resultado_descuento == True
        assert inventario.cantidad_disponible.valor == 70  # No cambia
        assert inventario.cantidad_reservada.valor == 10   # 30 - 20

    def test_reservar_toda_cantidad_disponible(self):
        inventario = Inventario(
            producto_id=ProductoID("prod-123"),
            cantidad_disponible=Cantidad(50),
            cantidad_reservada=Cantidad(0),
            fecha_vencimiento=FechaVencimiento(self.fecha_vencimiento)
        )
        
        resultado = inventario.reservar_cantidad(50)
        
        assert resultado == True
        assert inventario.cantidad_disponible.valor == 0
        assert inventario.cantidad_reservada.valor == 50

    def test_descontar_toda_cantidad_reservada(self):
        inventario = Inventario(
            producto_id=ProductoID("prod-123"),
            cantidad_disponible=Cantidad(100),
            cantidad_reservada=Cantidad(40),
            fecha_vencimiento=FechaVencimiento(self.fecha_vencimiento)
        )
        
        resultado = inventario.descontar_cantidad(40)
        
        assert resultado == True
        assert inventario.cantidad_disponible.valor == 100  # No cambia
        assert inventario.cantidad_reservada.valor == 0     # 40 - 40
