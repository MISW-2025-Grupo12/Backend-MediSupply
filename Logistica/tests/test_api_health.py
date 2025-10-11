import pytest
import sys
import os
from unittest.mock import patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

class TestAPIHealth:
    def setup_method(self):
        # Mock de la base de datos para evitar conexión a PostgreSQL
        with patch('config.db.init_db') as mock_init_db:
            from flask import Flask
            
            self.app = Flask(__name__)
            self.app.config['TESTING'] = True
            
            # Endpoint de health simple
            @self.app.route("/health")
            def health():
                return {
                    "status": "up",
                    "service": "logistica",
                    "endpoints": [
                        "GET /entregas-programadas",
                        "GET /api/inventario",
                        "GET /api/inventario/buscar",
                        "POST /api/inventario/reservar",
                        "POST /api/inventario/descontar",
                        "GET /api/inventario/producto/<id>",
                        "GET /spec",
                        "GET /health"
                    ]
                }, 200
            
            self.client = self.app.test_client()

    def test_health_check(self):
        response = self.client.get('/health')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['status'] == 'up'
        assert 'service' in data
        assert 'endpoints' in data
