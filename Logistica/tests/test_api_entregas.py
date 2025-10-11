import pytest
import sys
import os
import json
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from aplicacion.dto import EntregaDTO

class TestAPIEntregas:
    def setup_method(self):
        # Mock de la base de datos para evitar conexión a PostgreSQL
        with patch('config.db.init_db') as mock_init_db, \
             patch('api.entregas.ejecutar_consulta') as mock_ejecutar_consulta:
            
            from flask import Flask
            from api.entregas import bp
            
            self.app = Flask(__name__)
            self.app.register_blueprint(bp)
            self.app.config['TESTING'] = True
            self.client = self.app.test_client()
            
            # Mock de la función de consulta
            self.mock_ejecutar_consulta = mock_ejecutar_consulta

    @patch('api.entregas.ejecutar_consulta')
    def test_obtener_entregas_exitoso(self, mock_ejecutar_consulta):
        entrega_dto = EntregaDTO(
            direccion="Calle 123 #45-67",
            fecha_entrega=datetime.now() + timedelta(days=1),
            producto_id="producto-123",
            cliente_id="cliente-456"
        )
        
        mock_ejecutar_consulta.return_value = [entrega_dto]
        
        response = self.client.get('/api/logistica/entregas/')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list)

    @patch('api.entregas.ejecutar_consulta')
    def test_obtener_entregas_vacio(self, mock_ejecutar_consulta):
        mock_ejecutar_consulta.return_value = []
        
        response = self.client.get('/api/logistica/entregas/')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data == []

    @patch('api.entregas.ejecutar_consulta')
    def test_obtener_entregas_error(self, mock_ejecutar_consulta):
        mock_ejecutar_consulta.side_effect = Exception("Error de base de datos")
        
        response = self.client.get('/api/logistica/entregas/')
        
        assert response.status_code == 500
        data = json.loads(response.data)
        assert 'error' in data

    @patch('api.entregas.RepositorioEntregaSQLite')
    def test_crear_entregas_temp_exitoso(self, mock_repo_class):
        mock_repo = Mock()
        mock_repo_class.return_value = mock_repo
        
        response = self.client.post('/api/logistica/entregas/creartemp')
        
        assert response.status_code == 201
        data = json.loads(response.data)
        assert 'message' in data
        assert '20 entregas generadas' in data['message']

    @patch('api.entregas.RepositorioEntregaSQLite')
    def test_crear_entregas_temp_error(self, mock_repo_class):
        mock_repo = Mock()
        mock_repo.crear.side_effect = Exception("Error de base de datos")
        mock_repo_class.return_value = mock_repo
        
        response = self.client.post('/api/logistica/entregas/creartemp')
        
        assert response.status_code == 500
        data = json.loads(response.data)
        assert 'error' in data
