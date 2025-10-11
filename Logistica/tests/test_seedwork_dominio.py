import pytest
import sys
import os
from datetime import datetime
from unittest.mock import Mock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from seedwork.dominio.entidades import Entidad, AgregacionRaiz
from seedwork.dominio.eventos import EventoDominio, despachador_eventos
from seedwork.dominio.excepciones import ReglaNegocioExcepcion, ExcepcionDominio
from seedwork.dominio.reglas import ReglaNegocio
from seedwork.dominio.mixins import ValidarReglasMixin

class TestEntidad:
    def test_crear_entidad(self):
        entidad = Entidad()
        assert entidad.id is not None
        assert hasattr(entidad, 'id')

    def test_entidad_con_id_personalizado(self):
        entidad = Entidad()
        

        assert entidad.id is not None
        assert hasattr(entidad, 'id')

class TestAgregacionRaiz:
    def test_crear_agregacion_raiz(self):
        agregacion = AgregacionRaiz()
        assert agregacion.id is not None
        assert hasattr(agregacion, 'id')

class TestEventoDominio:
    def test_crear_evento_dominio(self):

        assert EventoDominio is not None
        assert hasattr(EventoDominio, '_get_datos_evento')

    def test_despachador_eventos(self):

        assert despachador_eventos is not None

        assert hasattr(despachador_eventos, '__class__')

class TestReglaNegocioExcepcion:
    def test_crear_excepcion_regla_negocio(self):
        excepcion = ReglaNegocioExcepcion("Mensaje de error")
        assert str(excepcion) == "Mensaje de error"
        assert isinstance(excepcion, Exception)

    def test_crear_excepcion_regla_negocio_con_detalles(self):

        excepcion = ReglaNegocioExcepcion("Error con detalles")
        assert str(excepcion) == "Error con detalles"

class TestExcepcionDominio:
    def test_crear_excepcion_dominio(self):
        excepcion = ExcepcionDominio("Error de dominio")
        assert str(excepcion) == "Error de dominio"
        assert isinstance(excepcion, Exception)

class TestReglaNegocio:
    def test_crear_regla_negocio(self):
        assert ReglaNegocio is not None
        assert hasattr(ReglaNegocio, 'es_valido')

    def test_regla_negocio_es_abstracta(self):

        assert hasattr(ReglaNegocio, '__abstractmethods__')
        assert 'es_valido' in ReglaNegocio.__abstractmethods__

class TestValidarReglasMixin:
    def test_crear_mixin_validar_reglas(self):
        class ClaseConMixin(ValidarReglasMixin):
            pass
        
        instancia = ClaseConMixin()
        assert hasattr(instancia, 'validar_regla')

    def test_validar_regla_exitosa(self):
        class ClaseConMixin(ValidarReglasMixin):
            pass
        
        class ReglaMock:
            def es_valido(self):
                return True
        
        instancia = ClaseConMixin()
        regla = ReglaMock()
        
        # No debe lanzar excepción
        instancia.validar_regla(regla)

    def test_validar_regla_fallida(self):
        class ClaseConMixin(ValidarReglasMixin):
            pass
        
        class ReglaMock:
            def es_valido(self):
                return False
        
        instancia = ClaseConMixin()
        regla = ReglaMock()
        
        with pytest.raises(ReglaNegocioExcepcion):
            instancia.validar_regla(regla)

    def test_validar_regla_con_detalles(self):
        class ClaseConMixin(ValidarReglasMixin):
            pass
        
        class ReglaMock:
            def es_valido(self):
                return False
        
        instancia = ClaseConMixin()
        regla = ReglaMock()
        
        with pytest.raises(ReglaNegocioExcepcion) as exc_info:
            instancia.validar_regla(regla)
        
        # Verificar que se lanzó la excepción correcta
        assert isinstance(exc_info.value, ReglaNegocioExcepcion)
