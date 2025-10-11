import pytest
import sys
import os
from unittest.mock import Mock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from seedwork.presentacion.api import crear_blueprint


class TestPresentacionAPI:
    """Test para presentación API"""
    
    def test_crear_blueprint_exitoso(self):
        """Test creación exitosa de blueprint"""
        # Arrange & Act
        with patch('seedwork.presentacion.api.Blueprint') as mock_blueprint:
            mock_bp = Mock()
            mock_blueprint.return_value = mock_bp
            
            resultado = crear_blueprint('test', '/api/test')
            
            # Assert
            assert resultado == mock_bp
            mock_blueprint.assert_called_once_with('test', 'seedwork.presentacion.api', url_prefix='/api/test')
    
    def test_crear_blueprint_con_nombre_none(self):
        """Test crear blueprint con nombre None"""
        # Arrange & Act & Assert
        with pytest.raises(ValueError, match="'name' may not be empty"):
            crear_blueprint(None, "/test")
    
    def test_crear_blueprint_con_nombre_vacio(self):
        """Test crear blueprint con nombre vacío"""
        # Arrange & Act & Assert
        with pytest.raises(ValueError, match="'name' may not be empty"):
            crear_blueprint("", "/test")
    
    def test_crear_blueprint_ambos_parametros_none(self):
        """Test crear blueprint con ambos parámetros None"""
        # Arrange & Act & Assert
        with pytest.raises(ValueError, match="'name' may not be empty"):
            crear_blueprint(None, None)
