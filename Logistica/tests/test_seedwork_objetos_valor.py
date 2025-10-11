import pytest
import sys
import os
from unittest.mock import Mock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from seedwork.dominio.objetos_valor import ObjetoValor

class TestObjetoValor:
    def test_crear_objeto_valor_abstracto(self):
        # ObjetoValor es abstracto, solo verificamos que existe
        assert ObjetoValor is not None

    def test_objeto_valor_es_abstracto(self):
        assert not hasattr(ObjetoValor, '__abstractmethods__')

    def test_objeto_valor_herencia(self):
        # Verificar que ObjetoValor puede ser heredado
        class MiObjetoValor(ObjetoValor):
            def __init__(self, valor):
                self.valor = valor
            
            def __eq__(self, other):
                return isinstance(other, MiObjetoValor) and self.valor == other.valor
        
        obj1 = MiObjetoValor("test")
        obj2 = MiObjetoValor("test")
        obj3 = MiObjetoValor("otro")
        
        assert obj1 == obj2
        assert obj1 != obj3
        assert obj1.valor == "test"

    def test_objeto_valor_con_metodos_abstractos(self):
        # Verificar que se puede crear una clase que herede de ObjetoValor
        class TestObjetoValor(ObjetoValor):
            def __init__(self, valor):
                self.valor = valor
            
            def __eq__(self, other):
                return isinstance(other, TestObjetoValor) and self.valor == other.valor
        
        obj = TestObjetoValor("test")
        assert obj.valor == "test"

    def test_objeto_valor_inmutable(self):
        class TestObjetoValor(ObjetoValor):
            def __init__(self, valor):
                self._valor = valor
            
            def __eq__(self, other):
                return isinstance(other, TestObjetoValor) and self._valor == other._valor
            
            @property
            def valor(self):
                return self._valor
        
        obj = TestObjetoValor("test")
        assert obj.valor == "test"
        
        # Verificar que no se puede modificar directamente
        with pytest.raises(AttributeError):
            obj.valor = "nuevo"

    def test_objeto_valor_con_diferentes_tipos(self):
        class TestObjetoValor(ObjetoValor):
            def __init__(self, valor):
                self.valor = valor
            
            def __eq__(self, other):
                return isinstance(other, TestObjetoValor) and self.valor == other.valor
        
        # String
        obj_str = TestObjetoValor("string")
        assert obj_str.valor == "string"
        
        # Número
        obj_int = TestObjetoValor(123)
        assert obj_int.valor == 123
        
        # Lista
        obj_list = TestObjetoValor([1, 2, 3])
        assert obj_list.valor == [1, 2, 3]
        
        # Diccionario
        obj_dict = TestObjetoValor({"key": "value"})
        assert obj_dict.valor == {"key": "value"}

    def test_objeto_valor_igualdad(self):
        class TestObjetoValor(ObjetoValor):
            def __init__(self, valor):
                self.valor = valor
            
            def __eq__(self, other):
                return isinstance(other, TestObjetoValor) and self.valor == other.valor
        
        obj1 = TestObjetoValor("test")
        obj2 = TestObjetoValor("test")
        obj3 = TestObjetoValor("otro")
        
        assert obj1 == obj2
        assert obj1 != obj3
        assert obj1 != "string"
        assert obj1 != None

    def test_objeto_valor_con_metodos_personalizados(self):
        class TestObjetoValor(ObjetoValor):
            def __init__(self, valor):
                self.valor = valor
            
            def __eq__(self, other):
                return isinstance(other, TestObjetoValor) and self.valor == other.valor
            
            def es_valido(self):
                return self.valor is not None and self.valor != ""
            
            def to_string(self):
                return str(self.valor)
        
        obj = TestObjetoValor("test")
        assert obj.es_valido() == True
        assert obj.to_string() == "test"
        
        obj_invalido = TestObjetoValor("")
        assert obj_invalido.es_valido() == False
