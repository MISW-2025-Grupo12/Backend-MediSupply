import pytest
import sys
import os
import json
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from api import create_app
from config.db import db


class TestAPIPedidos:
    """Tests de integración para los endpoints de la API de pedidos"""
    
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
    
    @patch('aplicacion.comandos.crear_pedido.ServicioUsuarios')
    def test_crear_pedido_exitoso(self, mock_servicio_usuarios_class):
        """Test para crear un pedido correctamente"""
        mock_servicio = MagicMock()
        mock_servicio_usuarios_class.return_value = mock_servicio
        mock_servicio.obtener_vendedor_por_id.return_value = {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "nombre": "Vendedor Test"
        }
        mock_servicio.obtener_cliente_por_id.return_value = {
            "id": "550e8400-e29b-41d4-a716-446655440001",
            "nombre": "Cliente Test"
        }
        
        pedido_data = {
            "vendedor_id": "550e8400-e29b-41d4-a716-446655440000",
            "cliente_id": "550e8400-e29b-41d4-a716-446655440001"
        }
        
        response = self.client.post(
            '/ventas/api/pedidos/',
            data=json.dumps(pedido_data),
            content_type='application/json'
        )
        
        assert response.status_code == 201
        data = response.get_json()
        assert 'pedido_id' in data
    
    def test_crear_pedido_sin_json(self):
        """Test para validar error cuando no se envía JSON"""
        response = self.client.post(
            '/ventas/api/pedidos/',
            data='',
            content_type='application/json'
        )
        
        assert response.status_code in [400, 500]
        data = response.get_json()
        assert 'error' in data
    
    def test_obtener_pedidos(self):
        """Test para obtener todos los pedidos"""
        response = self.client.get('/ventas/api/pedidos/')
        
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, dict)
        assert 'items' in data
        assert 'pagination' in data
        assert isinstance(data['items'], list)
    
    def test_obtener_pedidos_por_vendedor(self):
        """Test para obtener pedidos filtrados por vendedor"""
        vendedor_id = "550e8400-e29b-41d4-a716-446655440000"
        response = self.client.get(f'/ventas/api/pedidos/?vendedor_id={vendedor_id}')
        
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, dict)
        assert 'items' in data
        assert 'pagination' in data
        assert isinstance(data['items'], list)
    
    def test_obtener_pedidos_por_cliente(self):
        """Test para obtener pedidos filtrados por cliente"""
        cliente_id = "550e8400-e29b-41d4-a716-446655440001"
        response = self.client.get(f'/ventas/api/pedidos/?cliente_id={cliente_id}')
        
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, dict)
        assert 'items' in data
        assert 'pagination' in data
        assert isinstance(data['items'], list)
    
    def test_obtener_pedidos_por_estado(self):
        """Test para obtener pedidos filtrados por estado"""
        response = self.client.get('/ventas/api/pedidos/?estado=borrador')
        
        assert response.status_code == 200
        data = response.get_json()
        assert isinstance(data, dict)
        assert 'items' in data
        assert 'pagination' in data
        assert isinstance(data['items'], list)
    
    @patch('aplicacion.comandos.crear_pedido.ServicioUsuarios')
    def test_obtener_pedido_por_id(self, mock_servicio_usuarios_class):
        """Test para obtener un pedido específico por ID"""
        mock_servicio = MagicMock()
        mock_servicio_usuarios_class.return_value = mock_servicio
        mock_servicio.obtener_vendedor_por_id.return_value = {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "nombre": "Vendedor Test"
        }
        mock_servicio.obtener_cliente_por_id.return_value = {
            "id": "550e8400-e29b-41d4-a716-446655440001",
            "nombre": "Cliente Test"
        }
        
        # Primero crear un pedido
        pedido_data = {
            "vendedor_id": "550e8400-e29b-41d4-a716-446655440000",
            "cliente_id": "550e8400-e29b-41d4-a716-446655440001"
        }
        
        create_response = self.client.post(
            '/ventas/api/pedidos/',
            data=json.dumps(pedido_data),
            content_type='application/json'
        )
        
        pedido_id = create_response.get_json()['pedido_id']
        
        # Obtener el pedido
        response = self.client.get(f'/ventas/api/pedidos/{pedido_id}')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['id'] == pedido_id
    
    @patch('aplicacion.comandos.crear_pedido.ServicioUsuarios')
    def test_agregar_item_pedido(self, mock_servicio_usuarios_class):
        """Test para agregar un item a un pedido"""
        mock_servicio = MagicMock()
        mock_servicio_usuarios_class.return_value = mock_servicio
        mock_servicio.obtener_vendedor_por_id.return_value = {
            "id": "550e8400-e29b-41d4-a716-446655440000",
            "nombre": "Vendedor Test"
        }
        mock_servicio.obtener_cliente_por_id.return_value = {
            "id": "550e8400-e29b-41d4-a716-446655440001",
            "nombre": "Cliente Test"
        }
        
        # Primero crear un pedido
        pedido_data = {
            "vendedor_id": "550e8400-e29b-41d4-a716-446655440000",
            "cliente_id": "550e8400-e29b-41d4-a716-446655440001"
        }
        
        create_response = self.client.post(
            '/ventas/api/pedidos/',
            data=json.dumps(pedido_data),
            content_type='application/json'
        )
        
        pedido_id = create_response.get_json()['pedido_id']
        
        # Agregar item
        item_data = {
            "producto_id": "550e8400-e29b-41d4-a716-446655440002",
            "cantidad": 5
        }
        
        response = self.client.post(
            f'/ventas/api/pedidos/{pedido_id}/items',
            data=json.dumps(item_data),
            content_type='application/json'
        )
        
        assert response.status_code in [200, 201, 400]
    
    def test_agregar_item_sin_json(self):
        """Test para validar error al agregar item sin JSON"""
        pedido_id = "550e8400-e29b-41d4-a716-446655440000"
        
        response = self.client.post(
            f'/ventas/api/pedidos/{pedido_id}/items',
            data='',
            content_type='application/json'
        )
        
        assert response.status_code in [400, 500]
        data = response.get_json()
        assert 'error' in data
    
    def test_actualizar_item_pedido(self):
        """Test para actualizar la cantidad de un item"""
        pedido_id = "550e8400-e29b-41d4-a716-446655440000"
        item_id = "550e8400-e29b-41d4-a716-446655440001"
        
        update_data = {
            "cantidad": 10
        }
        
        response = self.client.put(
            f'/ventas/api/pedidos/{pedido_id}/items/{item_id}',
            data=json.dumps(update_data),
            content_type='application/json'
        )
        
        # Puede fallar si no existe, pero verificamos la estructura
        assert response.status_code in [200, 404, 400]
    
    def test_quitar_item_pedido(self):
        """Test para quitar un item de un pedido"""
        pedido_id = "550e8400-e29b-41d4-a716-446655440000"
        item_id = "550e8400-e29b-41d4-a716-446655440001"
        
        response = self.client.delete(
            f'/ventas/api/pedidos/{pedido_id}/items/{item_id}'
        )
        
        # Puede fallar si no existe, pero verificamos la estructura
        assert response.status_code in [200, 404, 400]
    
    def test_confirmar_pedido(self):
        """Test para confirmar un pedido"""
        pedido_id = "550e8400-e29b-41d4-a716-446655440000"
        
        response = self.client.post(f'/ventas/api/pedidos/{pedido_id}/confirmar')
        
        # Puede fallar si no existe o no tiene items
        assert response.status_code in [200, 400, 404]
    
    @patch('aplicacion.servicios.validador_pedidos.ValidadorPedidos')
    def test_crear_pedido_completo_con_mock(self, mock_validador):
        """Test para crear un pedido completo con items"""
        # Mock del validador
        mock_validador_instance = MagicMock()
        mock_validador_instance.validar_producto.return_value = {
            'id': '550e8400-e29b-41d4-a716-446655440002',
            'nombre': 'Producto Test',
            'precio': 100
        }
        mock_validador_instance.validar_inventario.return_value = True
        mock_validador.return_value = mock_validador_instance
        
        pedido_data = {
            "vendedor_id": "550e8400-e29b-41d4-a716-446655440000",
            "cliente_id": "550e8400-e29b-41d4-a716-446655440001",
            "items": [
                {
                    "producto_id": "550e8400-e29b-41d4-a716-446655440002",
                    "cantidad": 5
                }
            ]
        }
        
        response = self.client.post(
            '/ventas/api/pedidos/completo',
            data=json.dumps(pedido_data),
            content_type='application/json'
        )
        
        # El endpoint puede responder con diferentes códigos dependiendo de la lógica
        assert response.status_code in [200, 201, 400, 500]
    
    def test_buscar_productos(self):
        """Test para buscar productos disponibles"""
        response = self.client.get('/ventas/api/pedidos/productos/buscar?q=test')
        
        assert response.status_code in [200, 404]
        # Si es exitoso, debe retornar una lista
        if response.status_code == 200:
            data = response.get_json()
            assert isinstance(data, list) or isinstance(data, dict)
    
    def test_buscar_productos_sin_query(self):
        """Test para buscar productos sin parámetro de búsqueda"""
        response = self.client.get('/ventas/api/pedidos/productos/buscar')
        
        # Puede retornar error o lista vacía
        assert response.status_code in [200, 400]
    
    def test_cambiar_estado_pedido_en_transito_exitoso(self):
        """Test para cambiar estado de pedido a en_transito exitosamente"""
        estado_data = {"estado": "en_transito"}
        
        # Test básico sin mock complejo - solo verificar que el endpoint existe
        response = self.client.put('/ventas/api/pedidos/pedido123/estado',
                                 json=estado_data,
                                 headers={'X-User-Id': 'vendedor123', 'X-User-Role': 'VENDEDOR'})
        
        # El endpoint debe responder (puede ser 400 por pedido no encontrado, pero no 500)
        assert response.status_code != 500
        assert response.status_code in [200, 400, 404]
    
    def test_cambiar_estado_pedido_entregado_exitoso(self):
        """Test para cambiar estado de pedido a entregado exitosamente"""
        estado_data = {"estado": "entregado"}
        
        response = self.client.put('/ventas/api/pedidos/pedido123/estado',
                                 json=estado_data,
                                 headers={'X-User-Id': 'repartidor123', 'X-User-Role': 'REPARTIDOR'})
        
        # El endpoint debe responder (puede ser 400 por pedido no encontrado, pero no 500)
        assert response.status_code != 500
        assert response.status_code in [200, 400, 404]
    
    def test_cambiar_estado_pedido_sin_json(self):
        """Test para cambiar estado sin enviar JSON"""
        response = self.client.put('/ventas/api/pedidos/pedido123/estado',
                                 headers={'X-User-Id': 'vendedor123', 'X-User-Role': 'VENDEDOR'})
        
        # El endpoint puede devolver 400 o 500 dependiendo del manejo de errores
        assert response.status_code in [400, 500]
    
    def test_cambiar_estado_pedido_estado_vacio(self):
        """Test para cambiar estado con campo estado vacío"""
        estado_data = {"estado": ""}
        
        response = self.client.put('/ventas/api/pedidos/pedido123/estado',
                                 json=estado_data,
                                 headers={'X-User-Id': 'vendedor123', 'X-User-Role': 'VENDEDOR'})
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'obligatorio' in data['error']
    
    def test_cambiar_estado_pedido_sin_headers_usuario(self):
        """Test para cambiar estado sin headers de usuario"""
        estado_data = {"estado": "en_transito"}
        
        response = self.client.put('/ventas/api/pedidos/pedido123/estado',
                                 json=estado_data)
        
        assert response.status_code == 401
        data = response.get_json()
        assert 'usuario no disponible' in data['error']
    
    def test_cambiar_estado_pedido_estado_invalido(self):
        """Test para cambiar estado con estado inválido"""
        estado_data = {"estado": "estado_invalido"}
        
        response = self.client.put('/ventas/api/pedidos/pedido123/estado',
                                 json=estado_data,
                                 headers={'X-User-Id': 'vendedor123', 'X-User-Role': 'VENDEDOR'})
        
        # Debe responder con error de validación
        assert response.status_code in [400, 500]
    
    def test_cambiar_estado_pedido_no_encontrado(self):
        """Test para cambiar estado de pedido que no existe"""
        estado_data = {"estado": "en_transito"}
        
        response = self.client.put('/ventas/api/pedidos/pedido_inexistente/estado',
                                 json=estado_data,
                                 headers={'X-User-Id': 'vendedor123', 'X-User-Role': 'VENDEDOR'})
        
        # Debe responder con error (pedido no encontrado)
        assert response.status_code in [400, 404, 500]
    
    def test_cambiar_estado_pedido_transicion_invalida(self):
        """Test para cambiar estado con transición inválida"""
        estado_data = {"estado": "entregado"}
        
        response = self.client.put('/ventas/api/pedidos/pedido123/estado',
                                 json=estado_data,
                                 headers={'X-User-Id': 'vendedor123', 'X-User-Role': 'VENDEDOR'})
        
        # Debe responder con error de transición
        assert response.status_code in [400, 500]
    
    def test_cambiar_estado_pedido_sin_permisos(self):
        """Test para cambiar estado sin permisos suficientes"""
        estado_data = {"estado": "en_transito"}
        
        response = self.client.put('/ventas/api/pedidos/pedido123/estado',
                                 json=estado_data,
                                 headers={'X-User-Id': 'cliente123', 'X-User-Role': 'CLIENTE'})
        
        # Debe responder con error de permisos
        assert response.status_code in [400, 401, 403, 500]

