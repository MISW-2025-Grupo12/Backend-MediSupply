import pytest
import sys
import os
from unittest.mock import Mock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from aplicacion.consultas.obtener_entregas import ObtenerEntregas, ObtenerEntregasHandler

class TestObtenerEntregas:
    def test_crear_consulta(self):
        consulta = ObtenerEntregas()
        assert consulta is not None

class TestObtenerEntregasHandler:
    def setup_method(self):
        self.mock_repositorio = Mock()
        self.handler = ObtenerEntregasHandler()
        self.handler.repositorio = self.mock_repositorio

    def test_handle_exitoso(self):
        consulta = ObtenerEntregas()
        self.mock_repositorio.obtener_todos.return_value = []
        
        resultado = self.handler.handle(consulta)
        
        assert resultado == []
        self.mock_repositorio.obtener_todos.assert_called_once()

    def test_handle_con_error(self):
        consulta = ObtenerEntregas()
        self.mock_repositorio.obtener_todos.side_effect = Exception("Error de base de datos")
        
        with pytest.raises(Exception):
            self.handler.handle(consulta)
