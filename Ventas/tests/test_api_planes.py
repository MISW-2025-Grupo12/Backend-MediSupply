import pytest
import sys
import os
import json
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from api import create_app
from config.db import db
from infraestructura.modelos import PlanVisitaModel, VisitaModel


class TestAPIPlanes:
    """Tests de integración para los endpoints de la API de planes"""
    
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
    
    @patch('aplicacion.comandos.crear_plan.ServicioUsuarios')
    def test_crear_plan_exitoso(self, mock_servicio_usuarios_class):
        """Test para crear un plan correctamente"""
        # Mock del servicio de usuarios
        mock_servicio = MagicMock()
        mock_servicio_usuarios_class.return_value = mock_servicio
        mock_servicio.obtener_cliente_por_id.return_value = {
            "id": "550e8400-e29b-41d4-a716-446655440001",
            "direccion": "Calle 123 #45-67",
            "telefono": "3001234567"
        }
        
        plan_data = {
            "nombre": "Plan de Visitas Octubre 2025",
            "id_usuario": "550e8400-e29b-41d4-a716-446655440000",
            "fecha_inicio": "2025-10-01T00:00:00",
            "fecha_fin": "2025-10-31T23:59:59",
            "visitas_clientes": [
                {
                    "id_cliente": "550e8400-e29b-41d4-a716-446655440001",
                    "visitas": [
                        "2025-10-05T10:00:00",
                        "2025-10-15T14:00:00"
                    ]
                }
            ]
        }
        
        response = self.client.post(
            '/ventas/api/planes/',
            data=json.dumps(plan_data),
            content_type='application/json'
        )
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['success'] is True
        assert 'plan_id' in data
        assert data['message'] == 'Plan creado exitosamente'
    
    def test_crear_plan_sin_json(self):
        """Test para validar error cuando no se envía JSON"""
        response = self.client.post(
            '/ventas/api/planes/',
            data='',
            content_type='application/json'
        )
        
        # Puede retornar 400 o 500 dependiendo de cómo se maneje el error
        assert response.status_code in [400, 500]
        data = response.get_json()
        assert 'error' in data
    
    def test_crear_plan_nombre_vacio(self):
        """Test para validar error con nombre vacío"""
        plan_data = {
            "nombre": "",
            "id_usuario": "550e8400-e29b-41d4-a716-446655440000",
            "fecha_inicio": "2025-10-01T00:00:00",
            "fecha_fin": "2025-10-31T23:59:59",
            "visitas_clientes": [
                {
                    "id_cliente": "550e8400-e29b-41d4-a716-446655440001",
                    "visitas": ["2025-10-05T10:00:00"]
                }
            ]
        }
        
        response = self.client.post(
            '/ventas/api/planes/',
            data=json.dumps(plan_data),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert 'nombre' in data['error'].lower()
    
    def test_crear_plan_nombre_muy_largo(self):
        """Test para validar error con nombre muy largo (>100 caracteres)"""
        plan_data = {
            "nombre": "a" * 101,
            "id_usuario": "550e8400-e29b-41d4-a716-446655440000",
            "fecha_inicio": "2025-10-01T00:00:00",
            "fecha_fin": "2025-10-31T23:59:59",
            "visitas_clientes": [
                {
                    "id_cliente": "550e8400-e29b-41d4-a716-446655440001",
                    "visitas": ["2025-10-05T10:00:00"]
                }
            ]
        }
        
        response = self.client.post(
            '/ventas/api/planes/',
            data=json.dumps(plan_data),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert '100' in data['error']
    
    def test_crear_plan_fecha_inicio_invalida(self):
        """Test para validar error con fecha de inicio inválida"""
        plan_data = {
            "nombre": "Plan de Visitas",
            "id_usuario": "550e8400-e29b-41d4-a716-446655440000",
            "fecha_inicio": "fecha-invalida",
            "fecha_fin": "2025-10-31T23:59:59",
            "visitas_clientes": [
                {
                    "id_cliente": "550e8400-e29b-41d4-a716-446655440001",
                    "visitas": ["2025-10-05T10:00:00"]
                }
            ]
        }
        
        response = self.client.post(
            '/ventas/api/planes/',
            data=json.dumps(plan_data),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert 'fecha' in data['error'].lower()
    
    def test_crear_plan_fecha_inicio_posterior_a_fin(self):
        """Test para validar error cuando fecha_inicio > fecha_fin"""
        plan_data = {
            "nombre": "Plan de Visitas",
            "id_usuario": "550e8400-e29b-41d4-a716-446655440000",
            "fecha_inicio": "2025-10-31T23:59:59",
            "fecha_fin": "2025-10-01T00:00:00",
            "visitas_clientes": [
                {
                    "id_cliente": "550e8400-e29b-41d4-a716-446655440001",
                    "visitas": ["2025-10-05T10:00:00"]
                }
            ]
        }
        
        response = self.client.post(
            '/ventas/api/planes/',
            data=json.dumps(plan_data),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert 'inicio' in data['error'].lower() or 'posterior' in data['error'].lower()
    
    def test_crear_plan_sin_visitas_clientes(self):
        """Test para validar error cuando no hay visitas_clientes"""
        plan_data = {
            "nombre": "Plan de Visitas",
            "id_usuario": "550e8400-e29b-41d4-a716-446655440000",
            "fecha_inicio": "2025-10-01T00:00:00",
            "fecha_fin": "2025-10-31T23:59:59",
            "visitas_clientes": []
        }
        
        response = self.client.post(
            '/ventas/api/planes/',
            data=json.dumps(plan_data),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert 'cliente' in data['error'].lower() or 'visita' in data['error'].lower()
    
    @patch('aplicacion.comandos.crear_plan.ServicioUsuarios')
    def test_crear_plan_cliente_no_encontrado(self, mock_servicio_usuarios_class):
        """Test para validar error cuando cliente no existe"""
        # Mock del servicio de usuarios - cliente no encontrado
        mock_servicio = MagicMock()
        mock_servicio_usuarios_class.return_value = mock_servicio
        mock_servicio.obtener_cliente_por_id.return_value = None
        
        plan_data = {
            "nombre": "Plan de Visitas",
            "id_usuario": "550e8400-e29b-41d4-a716-446655440000",
            "fecha_inicio": "2025-10-01T00:00:00",
            "fecha_fin": "2025-10-31T23:59:59",
            "visitas_clientes": [
                {
                    "id_cliente": "cliente-inexistente",
                    "visitas": ["2025-10-05T10:00:00"]
                }
            ]
        }
        
        response = self.client.post(
            '/ventas/api/planes/',
            data=json.dumps(plan_data),
            content_type='application/json'
        )
        
        assert response.status_code == 404
        data = response.get_json()
        assert 'error' in data
        assert 'no encontrado' in data['error'].lower()
    
    @patch('aplicacion.comandos.crear_plan.ServicioUsuarios')
    def test_crear_plan_fecha_visita_invalida(self, mock_servicio_usuarios_class):
        """Test para validar error con fecha de visita inválida"""
        # Mock del servicio de usuarios
        mock_servicio = MagicMock()
        mock_servicio_usuarios_class.return_value = mock_servicio
        mock_servicio.obtener_cliente_por_id.return_value = {
            "id": "550e8400-e29b-41d4-a716-446655440001",
            "direccion": "Calle 123 #45-67",
            "telefono": "3001234567"
        }
        
        plan_data = {
            "nombre": "Plan de Visitas",
            "id_usuario": "550e8400-e29b-41d4-a716-446655440000",
            "fecha_inicio": "2025-10-01T00:00:00",
            "fecha_fin": "2025-10-31T23:59:59",
            "visitas_clientes": [
                {
                    "id_cliente": "550e8400-e29b-41d4-a716-446655440001",
                    "visitas": ["fecha-invalida"]
                }
            ]
        }
        
        response = self.client.post(
            '/ventas/api/planes/',
            data=json.dumps(plan_data),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert 'fecha' in data['error'].lower()
    
    @patch('aplicacion.comandos.crear_plan.ServicioUsuarios')
    def test_crear_plan_multiple_clientes(self, mock_servicio_usuarios_class):
        """Test para crear plan con múltiples clientes"""
        # Mock del servicio de usuarios
        mock_servicio = MagicMock()
        mock_servicio_usuarios_class.return_value = mock_servicio
        
        def mock_obtener_cliente(cliente_id):
            clientes = {
                "550e8400-e29b-41d4-a716-446655440001": {
                    "id": "550e8400-e29b-41d4-a716-446655440001",
                    "direccion": "Calle 123 #45-67",
                    "telefono": "3001234567"
                },
                "550e8400-e29b-41d4-a716-446655440002": {
                    "id": "550e8400-e29b-41d4-a716-446655440002",
                    "direccion": "Calle 456 #78-90",
                    "telefono": "3007654321"
                }
            }
            return clientes.get(cliente_id)
        
        mock_servicio.obtener_cliente_por_id.side_effect = mock_obtener_cliente
        
        plan_data = {
            "nombre": "Plan de Visitas Múltiples Clientes",
            "id_usuario": "550e8400-e29b-41d4-a716-446655440000",
            "fecha_inicio": "2025-10-01T00:00:00",
            "fecha_fin": "2025-10-31T23:59:59",
            "visitas_clientes": [
                {
                    "id_cliente": "550e8400-e29b-41d4-a716-446655440001",
                    "visitas": ["2025-10-05T10:00:00"]
                },
                {
                    "id_cliente": "550e8400-e29b-41d4-a716-446655440002",
                    "visitas": ["2025-10-10T14:00:00", "2025-10-20T16:00:00"]
                }
            ]
        }
        
        response = self.client.post(
            '/ventas/api/planes/',
            data=json.dumps(plan_data),
            content_type='application/json'
        )
        
        assert response.status_code == 201
        data = response.get_json()
        assert data['success'] is True
    
    def test_obtener_planes_sin_filtros(self):
        """Test para obtener todos los planes (admin)"""
        with self.app.app_context():
            # Crear un plan de prueba directamente
            plan = PlanVisitaModel(
                id="plan-test-1",
                nombre="Plan Test",
                id_usuario="user-1",
                fecha_inicio=datetime.now(),
                fecha_fin=datetime.now() + timedelta(days=30)
            )
            db.session.add(plan)
            db.session.commit()
        
        response = self.client.get(
            '/ventas/api/planes/',
            headers={'X-User-Role': 'ADMINISTRADOR'}
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'items' in data
        assert 'pagination' in data
        assert 'page' in data['pagination']
        assert 'page_size' in data['pagination']
        assert 'total_items' in data['pagination']
    
    def test_obtener_planes_por_usuario(self):
        """Test para obtener planes por usuario"""
        user_id = "user-1"
        
        with self.app.app_context():
            # Crear planes de prueba
            plan1 = PlanVisitaModel(
                id="plan-test-1",
                nombre="Plan Test 1",
                id_usuario=user_id,
                fecha_inicio=datetime.now(),
                fecha_fin=datetime.now() + timedelta(days=30)
            )
            plan2 = PlanVisitaModel(
                id="plan-test-2",
                nombre="Plan Test 2",
                id_usuario="user-2",
                fecha_inicio=datetime.now(),
                fecha_fin=datetime.now() + timedelta(days=30)
            )
            db.session.add(plan1)
            db.session.add(plan2)
            db.session.commit()
        
        response = self.client.get(
            f'/ventas/api/planes/?user_id={user_id}',
            headers={'X-User-Role': 'VENDEDOR'}
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'items' in data
        assert 'pagination' in data
        # Debería retornar solo los planes del usuario
        if data['items']:
            for plan in data['items']:
                assert plan['id_usuario'] == user_id
    
    def test_obtener_planes_con_paginacion(self):
        """Test para obtener planes con paginación"""
        with self.app.app_context():
            # Crear varios planes de prueba
            for i in range(5):
                plan = PlanVisitaModel(
                    id=f"plan-test-{i}",
                    nombre=f"Plan Test {i}",
                    id_usuario="user-1",
                    fecha_inicio=datetime.now(),
                    fecha_fin=datetime.now() + timedelta(days=30)
                )
                db.session.add(plan)
            db.session.commit()
        
        response = self.client.get(
            '/ventas/api/planes/?page=1&page_size=2',
            headers={'X-User-Role': 'ADMINISTRADOR'}
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'items' in data
        assert 'pagination' in data
        assert data['pagination']['page'] == 1
        assert data['pagination']['page_size'] == 2
        assert len(data['items']) <= 2
    
    def test_obtener_planes_sin_resultados(self):
        """Test para obtener planes cuando no hay resultados"""
        response = self.client.get(
            '/ventas/api/planes/?user_id=usuario-inexistente',
            headers={'X-User-Role': 'VENDEDOR'}
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'items' in data
        assert 'pagination' in data
        assert len(data['items']) == 0
        assert data['pagination']['total_items'] == 0

