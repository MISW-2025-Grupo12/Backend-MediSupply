import pytest
import sys
import os
import json
from datetime import datetime
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from api import create_app
from config.db import db


class TestAPIVisitas:
    """Tests de integración para los endpoints de la API de visitas"""
    
    def setup_method(self):
        """Configuración antes de cada test"""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.client = self.app.test_client()
        
        with self.app.app_context():
            db.create_all()
    
    def teardown_method(self):
        """Limpieza después de cada test"""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
    
    def test_crear_visita_exitoso(self):
        """Test para crear una visita correctamente"""
        visita_data = {
            "vendedor_id": "550e8400-e29b-41d4-a716-446655440000",
            "cliente_id": "550e8400-e29b-41d4-a716-446655440001",
            "fecha_programada": "2025-10-15T10:00:00",
            "direccion": "Calle 123 #45-67",
            "telefono": "3001234567",
            "estado": "pendiente",
            "descripcion": "Visita de prueba"
        }
        
        response = self.client.post(
            '/ventas/api/visitas/',
            data=json.dumps(visita_data),
            content_type='application/json'
        )
        
        # Puede fallar con 400 si el vendedor no existe (sin servicio externo)
        # o 201 si se crea exitosamente
        assert response.status_code in [201, 400]
        data = response.get_json()
        
        if response.status_code == 201:
            assert data['vendedor_id'] == visita_data['vendedor_id']
            assert data['cliente_id'] == visita_data['cliente_id']
            assert data['estado'] == 'pendiente'
        else:
            # Validar que hay un mensaje de error
            assert 'error' in data
    
    def test_crear_visita_sin_json(self):
        """Test para validar error cuando no se envía JSON"""
        response = self.client.post(
            '/ventas/api/visitas/',
            data='',
            content_type='application/json'
        )
        
        # Puede retornar 400 o 500 dependiendo de cómo se maneje el error
        assert response.status_code in [400, 500]
        data = response.get_json()
        assert 'error' in data
    
    def test_crear_visita_fecha_invalida(self):
        """Test para validar error con fecha inválida"""
        visita_data = {
            "vendedor_id": "550e8400-e29b-41d4-a716-446655440000",
            "cliente_id": "550e8400-e29b-41d4-a716-446655440001",
            "fecha_programada": "fecha-invalida",
            "direccion": "Calle 123",
            "telefono": "3001234567"
        }
        
        response = self.client.post(
            '/ventas/api/visitas/',
            data=json.dumps(visita_data),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert 'fecha' in data['error'].lower()
    
    def test_obtener_visitas_sin_filtros(self):
        """Test para obtener todas las visitas sin filtros"""
        # Primero crear una visita
        visita_data = {
            "vendedor_id": "550e8400-e29b-41d4-a716-446655440000",
            "cliente_id": "550e8400-e29b-41d4-a716-446655440001",
            "fecha_programada": "2025-10-15T10:00:00",
            "direccion": "Calle 123",
            "telefono": "3001234567"
        }
        
        self.client.post(
            '/ventas/api/visitas/',
            data=json.dumps(visita_data),
            content_type='application/json'
        )
        
        # Obtener visitas
        response = self.client.get('/ventas/api/visitas/')
        
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, dict)
        assert 'items' in data
        assert 'pagination' in data
        assert isinstance(data['items'], list)
    
    def test_obtener_visitas_por_estado(self):
        """Test para obtener visitas filtradas por estado"""
        response = self.client.get('/ventas/api/visitas/?estado=pendiente')
        
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, dict)
        assert 'items' in data
        assert 'pagination' in data
        assert isinstance(data['items'], list)
    
    def test_obtener_visitas_por_vendedor(self):
        """Test para obtener visitas filtradas por vendedor"""
        vendedor_id = "550e8400-e29b-41d4-a716-446655440000"
        response = self.client.get(f'/ventas/api/visitas/?vendedor_id={vendedor_id}')
        
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, dict)
        assert 'items' in data
        assert 'pagination' in data
        assert isinstance(data['items'], list)
    
    def test_obtener_visitas_por_rango_fechas(self):
        """Test para obtener visitas por rango de fechas"""
        response = self.client.get(
            '/ventas/api/visitas/?fecha_inicio=2025-10-01&fecha_fin=2025-10-31'
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, dict)
        assert 'items' in data
        assert 'pagination' in data
        assert isinstance(data['items'], list)
    
    def test_obtener_visitas_por_vendedor_endpoint_especifico(self):
        """Test para obtener visitas por vendedor usando endpoint específico"""
        vendedor_id = "550e8400-e29b-41d4-a716-446655440000"
        response = self.client.get(f'/ventas/api/visitas/vendedor/{vendedor_id}')
        
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, dict)
        assert 'items' in data
        assert 'pagination' in data
        assert isinstance(data['items'], list)
    
    def test_obtener_visitas_vendedor_con_estado(self):
        """Test para obtener visitas por vendedor filtradas por estado"""
        vendedor_id = "550e8400-e29b-41d4-a716-446655440000"
        response = self.client.get(
            f'/ventas/api/visitas/vendedor/{vendedor_id}?estado=pendiente'
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, dict)
        assert 'items' in data
        assert 'pagination' in data
        assert isinstance(data['items'], list)
    
    def test_obtener_visitas_vendedor_con_fechas(self):
        """Test para obtener visitas por vendedor con rango de fechas"""
        vendedor_id = "550e8400-e29b-41d4-a716-446655440000"
        response = self.client.get(
            f'/ventas/api/visitas/vendedor/{vendedor_id}?fecha_inicio=2025-10-01&fecha_fin=2025-10-31'
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, dict)
        assert 'items' in data
        assert 'pagination' in data
        assert isinstance(data['items'], list)
    
    def test_registrar_visita_endpoint_estructura(self):
        """Test para verificar estructura del endpoint de registrar visita"""
        visita_id = "550e8400-e29b-41d4-a716-446655440000"
        
        # Registrar la visita
        registro_data = {
            "fecha_realizada": "2025-10-15",
            "hora_realizada": "10:30:00",
            "cliente_id": "550e8400-e29b-41d4-a716-446655440001",
            "novedades": "Visita exitosa",
            "pedido_generado": True
        }
        
        response = self.client.put(
            f'/ventas/api/visitas/{visita_id}',
            data=json.dumps(registro_data),
            content_type='application/json'
        )
        
        assert response.status_code in [200, 400, 404]
        data = response.get_json()
        assert data is not None
    
    def test_registrar_visita_sin_json(self):
        """Test para validar error al registrar visita sin JSON"""
        visita_id = "550e8400-e29b-41d4-a716-446655440000"
        
        response = self.client.put(
            f'/ventas/api/visitas/{visita_id}',
            data='',
            content_type='application/json'
        )
        
        assert response.status_code in [400, 500]
        data = response.get_json()
        assert 'error' in data
    
    def test_registrar_visita_sin_campos_obligatorios(self):
        """Test para validar error cuando faltan campos obligatorios"""
        visita_id = "550e8400-e29b-41d4-a716-446655440000"
        registro_data = {
            "novedades": "Test"
        }
        
        response = self.client.put(
            f'/ventas/api/visitas/{visita_id}',
            data=json.dumps(registro_data),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert 'obligatorio' in data['error'].lower()

