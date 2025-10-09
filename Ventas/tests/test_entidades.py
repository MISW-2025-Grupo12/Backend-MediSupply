import pytest
import sys
import os
from datetime import datetime, timedelta
import uuid

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from dominio.entidades import Visita
from dominio.objetos_valor import EstadoVisita, FechaProgramada, Direccion, Telefono, Descripcion


class TestVisita:
    
    def setup_method(self):
        self.fecha_futura = datetime.now() + timedelta(days=1)
        self.vendedor_id = str(uuid.uuid4())
        self.cliente_id = str(uuid.uuid4())
    
    def test_crear_visita_exitosa(self):
        visita = Visita(
            vendedor_id=self.vendedor_id,
            cliente_id=self.cliente_id,
            fecha_programada=FechaProgramada(self.fecha_futura),
            direccion=Direccion("Calle 123 #45-67"),
            telefono=Telefono("3001234567"),
            estado=EstadoVisita("pendiente"),
            descripcion=Descripcion("Visita programada")
        )
        
        assert visita.vendedor_id == self.vendedor_id
        assert visita.cliente_id == self.cliente_id
        assert visita.fecha_programada.fecha == self.fecha_futura
        assert visita.direccion.direccion == "Calle 123 #45-67"
        assert visita.telefono.telefono == "3001234567"
        assert visita.estado.estado == "pendiente"
        assert visita.descripcion.descripcion == "Visita programada"
        assert visita.id is not None
    
    def test_disparar_evento_creacion(self):
        visita = Visita(
            vendedor_id=self.vendedor_id,
            cliente_id=self.cliente_id,
            fecha_programada=FechaProgramada(self.fecha_futura),
            direccion=Direccion("Calle 123 #45-67"),
            telefono=Telefono("3001234567"),
            estado=EstadoVisita("pendiente"),
            descripcion=Descripcion("Visita programada")
        )
        
        evento = visita.disparar_evento_creacion()
        
        assert evento.visita_id == visita.id
        assert evento.vendedor_id == self.vendedor_id
        assert evento.cliente_id == self.cliente_id
        assert evento.fecha_programada == self.fecha_futura
        assert evento.direccion == "Calle 123 #45-67"
        assert evento.telefono == "3001234567"
        assert evento.estado == "pendiente"
        assert evento.descripcion == "Visita programada"
