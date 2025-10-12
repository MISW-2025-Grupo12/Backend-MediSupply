import pytest
import sys
import os
from datetime import datetime, timedelta
from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from dominio.eventos import EntregaCreada, InventarioReservado, InventarioDescontado

class TestEntregaCreada:
    def test_crear_evento_entrega_creada(self):
        evento = EntregaCreada(
            entrega_id="entrega-123",
            direccion="Calle 123 #45-67",
            fecha_entrega=datetime.now() + timedelta(days=1),
            pedido={
                "id": "pedido-456",
                "cliente": {"nombre": "Cliente Mock", "direccion": "Calle 123"},
                "productos": [{"nombre": "Paracetamol", "cantidad": 2}]
            }
        )
        
        assert evento.entrega_id == "entrega-123"
        assert evento.direccion == "Calle 123 #45-67"
        assert isinstance(evento.fecha_entrega, datetime)
        assert isinstance(evento.pedido, dict)
        assert "cliente" in evento.pedido
        assert "productos" in evento.pedido

    def test_evento_entrega_creada_inmutable(self):
        evento = EntregaCreada(
            entrega_id="entrega-123",
            direccion="Calle 123 #45-67",
            fecha_entrega=datetime.now() + timedelta(days=1),
            pedido={"id": "pedido-789"}
        )

        assert evento.entrega_id == "entrega-123"
        assert evento.direccion == "Calle 123 #45-67"
        assert "id" in evento.pedido

    def test_evento_entrega_creada_igualdad(self):
        fecha = datetime.now() + timedelta(days=1)
        pedido_mock = {
            "id": "pedido-001",
            "cliente": {"nombre": "Cliente Mock"},
            "productos": [{"nombre": "Ibuprofeno"}]
        }

        evento1 = EntregaCreada(
            entrega_id="entrega-123",
            direccion="Calle 123",
            fecha_entrega=fecha,
            pedido=pedido_mock
        )
        evento2 = EntregaCreada(
            entrega_id="entrega-123",
            direccion="Calle 123",
            fecha_entrega=fecha,
            pedido=pedido_mock
        )

        assert evento1.entrega_id == evento2.entrega_id
        assert evento1.direccion == evento2.direccion
        assert evento1.fecha_entrega == evento2.fecha_entrega
        assert evento1.pedido == evento2.pedido

class TestInventarioReservado:
    def test_crear_evento_inventario_reservado(self):
        evento = InventarioReservado(
            producto_id="prod-123",
            cantidad_reservada=10,
            cantidad_disponible_restante=90
        )
        
        assert evento.producto_id == "prod-123"
        assert evento.cantidad_reservada == 10
        assert evento.cantidad_disponible_restante == 90

    def test_evento_inventario_reservado_inmutable(self):
        evento = InventarioReservado(
            producto_id="prod-123",
            cantidad_reservada=10,
            cantidad_disponible_restante=90
        )
        

        assert evento.producto_id == "prod-123"
        assert evento.cantidad_reservada == 10

    def test_evento_inventario_reservado_igualdad(self):
        evento1 = InventarioReservado(
            producto_id="prod-123",
            cantidad_reservada=10,
            cantidad_disponible_restante=90
        )
        evento2 = InventarioReservado(
            producto_id="prod-123",
            cantidad_reservada=10,
            cantidad_disponible_restante=90
        )
        

        assert evento1.producto_id == evento2.producto_id
        assert evento1.cantidad_reservada == evento2.cantidad_reservada
        assert evento1.cantidad_disponible_restante == evento2.cantidad_disponible_restante

class TestInventarioDescontado:
    def test_crear_evento_inventario_descontado(self):
        evento = InventarioDescontado(
            producto_id="prod-123",
            cantidad_descontada=5,
            cantidad_reservada_restante=15
        )
        
        assert evento.producto_id == "prod-123"
        assert evento.cantidad_descontada == 5
        assert evento.cantidad_reservada_restante == 15

    def test_evento_inventario_descontado_inmutable(self):
        evento = InventarioDescontado(
            producto_id="prod-123",
            cantidad_descontada=5,
            cantidad_reservada_restante=15
        )
        

        assert evento.producto_id == "prod-123"
        assert evento.cantidad_descontada == 5

    def test_evento_inventario_descontado_igualdad(self):
        evento1 = InventarioDescontado(
            producto_id="prod-123",
            cantidad_descontada=5,
            cantidad_reservada_restante=15
        )
        evento2 = InventarioDescontado(
            producto_id="prod-123",
            cantidad_descontada=5,
            cantidad_reservada_restante=15
        )
        

        assert evento1.producto_id == evento2.producto_id
        assert evento1.cantidad_descontada == evento2.cantidad_descontada
        assert evento1.cantidad_reservada_restante == evento2.cantidad_reservada_restante

    def test_evento_inventario_descontado_diferentes(self):
        evento1 = InventarioDescontado(
            producto_id="prod-123",
            cantidad_descontada=5,
            cantidad_reservada_restante=15
        )
        evento2 = InventarioDescontado(
            producto_id="prod-456",
            cantidad_descontada=5,
            cantidad_reservada_restante=15
        )
        
        assert evento1 != evento2
