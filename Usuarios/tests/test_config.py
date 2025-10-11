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
    # Crear archivo temporal para SQLite
    db_fd, db_path = tempfile.mkstemp()
    
    # Mockear la función init_db para usar SQLite
    with patch('src.config.db.init_db') as mock_init_db:
        # Importar solo la función create_app, no el módulo completo
        from api import create_app
        app = create_app()
        
        # Configurar SQLite para las pruebas
        app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
        app.config['TESTING'] = True
        app.config['WTF_CSRF_ENABLED'] = False
        
        # Inicializar la base de datos con SQLite
        from src.config.db import db
        db.init_app(app)
        
        with app.app_context():
            db.create_all()
    
    yield app
    
    # Limpiar después de las pruebas
    os.close(db_fd)
    os.unlink(db_path)

@pytest.fixture
def client(app):
    """Cliente de prueba de Flask"""
    return app.test_client()

@pytest.fixture
def runner(app):
    """Runner de comandos de Flask"""
    return app.test_cli_runner()
