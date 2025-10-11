import pytest
import os
import tempfile
import sys
from unittest.mock import patch

# Agregar el directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

@pytest.fixture
def app():
    """Crear aplicación Flask para pruebas con SQLite"""
    os.environ['TESTING'] = 'True'
    from api import create_app
    app = create_app()
    
    yield app

@pytest.fixture
def client(app):
    """Cliente de prueba de Flask"""
    return app.test_client()

@pytest.fixture
def runner(app):
    """Runner de comandos de Flask"""
    return app.test_cli_runner()