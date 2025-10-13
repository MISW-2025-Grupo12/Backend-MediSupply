import pytest
import sys
import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

# Agregar el directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

class BaseTestHelper:
    """Clase base para pruebas con configuración común"""
    
    def __init__(self):
        self.app = None
        self.client = None
        self.db = None
    
    def setup_method(self, service_name='productos'):
        """Setup para cada test"""
        # Crear aplicación Flask para pruebas con SQLite
        self.app = Flask(__name__)
        
        # Usar SQLite en memoria para pruebas
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        self.app.config['TESTING'] = True
        
        # Importar y configurar la base de datos
        from config.db import db
        self.db = db
        self.db.init_app(self.app)
        
        # Crear tablas
        with self.app.app_context():
            self.db.create_all()
        
        # Crear cliente de prueba
        self.client = self.app.test_client()
    
    def teardown_method(self):
        """Cleanup después de cada test"""
        if self.app and self.db:
            with self.app.app_context():
                self.db.session.rollback()
                self.db.drop_all()
