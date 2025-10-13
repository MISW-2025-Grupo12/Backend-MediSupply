import pytest
import sys
import os
from datetime import datetime, timedelta
import uuid

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from datetime import datetime
from aplicacion.mapeadores import MapeadorEntregaDTOJson, MapeadorEntrega
from aplicacion.dto import EntregaDTO
from dominio.entidades import Entrega
from dominio.objetos_valor import Direccion, FechaEntrega, ProductoID, ClienteID

class TestMapeadorEntregaDTOJson:
    def test_dto_a_externo(self):
        dto = EntregaDTO(
            id="uuid-test",
            direccion="Calle 1",
            fecha_entrega=datetime(2025, 10, 15),
            pedido={
                "id": "mock-id",
                "cliente": {"nombre": "Cliente Mock"},
                "productos": [{"nombre": "Producto Mock"}]
            }
        )

        mapeador = MapeadorEntregaDTOJson()
        externo = mapeador.dto_a_externo(dto)

        assert externo["direccion"] == "Calle 1"
        assert "pedido" in externo
        assert "productos" in externo["pedido"]

    def test_externo_a_dto(self):
        externo = {
            "id": "uuid-test",
            "direccion": "Calle 2",
            "fecha_entrega": "2025-10-15T00:00:00",
            "pedido": {
                "id": "pedido-1",
                "cliente": {"nombre": "Cliente X"},
                "productos": [{"nombre": "Prod A"}]
            }
        }

        mapeador = MapeadorEntregaDTOJson()
        dto = mapeador.externo_a_dto(externo)

        assert dto.direccion == "Calle 2"
        assert isinstance(dto.fecha_entrega, datetime)
        assert "cliente" in dto.pedido

    def test_dtos_a_externo(self):
        dto1 = EntregaDTO(
            id="uuid1",
            direccion="Calle 10",
            fecha_entrega=datetime(2025, 10, 16),
            pedido={"id": "pedido-1", "productos": []}
        )
        dto2 = EntregaDTO(
            id="uuid2",
            direccion="Calle 20",
            fecha_entrega=datetime(2025, 10, 17),
            pedido={"id": "pedido-2", "productos": []}
        )

        mapeador = MapeadorEntregaDTOJson()
        externos = [mapeador.dto_a_externo(dto) for dto in [dto1, dto2]]

        assert len(externos) == 2
        assert externos[0]["direccion"] == "Calle 10"
        assert externos[1]["direccion"] == "Calle 20"


class TestMapeadorEntrega:
    def test_entidad_a_dto(self):
        entidad = Entrega(
            id="uuid-test",
            direccion=Direccion("Calle 3"),
            fecha_entrega=FechaEntrega(datetime(2025, 10, 15)),
            producto_id=ProductoID("prod-1"),
            cliente_id=ClienteID("cli-1")
        )

        mapeador = MapeadorEntrega()
        dto = mapeador.entidad_a_dto(entidad)

        assert dto.direccion == "Calle 3"
        assert isinstance(dto.fecha_entrega, datetime)
        assert dto.pedido is None or isinstance(dto.pedido, dict)

    def test_dto_a_entidad(self):
        dto = EntregaDTO(
            id="uuid-test",
            direccion="Calle 4",
            fecha_entrega=datetime(2025, 10, 18),
            pedido={"id": "pedido-123", "productos": [{"nombre": "Paracetamol"}]}
        )

        mapeador = MapeadorEntrega()
        entidad = mapeador.dto_a_entidad(dto)

        assert entidad.direccion.valor == "Calle 4"
        assert isinstance(entidad.fecha_entrega.valor, datetime)
        assert hasattr(entidad, "producto_id")
        assert hasattr(entidad, "cliente_id")
