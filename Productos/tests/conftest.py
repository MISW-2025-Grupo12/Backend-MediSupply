import pytest
import os
import tempfile
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Configurar SQLite para pruebas
@pytest.fixture(scope='session')
def app():
    """Crear aplicación Flask para pruebas con SQLite"""
    app = Flask(__name__)
    
    # Usar SQLite en memoria para pruebas
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['TESTING'] = True
    
    # Importar y configurar la base de datos
    from src.config.db import db
    db.init_app(app)
    
    # Crear tablas
    with app.app_context():
        db.create_all()
    
    return app

@pytest.fixture(scope='function')
def client(app):
    """Cliente de prueba"""
    return app.test_client()

@pytest.fixture(scope='function')
def db_session(app):
    """Sesión de base de datos para pruebas"""
    from src.config.db import db
    
    with app.app_context():
        # Limpiar base de datos antes de cada prueba
        db.drop_all()
        db.create_all()
        yield db
        # Limpiar después de cada prueba
        db.session.rollback()
        db.drop_all()
