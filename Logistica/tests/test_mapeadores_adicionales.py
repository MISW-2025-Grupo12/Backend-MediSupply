import pytest
import sys
import os
from datetime import datetime, timedelta
from unittest.mock import Mock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from aplicacion.mapeadores import MapeadorEntregaDTOJson, MapeadorEntrega
from aplicacion.dto import EntregaDTO
from dominio.entidades import Entrega
from dominio.objetos_valor import Direccion, FechaEntrega, ProductoID, ClienteID

class TestMapeadorEntregaDTOJsonAdicionales:
    def setup_method(self):
        self.mapeador = MapeadorEntregaDTOJson()
        self.fecha = datetime.now() + timedelta(days=1)

    def test_dto_a_externo_con_id_none(self):
        dto = EntregaDTO(
            id=None,
            direccion="Calle 123 #45-67",
            fecha_entrega=self.fecha,
            producto_id="producto-123",
            cliente_id="cliente-456"
        )
        
        resultado = self.mapeador.dto_a_externo(dto)
        
        assert resultado['id'] == "None"
        assert resultado['direccion'] == "Calle 123 #45-67"
        assert resultado['fecha_entrega'] == self.fecha.isoformat()
        assert resultado['producto_id'] == "producto-123"
        assert resultado['cliente_id'] == "cliente-456"

    def test_externo_a_dto_con_id_none(self):
        externo = {
            'id': None,
            'direccion': 'Calle 123 #45-67',
            'fecha_entrega': self.fecha.isoformat(),
            'producto_id': 'producto-123',
            'cliente_id': 'cliente-456'
        }
        
        resultado = self.mapeador.externo_a_dto(externo)
        
        assert resultado.id is None
        assert resultado.direccion == "Calle 123 #45-67"
        assert resultado.fecha_entrega == self.fecha
        assert resultado.producto_id == "producto-123"
        assert resultado.cliente_id == "cliente-456"

    def test_dto_a_externo_con_datos_vacios(self):
        dto = EntregaDTO(
            id=None,
            direccion="",
            fecha_entrega=datetime.now(),
            producto_id="",
            cliente_id=""
        )
        
        resultado = self.mapeador.dto_a_externo(dto)
        
        assert resultado['direccion'] == ""
        assert resultado['producto_id'] == ""
        assert resultado['cliente_id'] == ""

    def test_externo_a_dto_con_datos_vacios(self):
        externo = {
            'id': None,
            'direccion': '',
            'fecha_entrega': datetime.now().isoformat(),
            'producto_id': '',
            'cliente_id': ''
        }
        
        resultado = self.mapeador.externo_a_dto(externo)
        
        assert resultado.direccion == ""
        assert resultado.producto_id == ""
        assert resultado.cliente_id == ""

class TestMapeadorEntregaAdicionales:
    def setup_method(self):
        self.mapeador = MapeadorEntrega()
        self.fecha_futura = datetime.now() + timedelta(days=1)

    def test_entidad_a_dto_con_datos_vacios(self):
        entidad = Entrega(
            direccion=Direccion(""),
            fecha_entrega=FechaEntrega(datetime.now()),
            producto_id=ProductoID(""),
            cliente_id=ClienteID("")
        )
        
        resultado = self.mapeador.entidad_a_dto(entidad)
        
        assert resultado.direccion == ""
        assert resultado.producto_id == ""
        assert resultado.cliente_id == ""

    def test_entidad_a_dto_con_datos_none(self):
        # Crear entidad con valores por defecto
        entidad = Entrega()
        
        resultado = self.mapeador.entidad_a_dto(entidad)
        
        assert isinstance(resultado, EntregaDTO)
        assert hasattr(resultado, 'direccion')
        assert hasattr(resultado, 'fecha_entrega')
        assert hasattr(resultado, 'producto_id')
        assert hasattr(resultado, 'cliente_id')

    def test_entidad_a_dto_con_fecha_pasada(self):
        fecha_pasada = datetime.now() - timedelta(days=1)
        entidad = Entrega(
            direccion=Direccion("Calle 123"),
            fecha_entrega=FechaEntrega(fecha_pasada),
            producto_id=ProductoID("prod-123"),
            cliente_id=ClienteID("cliente-456")
        )
        
        resultado = self.mapeador.entidad_a_dto(entidad)
        
        assert resultado.direccion == "Calle 123"
        assert resultado.fecha_entrega == fecha_pasada
        assert resultado.producto_id == "prod-123"
        assert resultado.cliente_id == "cliente-456"

    def test_entidad_a_dto_con_caracteres_especiales(self):
        direccion_especial = "Calle 123 #45-67, Apt 8B, Bogotá D.C."
        entidad = Entrega(
            direccion=Direccion(direccion_especial),
            fecha_entrega=FechaEntrega(self.fecha_futura),
            producto_id=ProductoID("prod-123-abc"),
            cliente_id=ClienteID("cliente-456-xyz")
        )
        
        resultado = self.mapeador.entidad_a_dto(entidad)
        
        assert resultado.direccion == direccion_especial
        assert resultado.producto_id == "prod-123-abc"
        assert resultado.cliente_id == "cliente-456-xyz"
