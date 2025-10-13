import pytest
import sys
import os
from unittest.mock import Mock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from seedwork.dominio.reglas import ReglaNegocio, IdEntidadEsInmutable

class TestReglaNegocio:
    def test_crear_regla_negocio_abstracta(self):
        # ReglaNegocio es abstracta, solo verificamos que existe
        assert ReglaNegocio is not None
        assert hasattr(ReglaNegocio, 'es_valido')

    def test_regla_negocio_es_abstracta(self):
        assert hasattr(ReglaNegocio, '__abstractmethods__')
        assert 'es_valido' in ReglaNegocio.__abstractmethods__

class TestIdEntidadEsInmutable:
    def test_crear_regla_con_entidad_sin_id(self):
        entidad = Mock()
        entidad._id = None
        
        regla = IdEntidadEsInmutable(entidad)
        assert regla.es_valido() == True

    def test_crear_regla_con_entidad_con_id(self):
        entidad = Mock()
        entidad._id = "test-id"
        
        regla = IdEntidadEsInmutable(entidad)
        assert regla.es_valido() == False

    def test_crear_regla_con_entidad_sin_atributo_id(self):
        entidad = Mock()
        # No tiene atributo _id
        del entidad._id  # Asegurar que no tiene _id
        
        regla = IdEntidadEsInmutable(entidad)
        assert regla.es_valido() == True

    def test_crear_regla_con_mensaje_personalizado(self):
        entidad = Mock()
        entidad._id = "test-id"
        
        mensaje = "ID personalizado no puede cambiar"
        regla = IdEntidadEsInmutable(entidad, mensaje)
        assert regla.mensaje_error() == mensaje

    def test_crear_regla_con_mensaje_default(self):
        entidad = Mock()
        entidad._id = "test-id"
        
        regla = IdEntidadEsInmutable(entidad)
        assert regla.mensaje_error() == "El identificador de la entidad debe ser Inmutable"

    def test_regla_con_entidad_real(self):
        class TestEntidad:
            def __init__(self):
                self._id = None
        
        entidad = TestEntidad()
        regla = IdEntidadEsInmutable(entidad)
        assert regla.es_valido() == True
        
        entidad._id = "test-id"
        assert regla.es_valido() == False

    def test_regla_con_entidad_con_excepcion(self):
        entidad = Mock()
        # Simular que hasattr lanza excepción
        def mock_hasattr(obj, name):
            if name == '_id':
                raise AttributeError("No attribute")
            return hasattr(obj, name)
        
        with patch('builtins.hasattr', side_effect=mock_hasattr):
            regla = IdEntidadEsInmutable(entidad)
            assert regla.es_valido() == True
