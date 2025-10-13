import pytest
import sys
import os
from unittest.mock import Mock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from seedwork.dominio.fabricas import Fabrica

class TestFabrica:
    def test_crear_fabrica_abstracta(self):
        # Fabrica es abstracta, solo verificamos que existe
        assert Fabrica is not None

    def test_fabrica_es_abstracta(self):
        assert hasattr(Fabrica, '__abstractmethods__')
        assert 'crear_objeto' in Fabrica.__abstractmethods__

    def test_fabrica_herencia(self):
        # Verificar que Fabrica puede ser heredada
        class MiFabrica(Fabrica):
            def crear_objeto(self, obj, mapeador=None):
                return {"tipo": type(obj).__name__, "datos": obj}
        
        fabrica = MiFabrica()
        resultado = fabrica.crear_objeto("test")
        
        assert resultado["tipo"] == "str"
        assert resultado["datos"] == "test"

    def test_fabrica_con_metodos_abstractos(self):
        # Verificar que se puede crear una clase que herede de Fabrica
        class TestFabrica(Fabrica):
            def crear_objeto(self, obj, mapeador=None):
                return {"tipo": type(obj).__name__, "datos": obj}
        
        fabrica = TestFabrica()
        assert fabrica is not None

    def test_fabrica_con_diferentes_tipos(self):
        class TestFabrica(Fabrica):
            def crear_objeto(self, obj, mapeador=None):
                if isinstance(obj, str):
                    return "string_creado"
                elif isinstance(obj, int):
                    return 123
                elif isinstance(obj, dict):
                    return {"creado": True}
                else:
                    return None
        
        fabrica = TestFabrica()
        
        assert fabrica.crear_objeto("test") == "string_creado"
        assert fabrica.crear_objeto(123) == 123
        assert fabrica.crear_objeto({"key": "value"}) == {"creado": True}
        assert fabrica.crear_objeto([]) is None

    def test_fabrica_con_mapeador(self):
        class TestFabrica(Fabrica):
            def crear_objeto(self, obj, mapeador=None):
                if mapeador:
                    return mapeador.mapear(obj)
                return {"original": obj}
        
        fabrica = TestFabrica()
        mock_mapeador = Mock()
        mock_mapeador.mapear.return_value = {"mapeado": True}
        
        resultado = fabrica.crear_objeto("test", mock_mapeador)
        assert resultado == {"mapeado": True}
        mock_mapeador.mapear.assert_called_once_with("test")

    def test_fabrica_sin_mapeador(self):
        class TestFabrica(Fabrica):
            def crear_objeto(self, obj, mapeador=None):
                return {"original": obj}
        
        fabrica = TestFabrica()
        resultado = fabrica.crear_objeto("test")
        assert resultado == {"original": "test"}

    def test_fabrica_con_metodos_personalizados(self):
        class TestFabrica(Fabrica):
            def __init__(self):
                self.contador = 0
            
            def crear_objeto(self, obj, mapeador=None):
                self.contador += 1
                return {
                    "objeto": obj,
                    "contador": self.contador
                }
            
            def reset_contador(self):
                self.contador = 0
        
        fabrica = TestFabrica()
        
        resultado1 = fabrica.crear_objeto("test1")
        resultado2 = fabrica.crear_objeto("test2")
        
        assert resultado1["contador"] == 1
        assert resultado2["contador"] == 2
        
        fabrica.reset_contador()
        resultado3 = fabrica.crear_objeto("test3")
        assert resultado3["contador"] == 1

    def test_fabrica_con_validacion(self):
        class TestFabrica(Fabrica):
            def crear_objeto(self, obj, mapeador=None):
                if obj is None:
                    raise ValueError("Objeto no puede ser None")
                
                if isinstance(obj, str) and len(obj) == 0:
                    raise ValueError("String no puede estar vacío")
                
                return {"objeto": obj}
        
        fabrica = TestFabrica()
        
        # Caso válido
        resultado = fabrica.crear_objeto("test")
        assert resultado["objeto"] == "test"
        
        # Caso inválido - objeto None
        with pytest.raises(ValueError, match="Objeto no puede ser None"):
            fabrica.crear_objeto(None)
        
        # Caso inválido - string vacío
        with pytest.raises(ValueError, match="String no puede estar vacío"):
            fabrica.crear_objeto("")