import pytest
import sys
import os
import json

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from api import create_app


class TestAPIHealth:
    
    def setup_method(self):
        """Setup para cada test"""
        # Configurar SQLite para pruebas
        os.environ['DB_HOST'] = 'localhost'
        os.environ['DB_PORT'] = '5432'
        os.environ['DB_NAME'] = 'test_usuarios_db'
        os.environ['DB_USER'] = 'test_user'
        os.environ['DB_PASSWORD'] = 'test_pass'
        
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
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
        assert 'POST /api/proveedores/' in data['endpoints']
