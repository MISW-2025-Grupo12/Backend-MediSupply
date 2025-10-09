import pytest
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from dominio.objetos_valor import Direccion, FechaEntrega, ProductoID, ClienteID

class TestDireccion:
    def test_crear_direccion_valida(self):
        direccion = Direccion("Calle 123 #45-67")
        assert direccion.valor == "Calle 123 #45-67"

    def test_direccion_inmutable(self):
        direccion = Direccion("Calle 123 #45-67")
        with pytest.raises(AttributeError):
            direccion.valor = "Nueva dirección"

class TestFechaEntrega:
    def test_crear_fecha_entrega_valida(self):
        fecha = datetime.now()
        fecha_entrega = FechaEntrega(fecha)
        assert fecha_entrega.valor == fecha

    def test_fecha_entrega_inmutable(self):
        fecha = datetime.now()
        fecha_entrega = FechaEntrega(fecha)
        with pytest.raises(AttributeError):
            fecha_entrega.valor = datetime.now()

class TestProductoID:
    def test_crear_producto_id_valido(self):
        producto_id = ProductoID("producto-123")
        assert producto_id.valor == "producto-123"

    def test_producto_id_inmutable(self):
        producto_id = ProductoID("producto-123")
        with pytest.raises(AttributeError):
            producto_id.valor = "nuevo-producto"

class TestClienteID:
    def test_crear_cliente_id_valido(self):
        cliente_id = ClienteID("cliente-456")
        assert cliente_id.valor == "cliente-456"

    def test_cliente_id_inmutable(self):
        cliente_id = ClienteID("cliente-456")
        with pytest.raises(AttributeError):
            cliente_id.valor = "nuevo-cliente"
