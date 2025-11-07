"""Tests para normalización de nombres en ServicioProveedores"""
import pytest
import sys
import os
from unittest.mock import Mock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from infraestructura.servicio_proveedores import ServicioProveedores


class TestServicioProveedoresNormalizacion:
    """Tests para la normalización de nombres de proveedores"""
    
    @pytest.fixture
    def servicio(self):
        """Crea una instancia del servicio"""
        return ServicioProveedores(base_url='http://localhost:5001/usuarios/api')
    
    def test_normalizar_nombre_elimina_espacios(self, servicio):
        """Test que la normalización elimina espacios"""
        nombre = "Distribuidora MediPro S.A.S."
        normalizado = servicio._normalizar_nombre(nombre)
        assert " " not in normalizado
    
    def test_normalizar_nombre_elimina_puntos(self, servicio):
        """Test que la normalización elimina puntos"""
        nombre = "Distribuidora MediPro S.A.S."
        normalizado = servicio._normalizar_nombre(nombre)
        assert "." not in normalizado
    
    def test_normalizar_nombre_minusculas(self, servicio):
        """Test que la normalización convierte a minúsculas"""
        nombre = "DISTRIBUIDORA MEDIPRO"
        normalizado = servicio._normalizar_nombre(nombre)
        assert normalizado == normalizado.lower()
    
    def test_normalizar_nombre_ignora_puntuacion(self, servicio):
        """Test que normaliza nombres con/sin puntuación de la misma forma"""
        nombre1 = "Distribuidora MediPro S.A.S."
        nombre2 = "Distribuidora MediPro S.A.S"
        
        norm1 = servicio._normalizar_nombre(nombre1)
        norm2 = servicio._normalizar_nombre(nombre2)
        
        assert norm1 == norm2
    
    @patch('infraestructura.servicio_proveedores.requests.get')
    def test_obtener_proveedor_por_nombre_formato_paginado(self, mock_get, servicio):
        """Test obtener proveedor con formato paginado"""
        # Mock respuesta paginada
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'items': [
                {'id': '123', 'nombre': 'Distribuidora MediPro S.A.S'}
            ],
            'pagination': {
                'page': 1,
                'page_size': 100,
                'total_items': 1,
                'total_pages': 1,
                'has_next': False,
                'has_prev': False
            }
        }
        mock_get.return_value = mock_response
        
        resultado = servicio.obtener_proveedor_por_nombre("Distribuidora MediPro S.A.S.")
        
        assert resultado is not None
        assert resultado['id'] == '123'
        mock_get.assert_called_once()
    
    @patch('infraestructura.servicio_proveedores.requests.get')
    def test_obtener_proveedor_por_nombre_formato_lista(self, mock_get, servicio):
        """Test obtener proveedor con formato de lista"""
        # Mock respuesta como lista
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {'id': '123', 'nombre': 'Distribuidora MediPro S.A.S'}
        ]
        mock_get.return_value = mock_response
        
        resultado = servicio.obtener_proveedor_por_nombre("Distribuidora MediPro S.A.S.")
        
        assert resultado is not None
        assert resultado['id'] == '123'
    
    @patch('infraestructura.servicio_proveedores.requests.get')
    def test_obtener_proveedor_por_nombre_no_encontrado(self, mock_get, servicio):
        """Test cuando el proveedor no se encuentra"""
        # Mock respuesta vacía
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'items': [],
            'pagination': {
                'page': 1,
                'page_size': 100,
                'total_items': 0,
                'total_pages': 1,
                'has_next': False,
                'has_prev': False
            }
        }
        mock_get.return_value = mock_response
        
        resultado = servicio.obtener_proveedor_por_nombre("Proveedor Inexistente")
        
        assert resultado is None

