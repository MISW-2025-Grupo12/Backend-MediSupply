import pytest
import sys
import os
from datetime import datetime
from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from dominio.entidades import Entrega
from dominio.objetos_valor import Direccion, FechaEntrega, ProductoID, ClienteID

class TestEntrega:
    def test_crear_entrega_basica(self):
        entrega = Entrega()
        assert entrega.id is not None
        assert isinstance(entrega.direccion, Direccion)
        assert isinstance(entrega.fecha_entrega, FechaEntrega)
        assert isinstance(entrega.producto_id, ProductoID)
        assert isinstance(entrega.cliente_id, ClienteID)

    def test_crear_entrega_con_datos(self):
        direccion = Direccion("Calle 123 #45-67")
        fecha = datetime.now()
        fecha_entrega = FechaEntrega(fecha)
        producto_id = ProductoID("producto-123")
        cliente_id = ClienteID("cliente-456")
        
        entrega = Entrega(
            direccion=direccion,
            fecha_entrega=fecha_entrega,
            producto_id=producto_id,
            cliente_id=cliente_id
        )
        
        assert entrega.direccion == direccion
        assert entrega.fecha_entrega == fecha_entrega
        assert entrega.producto_id == producto_id
        assert entrega.cliente_id == cliente_id

    @patch('builtins.print')
    def test_disparar_evento_creacion(self, mock_print):
        entrega = Entrega()
        entrega.disparar_evento_creacion()
        
        mock_print.assert_called_once()
        assert "Entrega creada:" in str(mock_print.call_args)
