import pytest
import sys
import os
from unittest.mock import patch, Mock
from datetime import datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

class TestAPIInventario:
    def setup_method(self):
        # Mock de la base de datos para evitar conexión a PostgreSQL
        with patch('config.db.init_db') as mock_init_db, \
             patch('api.inventario.ejecutar_consulta') as mock_ejecutar_consulta, \
             patch('api.inventario.ejecutar_comando') as mock_ejecutar_comando:
            
            from flask import Flask
            from api.inventario import bp
            
            self.app = Flask(__name__)
            self.app.register_blueprint(bp)
            self.app.config['TESTING'] = True
            self.client = self.app.test_client()
            
            # Mocks
            self.mock_ejecutar_consulta = mock_ejecutar_consulta
            self.mock_ejecutar_comando = mock_ejecutar_comando

    def test_obtener_inventario_exitoso(self):
        mock_inventario = [
            {
                'producto_id': 'prod-123',
                'cantidad_disponible': 100,
                'cantidad_reservada': 10,
                'fecha_vencimiento': (datetime.now() + timedelta(days=30)).isoformat()
            }
        ]
        self.mock_ejecutar_consulta.return_value = mock_inventario
        
        response = self.client.get('/api/inventario')
        
        assert response.status_code == 200
        data = response.get_json()
        assert len(data) == 1
        assert data[0]['producto_id'] == 'prod-123'

    def test_obtener_inventario_vacio(self):
        self.mock_ejecutar_consulta.return_value = []
        
        response = self.client.get('/api/inventario')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data == []

    def test_obtener_inventario_error(self):
        self.mock_ejecutar_consulta.side_effect = Exception("Error de DB")
        
        response = self.client.get('/api/inventario')
        
        assert response.status_code == 500

    def test_buscar_productos_exitoso(self):
        mock_productos = [
            {
                'id': 'prod-123',
                'nombre': 'Paracetamol',
                'cantidad_disponible': 100,
                'cantidad_reservada': 10,
                'lotes': []
            }
        ]
        self.mock_ejecutar_consulta.return_value = mock_productos
        
        response = self.client.get('/api/inventario/buscar?q=paracetamol')
        
        assert response.status_code == 200
        data = response.get_json()
        assert len(data) == 1
        assert data[0]['id'] == 'prod-123'

    def test_buscar_productos_sin_termino(self):
        response = self.client.get('/api/inventario/buscar')
        
        assert response.status_code == 400

    def test_buscar_productos_error(self):
        self.mock_ejecutar_consulta.side_effect = Exception("Error de DB")
        
        response = self.client.get('/api/inventario/buscar?q=test')
        
        assert response.status_code == 500

    def test_reservar_inventario_exitoso(self):
        mock_resultado = {
            'success': True,
            'message': 'Inventario reservado exitosamente'
        }
        self.mock_ejecutar_comando.return_value = mock_resultado
        
        data = {
            'items': [
                {'producto_id': 'prod-123', 'cantidad': 5}
            ]
        }
        
        response = self.client.post('/api/inventario/reservar', json=data)
        
        assert response.status_code == 200
        result = response.get_json()
        assert result['success'] == True

    def test_reservar_inventario_datos_invalidos(self):
        data = {
            'items': [
                {'producto_id': 'prod-123', 'cantidad': 0}
            ]
        }
        
        response = self.client.post('/api/inventario/reservar', json=data)
        
        assert response.status_code == 400

    def test_reservar_inventario_error(self):
        self.mock_ejecutar_comando.side_effect = Exception("Error de DB")
        
        data = {
            'items': [
                {'producto_id': 'prod-123', 'cantidad': 5}
            ]
        }
        
        response = self.client.post('/api/inventario/reservar', json=data)
        
        assert response.status_code == 500

    def test_descontar_inventario_exitoso(self):
        mock_resultado = {
            'success': True,
            'message': 'Inventario descontado exitosamente'
        }
        self.mock_ejecutar_comando.return_value = mock_resultado
        
        data = {
            'items': [
                {'producto_id': 'prod-123', 'cantidad': 5}
            ]
        }
        
        response = self.client.post('/api/inventario/descontar', json=data)
        
        assert response.status_code == 200
        result = response.get_json()
        assert result['success'] == True

    def test_descontar_inventario_datos_invalidos(self):
        data = {
            'items': [
                {'producto_id': 'prod-123', 'cantidad': 0}
            ]
        }
        
        response = self.client.post('/api/inventario/descontar', json=data)
        
        assert response.status_code == 400

    def test_descontar_inventario_error(self):
        self.mock_ejecutar_comando.side_effect = Exception("Error de DB")
        
        data = {
            'items': [
                {'producto_id': 'prod-123', 'cantidad': 5}
            ]
        }
        
        response = self.client.post('/api/inventario/descontar', json=data)
        
        assert response.status_code == 500

    def test_obtener_producto_por_id_exitoso(self):
        mock_inventario = [
            {
                'producto_id': 'prod-123',
                'cantidad_disponible': 100,
                'cantidad_reservada': 10,
                'fecha_vencimiento': (datetime.now() + timedelta(days=30)).isoformat()
            }
        ]
        self.mock_ejecutar_consulta.return_value = mock_inventario
        
        response = self.client.get('/api/inventario/producto/prod-123')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['producto_id'] == 'prod-123'

    def test_obtener_producto_por_id_no_encontrado(self):
        self.mock_ejecutar_consulta.return_value = []
        
        response = self.client.get('/api/inventario/producto/prod-999')
        
        assert response.status_code == 404

    def test_obtener_producto_por_id_error(self):
        self.mock_ejecutar_consulta.side_effect = Exception("Error de DB")
        
        response = self.client.get('/api/inventario/producto/prod-123')
        
        assert response.status_code == 500
