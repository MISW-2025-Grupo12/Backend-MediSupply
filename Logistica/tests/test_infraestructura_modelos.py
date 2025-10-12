import pytest
import sys
import os
from unittest.mock import Mock, patch
from datetime import datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from infraestructura.modelos import InventarioModel, EntregaModel

class TestInventarioModel:
    def test_crear_inventario_model(self):
        inventario = InventarioModel()
        assert inventario is not None
        assert hasattr(inventario, 'id')
        assert hasattr(inventario, 'producto_id')
        assert hasattr(inventario, 'cantidad_disponible')
        assert hasattr(inventario, 'cantidad_reservada')
        assert hasattr(inventario, 'fecha_vencimiento')

    def test_inventario_model_con_datos(self):
        inventario = InventarioModel(
            producto_id='prod-123',
            cantidad_disponible=100,
            cantidad_reservada=10,
            fecha_vencimiento=datetime.now() + timedelta(days=30)
        )
        
        assert inventario.producto_id == 'prod-123'
        assert inventario.cantidad_disponible == 100
        assert inventario.cantidad_reservada == 10
        assert isinstance(inventario.fecha_vencimiento, datetime)

    def test_inventario_model_con_datos_none(self):
        inventario = InventarioModel(
            producto_id=None,
            cantidad_disponible=None,
            cantidad_reservada=None,
            fecha_vencimiento=None
        )
        
        assert inventario.producto_id is None
        assert inventario.cantidad_disponible is None
        assert inventario.cantidad_reservada is None
        assert inventario.fecha_vencimiento is None

    def test_inventario_model_con_datos_vacios(self):
        inventario = InventarioModel(
            producto_id='',
            cantidad_disponible=0,
            cantidad_reservada=0,
            fecha_vencimiento=datetime.now()
        )
        
        assert inventario.producto_id == ''
        assert inventario.cantidad_disponible == 0
        assert inventario.cantidad_reservada == 0
        assert isinstance(inventario.fecha_vencimiento, datetime)

    def test_inventario_model_con_fecha_pasada(self):
        fecha_pasada = datetime.now() - timedelta(days=1)
        inventario = InventarioModel(
            producto_id='prod-123',
            cantidad_disponible=100,
            cantidad_reservada=10,
            fecha_vencimiento=fecha_pasada
        )

        assert inventario.fecha_vencimiento == fecha_pasada

    def test_inventario_model_con_fecha_futura(self):
        fecha_futura = datetime.now() + timedelta(days=365)
        inventario = InventarioModel(
            producto_id='prod-123',
            cantidad_disponible=100,
            cantidad_reservada=10,
            fecha_vencimiento=fecha_futura
        )

        assert inventario.fecha_vencimiento == fecha_futura

class TestEntregaModel:
    def test_crear_entrega_model(self):
        entrega = EntregaModel()
        assert entrega is not None
        assert hasattr(entrega, 'id')
        assert hasattr(entrega, 'direccion')
        assert hasattr(entrega, 'fecha_entrega')
        assert hasattr(entrega, 'pedido')

    def test_entrega_model_con_datos(self):
        entrega = EntregaModel(
            id="uuid-test",
            direccion="Calle Falsa 123",
            fecha_entrega=datetime.now(),
            pedido='{}'
        )

        assert entrega.direccion == 'Calle Falsa 123'
        assert isinstance(entrega.fecha_entrega, datetime)
        assert entrega.pedido == '{}'

    def test_entrega_model_con_datos_none(self):
        entrega = EntregaModel(
            direccion=None,
            fecha_entrega=None,
            pedido=None
        )

        assert entrega.direccion is None
        assert entrega.fecha_entrega is None
        assert entrega.pedido is None

    def test_entrega_model_con_datos_vacios(self):
        entrega = EntregaModel(
            direccion='',
            fecha_entrega=datetime.now(),
            pedido=''
        )

        assert entrega.direccion == ''
        assert isinstance(entrega.fecha_entrega, datetime)
        assert entrega.pedido == ''

    def test_entrega_model_con_fecha_pasada(self):
        fecha_pasada = datetime.now() - timedelta(days=1)
        entrega = EntregaModel(
            direccion='Calle 123',
            fecha_entrega=fecha_pasada,
            pedido='{}'
        )

        assert entrega.fecha_entrega == fecha_pasada

    def test_entrega_model_con_fecha_futura(self):
        fecha_futura = datetime.now() + timedelta(days=30)
        entrega = EntregaModel(
            direccion='Calle 123',
            fecha_entrega=fecha_futura,
            pedido='{}'
        )

        assert entrega.fecha_entrega == fecha_futura

    def test_entrega_model_con_caracteres_especiales(self):
        entrega = EntregaModel(
            direccion='Calle #123-45 & Av. Siempre Viva',
            fecha_entrega=datetime.now() + timedelta(days=1),
            pedido='{"producto": "prod-ñáéíóú", "cliente": "cli-üöä"}'
        )
        
        assert entrega.direccion == 'Calle #123-45 & Av. Siempre Viva'
        assert isinstance(entrega.fecha_entrega, datetime)
        assert isinstance(entrega.pedido, str)