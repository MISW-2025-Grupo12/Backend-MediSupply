import pytest
import os
import sys
import tempfile

# Configurar el path para importar los módulos
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.api import create_app

@pytest.fixture(scope='session')
def app():
    """Crear aplicación Flask para pruebas"""
    # Configurar variable de entorno para modo de pruebas
    os.environ['TESTING'] = 'True'
    
    # Crear aplicación
    app = create_app()
    
    yield app

@pytest.fixture(scope='function')
def client(app):
    """Cliente de prueba Flask"""
    return app.test_client()

@pytest.fixture(scope='function')
def app_context(app):
    """Contexto de aplicación Flask para pruebas"""
    with app.app_context():
        yield app