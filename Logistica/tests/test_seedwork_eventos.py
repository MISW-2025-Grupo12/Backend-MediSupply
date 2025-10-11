import pytest
import sys
import os
from unittest.mock import Mock, patch
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from seedwork.dominio.eventos import EventoDominio, DespachadorEventos
from seedwork.aplicacion.eventos import DespachadorEventos as AppDespachadorEventos, ejecutar_evento

class TestEventoDominio:
    def test_crear_evento_dominio_abstracto(self):
        # EventoDominio es abstracto, solo verificamos que existe
        assert EventoDominio is not None
        assert hasattr(EventoDominio, '_get_datos_evento')

class TestDespachadorEventos:
    def setup_method(self):
        self.despachador = DespachadorEventos()

    def test_crear_despachador(self):
        assert self.despachador is not None

    @patch('seedwork.dominio.eventos.logger')
    def test_publicar_evento_exitoso(self, mock_logger):
        evento = Mock()
        evento.__class__.__name__ = "TestEvento"
        evento._get_datos_evento.return_value = {"test": "data"}
        
        self.despachador.publicar(evento)
        
        mock_logger.info.assert_called()

    @patch('seedwork.dominio.eventos.logger')
    def test_publicar_evento_con_error(self, mock_logger):
        evento = Mock()
        evento.__class__.__name__ = "TestEvento"
        evento._get_datos_evento.side_effect = Exception("Error en evento")
        
        self.despachador.publicar(evento)
        
        mock_logger.error.assert_called()

    def test_publicar_evento_none(self):
        # No debería lanzar excepción
        self.despachador.publicar(None)

    def test_publicar_evento_sin_datos(self):
        evento = Mock()
        evento.__class__.__name__ = "TestEvento"
        evento._get_datos_evento.return_value = None
        
        # No debería lanzar excepción
        self.despachador.publicar(evento)

class TestAppDespachadorEventos:
    def setup_method(self):
        self.despachador = AppDespachadorEventos()

    def test_crear_despachador(self):
        assert self.despachador is not None

    def test_registrar_manejador(self):
        manejador = Mock()
        self.despachador.registrar_manejador('TestEvento', manejador)
        assert 'TestEvento' in self.despachador._manejadores
        assert manejador in self.despachador._manejadores['TestEvento']

    def test_registrar_publicador(self):
        publicador = Mock()
        self.despachador.registrar_publicador(publicador)
        assert publicador in self.despachador._publicadores

    def test_registrar_multiple_manejadores(self):
        manejador1 = Mock()
        manejador2 = Mock()
        self.despachador.registrar_manejador('TestEvento', manejador1)
        self.despachador.registrar_manejador('TestEvento', manejador2)
        assert len(self.despachador._manejadores['TestEvento']) == 2

class TestEjecutarEvento:
    def test_ejecutar_evento_no_implementado(self):
        evento = Mock()
        evento.__class__.__name__ = "EventoNoImplementado"
        
        with pytest.raises(NotImplementedError):
            ejecutar_evento(evento)

    def test_ejecutar_evento_con_tipo(self):
        evento = Mock()
        evento.__class__.__name__ = "TestEvento"
        
        with pytest.raises(NotImplementedError, match="No existe implementacion para el evento de tipo: TestEvento"):
            ejecutar_evento(evento)
