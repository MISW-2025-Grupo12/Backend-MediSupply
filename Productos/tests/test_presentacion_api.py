import pytest
import sys
import os
from unittest.mock import Mock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from seedwork.presentacion.api import crear_blueprint


class TestPresentacionAPI:
    """Test para presentación API"""
    
    def test_crear_blueprint_funcion_existe(self):
        """Test que la función crear_blueprint existe"""
        # Arrange & Act & Assert
        assert callable(crear_blueprint)
    
    def test_crear_blueprint_retorna_blueprint(self):
        """Test que crear_blueprint retorna un Blueprint"""
        # Arrange & Act
        bp = crear_blueprint("test", "/test")
        
        # Assert
        assert bp is not None
        assert hasattr(bp, 'name')
        assert hasattr(bp, 'url_prefix')
        assert hasattr(bp, 'register_blueprint')
    
    def test_crear_blueprint_con_parametros(self):
        """Test crear_blueprint con parámetros"""
        # Arrange
        nombre = "test_bp"
        url_prefix = "/test"
        
        # Act
        bp = crear_blueprint(nombre, url_prefix)
        
        # Assert
        assert bp is not None
        assert bp.name == nombre
        assert bp.url_prefix == url_prefix
    
    def test_crear_blueprint_es_reutilizable(self):
        """Test que crear_blueprint puede ser llamado múltiples veces"""
        # Arrange & Act
        bp1 = crear_blueprint("bp1", "/test1")
        bp2 = crear_blueprint("bp2", "/test2")
        
        # Assert
        assert bp1 is not None
        assert bp2 is not None
        assert bp1.name == "bp1"
        assert bp2.name == "bp2"
        assert bp1.url_prefix == "/test1"
        assert bp2.url_prefix == "/test2"
    
    def test_crear_blueprint_con_nombre_none(self):
        """Test crear_blueprint con nombre None"""
        # Arrange & Act & Assert
        with pytest.raises(ValueError, match="'name' may not be empty"):
            crear_blueprint(None, "/test")
    
    def test_crear_blueprint_con_url_prefix_none(self):
        """Test crear_blueprint con url_prefix None"""
        # Arrange & Act
        bp = crear_blueprint("test_bp", None)
        
        # Assert
        assert bp is not None
        assert bp.name == "test_bp"
    
    def test_crear_blueprint_ambos_parametros_none(self):
        """Test crear_blueprint con ambos parámetros None"""
        # Arrange & Act & Assert
        with pytest.raises(ValueError, match="'name' may not be empty"):
            crear_blueprint(None, None)
