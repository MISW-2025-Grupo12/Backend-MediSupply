import pytest
import sys
import os
from datetime import datetime, timedelta
import uuid

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from aplicacion.mapeadores import MapeadorVisitaDTOJson, MapeadorVisitaAgregacionDTOJson, MapeadorVisita
from aplicacion.dto import VisitaDTO
from aplicacion.dto_agregacion import VisitaAgregacionDTO
from dominio.entidades import Visita
from dominio.objetos_valor import EstadoVisita, FechaProgramada, Direccion, Telefono, Descripcion


class TestMapeadorVisitaDTOJson:
    
    def setup_method(self):
        self.mapeador = MapeadorVisitaDTOJson()
        self.fecha = datetime.now()
        self.visita_id = uuid.uuid4()
    
    def test_dto_a_externo(self):
        dto = VisitaDTO(
            id=self.visita_id,
            vendedor_id="vendedor123",
            cliente_id="cliente456",
            fecha_programada=self.fecha,
            direccion="Calle 123",
            telefono="3001234567",
            estado="pendiente",
            descripcion="Visita programada"
        )
        
        resultado = self.mapeador.dto_a_externo(dto)
        
        assert resultado['id'] == str(self.visita_id)
        assert resultado['vendedor_id'] == "vendedor123"
        assert resultado['cliente_id'] == "cliente456"
        assert resultado['fecha_programada'] == self.fecha.isoformat()
        assert resultado['direccion'] == "Calle 123"
        assert resultado['telefono'] == "3001234567"
        assert resultado['estado'] == "pendiente"
        assert resultado['descripcion'] == "Visita programada"
    
    def test_externo_a_dto(self):
        externo = {
            'id': str(self.visita_id),
            'vendedor_id': 'vendedor123',
            'cliente_id': 'cliente456',
            'fecha_programada': self.fecha.isoformat(),
            'direccion': 'Calle 123',
            'telefono': '3001234567',
            'estado': 'pendiente',
            'descripcion': 'Visita programada'
        }
        
        resultado = self.mapeador.externo_a_dto(externo)
        
        assert str(resultado.id) == str(self.visita_id)
        assert resultado.vendedor_id == "vendedor123"
        assert resultado.cliente_id == "cliente456"
        assert resultado.fecha_programada == self.fecha
        assert resultado.direccion == "Calle 123"
        assert resultado.telefono == "3001234567"
        assert resultado.estado == "pendiente"
        assert resultado.descripcion == "Visita programada"


class TestMapeadorVisitaAgregacionDTOJson:
    
    def setup_method(self):
        self.mapeador = MapeadorVisitaAgregacionDTOJson()
        self.fecha = datetime.now()
        self.visita_id = uuid.uuid4()
    
    def test_agregacion_a_externo(self):
        agregacion = VisitaAgregacionDTO(
            id=self.visita_id,
            fecha_programada=self.fecha,
            direccion="Calle 123",
            telefono="3001234567",
            estado="pendiente",
            descripcion="Visita programada",
            vendedor_id="vendedor123",
            vendedor_nombre="Juan Pérez",
            vendedor_email="juan@empresa.com",
            vendedor_telefono="3001234567",
            vendedor_direccion="Calle 123",
            cliente_id="cliente456",
            cliente_nombre="Hospital San Ignacio",
            cliente_email="contacto@hospital.com",
            cliente_telefono="3115566778",
            cliente_direccion="Cra 11 #89-76"
        )
        
        resultado = self.mapeador.agregacion_a_externo(agregacion)
        
        assert resultado['id'] == str(self.visita_id)
        assert resultado['fecha_programada'] == self.fecha.isoformat()
        assert resultado['direccion'] == "Calle 123"
        assert resultado['telefono'] == "3001234567"
        assert resultado['estado'] == "pendiente"
        assert resultado['descripcion'] == "Visita programada"
        
        assert resultado['vendedor']['id'] == "vendedor123"
        assert resultado['vendedor']['nombre'] == "Juan Pérez"
        assert resultado['vendedor']['email'] == "juan@empresa.com"
        
        assert resultado['cliente']['id'] == "cliente456"
        assert resultado['cliente']['nombre'] == "Hospital San Ignacio"
        assert resultado['cliente']['email'] == "contacto@hospital.com"
    
    def test_agregaciones_a_externo(self):
        agregacion1 = VisitaAgregacionDTO(
            id=self.visita_id,
            fecha_programada=self.fecha,
            direccion="Calle 123",
            telefono="3001234567",
            estado="pendiente",
            descripcion="Visita 1",
            vendedor_id="vendedor123",
            vendedor_nombre="Juan Pérez",
            vendedor_email="juan@empresa.com",
            vendedor_telefono="3001234567",
            vendedor_direccion="Calle 123",
            cliente_id="cliente456",
            cliente_nombre="Hospital San Ignacio",
            cliente_email="contacto@hospital.com",
            cliente_telefono="3115566778",
            cliente_direccion="Cra 11 #89-76"
        )
        
        agregacion2 = VisitaAgregacionDTO(
            id=uuid.uuid4(),
            fecha_programada=self.fecha,
            direccion="Calle 456",
            telefono="3009876543",
            estado="completada",
            descripcion="Visita 2",
            vendedor_id="vendedor123",
            vendedor_nombre="Juan Pérez",
            vendedor_email="juan@empresa.com",
            vendedor_telefono="3001234567",
            vendedor_direccion="Calle 123",
            cliente_id="cliente789",
            cliente_nombre="Clínica Marly",
            cliente_email="contacto@clinica.com",
            cliente_telefono="3115566778",
            cliente_direccion="Cra 11 #89-76"
        )
        
        resultado = self.mapeador.agregaciones_a_externo([agregacion1, agregacion2])
        
        assert len(resultado) == 2
        assert resultado[0]['descripcion'] == "Visita 1"
        assert resultado[1]['descripcion'] == "Visita 2"


class TestMapeadorVisita:
    
    def setup_method(self):
        self.mapeador = MapeadorVisita()
        self.fecha = datetime.now()
    
    def test_entidad_a_dto(self):
        fecha_futura = datetime.now() + timedelta(days=1)
        entidad = Visita(
            vendedor_id="vendedor123",
            cliente_id="cliente456",
            fecha_programada=FechaProgramada(fecha_futura),
            direccion=Direccion("Calle 123"),
            telefono=Telefono("3001234567"),
            estado=EstadoVisita("pendiente"),
            descripcion=Descripcion("Visita programada")
        )
        
        resultado = self.mapeador.entidad_a_dto(entidad)
        
        assert resultado.vendedor_id == "vendedor123"
        assert resultado.cliente_id == "cliente456"
        assert resultado.fecha_programada == fecha_futura
        assert resultado.direccion == "Calle 123"
        assert resultado.telefono == "3001234567"
        assert resultado.estado == "pendiente"
        assert resultado.descripcion == "Visita programada"
