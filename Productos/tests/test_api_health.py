import pytest
import sys
import os
import json
from flask import Flask

# Agregar el directorio de utilidades de prueba al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
sys.path.insert(0, os.path.dirname(__file__))

from test_utils import BaseTestHelper


class TestAPIHealth:
    
    def setup_method(self):
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
    
    def test_health_check(self):
        """Test endpoint de health check"""
        # Act
        response = self.client.get('/health')
        
        # Assert
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'up'
        assert 'endpoints' in data
