import pytest
import sys
import os
from datetime import datetime, timedelta
import uuid

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from aplicacion.mapeadores import MapeadorEntregaDTOJson, MapeadorEntrega
from aplicacion.dto import EntregaDTO
from dominio.entidades import Entrega
from dominio.objetos_valor import Direccion, FechaEntrega, ProductoID, ClienteID

class TestMapeadorEntregaDTOJson:
    def setup_method(self):
        self.mapeador = MapeadorEntregaDTOJson()
        self.entrega_id = uuid.uuid4()
        self.fecha = datetime.now() + timedelta(days=1)

    def test_dto_a_externo(self):
        dto = EntregaDTO(
            id=self.entrega_id,
            direccion="Calle 123 #45-67",
            fecha_entrega=self.fecha,
            producto_id="producto-123",
            cliente_id="cliente-456"
        )
        
        resultado = self.mapeador.dto_a_externo(dto)
        
        assert resultado['id'] == str(self.entrega_id)
        assert resultado['direccion'] == "Calle 123 #45-67"
        assert resultado['fecha_entrega'] == self.fecha.isoformat()
        assert resultado['producto_id'] == "producto-123"
        assert resultado['cliente_id'] == "cliente-456"

    def test_externo_a_dto(self):
        externo = {
            'id': str(self.entrega_id),
            'direccion': 'Calle 123 #45-67',
            'fecha_entrega': self.fecha.isoformat(),
            'producto_id': 'producto-123',
            'cliente_id': 'cliente-456'
        }
        
        resultado = self.mapeador.externo_a_dto(externo)
        
        assert str(resultado.id) == str(self.entrega_id)
        assert resultado.direccion == "Calle 123 #45-67"
        assert resultado.fecha_entrega == self.fecha
        assert resultado.producto_id == "producto-123"
        assert resultado.cliente_id == "cliente-456"

    def test_dtos_a_externo(self):
        dto1 = EntregaDTO(
            id=self.entrega_id,
            direccion="Calle 123",
            fecha_entrega=self.fecha,
            producto_id="producto-1",
            cliente_id="cliente-1"
        )
        dto2 = EntregaDTO(
            id=uuid.uuid4(),
            direccion="Calle 456",
            fecha_entrega=self.fecha,
            producto_id="producto-2",
            cliente_id="cliente-2"
        )
        
        resultado1 = self.mapeador.dto_a_externo(dto1)
        resultado2 = self.mapeador.dto_a_externo(dto2)
        
        assert resultado1['direccion'] == "Calle 123"
        assert resultado2['direccion'] == "Calle 456"

class TestMapeadorEntrega:
    def setup_method(self):
        self.mapeador = MapeadorEntrega()
        self.fecha_futura = datetime.now() + timedelta(days=1)

    def test_entidad_a_dto(self):
        entidad = Entrega(
            direccion=Direccion("Calle 123 #45-67"),
            fecha_entrega=FechaEntrega(self.fecha_futura),
            producto_id=ProductoID("producto-123"),
            cliente_id=ClienteID("cliente-456")
        )
        
        resultado = self.mapeador.entidad_a_dto(entidad)
        
        assert resultado.direccion == "Calle 123 #45-67"
        assert resultado.fecha_entrega == self.fecha_futura
        assert resultado.producto_id == "producto-123"
        assert resultado.cliente_id == "cliente-456"
