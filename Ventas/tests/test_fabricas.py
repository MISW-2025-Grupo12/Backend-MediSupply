import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from dominio.fabricas import FabricaVisita
from dominio.reglas import VendedorIdNoPuedeSerVacio


class TestFabricaVisita:
    
    def setup_method(self):
        self.fabrica = FabricaVisita()
    
    def test_validar_regla_exitosa(self):
        regla = VendedorIdNoPuedeSerVacio("123")
        self.fabrica.validar_regla(regla)
    
    def test_validar_regla_falla(self):
        regla = VendedorIdNoPuedeSerVacio("")
        with pytest.raises(ValueError, match="VendedorIdNoPuedeSerVacio"):
            self.fabrica.validar_regla(regla)
