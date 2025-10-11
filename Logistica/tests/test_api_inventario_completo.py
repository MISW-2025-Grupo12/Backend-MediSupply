import pytest
import sys
import os
from unittest.mock import patch, Mock, MagicMock
from datetime import datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

class TestAPIInventarioCompleto:
    def setup_method(self):
        # Mock de la base de datos para evitar conexión a PostgreSQL
        with patch('config.db.init_db') as mock_init_db, \
             patch('seedwork.aplicacion.consultas.ejecutar_consulta') as mock_ejecutar_consulta, \
             patch('seedwork.aplicacion.comandos.ejecutar_comando') as mock_ejecutar_comando, \
             patch('api.inventario.RepositorioInventarioSQLite') as mock_repo_class:
            
            from flask import Flask
            from api.inventario import bp
            
            self.app = Flask(__name__)
            self.app.register_blueprint(bp)
            self.app.config['TESTING'] = True
            self.client = self.app.test_client()
            
            # Mocks
            self.mock_ejecutar_consulta = mock_ejecutar_consulta
            self.mock_ejecutar_comando = mock_ejecutar_comando
            self.mock_repo_class = mock_repo_class
            self.mock_repositorio = Mock()
            self.mock_repo_class.return_value = self.mock_repositorio

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
        
        response = self.client.get('/api/inventario/buscar?q=paracetamol&limite=10')
        
        assert response.status_code == 200
        data = response.get_json()
        assert len(data) == 1
        assert data[0]['id'] == 'prod-123'
        self.mock_ejecutar_consulta.assert_called_once()

    def test_buscar_productos_sin_termino(self):
        response = self.client.get('/api/inventario/buscar')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data == []
        self.mock_ejecutar_consulta.assert_not_called()

    def test_buscar_productos_termino_vacio(self):
        response = self.client.get('/api/inventario/buscar?q=   ')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data == []
        self.mock_ejecutar_consulta.assert_not_called()

    def test_buscar_productos_con_limite_default(self):
        self.mock_ejecutar_consulta.return_value = []
        
        response = self.client.get('/api/inventario/buscar?q=test')
        
        assert response.status_code == 200
        # Verificar que se llama con limite 50 (default)
        call_args = self.mock_ejecutar_consulta.call_args[0][0]
        assert call_args.limite == 50

    def test_buscar_productos_con_limite_personalizado(self):
        self.mock_ejecutar_consulta.return_value = []
        
        response = self.client.get('/api/inventario/buscar?q=test&limite=25')
        
        assert response.status_code == 200
        call_args = self.mock_ejecutar_consulta.call_args[0][0]
        assert call_args.limite == 25

    def test_buscar_productos_error(self):
        self.mock_ejecutar_consulta.side_effect = Exception("Error de DB")
        
        response = self.client.get('/api/inventario/buscar?q=test')
        
        assert response.status_code == 500
        data = response.get_json()
        assert 'error' in data

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
        self.mock_ejecutar_comando.assert_called_once()

    def test_reservar_inventario_sin_json(self):
        response = self.client.post('/api/inventario/reservar')
        
        assert response.status_code == 500  # Flask devuelve 500 para JSON malformado
        data = response.get_json()
        assert 'error' in data

    def test_reservar_inventario_json_vacio(self):
        response = self.client.post('/api/inventario/reservar', json={})
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert 'items' in data['error']

    def test_reservar_inventario_items_no_lista(self):
        data = {'items': 'no_es_lista'}
        
        response = self.client.post('/api/inventario/reservar', json=data)
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert 'lista' in data['error']

    def test_reservar_inventario_items_vacia(self):
        data = {'items': []}
        
        response = self.client.post('/api/inventario/reservar', json=data)
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert 'vacía' in data['error']

    def test_reservar_inventario_item_sin_producto_id(self):
        data = {
            'items': [
                {'cantidad': 5}  # Falta producto_id
            ]
        }
        
        response = self.client.post('/api/inventario/reservar', json=data)
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert 'producto_id' in data['error']

    def test_reservar_inventario_item_sin_cantidad(self):
        data = {
            'items': [
                {'producto_id': 'prod-123'}  # Falta cantidad
            ]
        }
        
        response = self.client.post('/api/inventario/reservar', json=data)
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert 'cantidad' in data['error']

    def test_reservar_inventario_item_no_dict(self):
        data = {
            'items': [
                'no_es_dict'  # No es diccionario
            ]
        }
        
        response = self.client.post('/api/inventario/reservar', json=data)
        
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data
        assert 'producto_id' in data['error']

    def test_reservar_inventario_fallo_comando(self):
        mock_resultado = {
            'success': False,
            'error': 'Stock insuficiente'
        }
        self.mock_ejecutar_comando.return_value = mock_resultado
        
        data = {
            'items': [
                {'producto_id': 'prod-123', 'cantidad': 5}
            ]
        }
        
        response = self.client.post('/api/inventario/reservar', json=data)
        
        assert response.status_code == 400
        result = response.get_json()
        assert result['success'] == False

    def test_reservar_inventario_error(self):
        self.mock_ejecutar_comando.side_effect = Exception("Error de DB")
        
        data = {
            'items': [
                {'producto_id': 'prod-123', 'cantidad': 5}
            ]
        }
        
        response = self.client.post('/api/inventario/reservar', json=data)
        
        assert response.status_code == 500
        data = response.get_json()
        assert 'error' in data

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
        self.mock_ejecutar_comando.assert_called_once()

    def test_descontar_inventario_sin_json(self):
        response = self.client.post('/api/inventario/descontar')
        
        assert response.status_code == 500  # Flask devuelve 500 para JSON malformado
        data = response.get_json()
        assert 'error' in data

    def test_descontar_inventario_fallo_comando(self):
        mock_resultado = {
            'success': False,
            'error': 'Cantidad reservada insuficiente'
        }
        self.mock_ejecutar_comando.return_value = mock_resultado
        
        data = {
            'items': [
                {'producto_id': 'prod-123', 'cantidad': 5}
            ]
        }
        
        response = self.client.post('/api/inventario/descontar', json=data)
        
        assert response.status_code == 400
        result = response.get_json()
        assert result['success'] == False

    def test_descontar_inventario_error(self):
        self.mock_ejecutar_comando.side_effect = Exception("Error de DB")
        
        data = {
            'items': [
                {'producto_id': 'prod-123', 'cantidad': 5}
            ]
        }
        
        response = self.client.post('/api/inventario/descontar', json=data)
        
        assert response.status_code == 500
        data = response.get_json()
        assert 'error' in data

    def test_obtener_inventario_producto_exitoso(self):
        # Mock de lotes de inventario
        mock_lote1 = Mock()
        mock_lote1.cantidad_disponible = 50
        mock_lote1.cantidad_reservada = 10
        mock_lote1.fecha_vencimiento = datetime.now() + timedelta(days=30)
        
        mock_lote2 = Mock()
        mock_lote2.cantidad_disponible = 30
        mock_lote2.cantidad_reservada = 5
        mock_lote2.fecha_vencimiento = datetime.now() + timedelta(days=60)
        
        self.mock_repositorio.obtener_por_producto_id.return_value = [mock_lote1, mock_lote2]
        
        response = self.client.get('/api/inventario/producto/prod-123')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['producto_id'] == 'prod-123'
        assert data['total_disponible'] == 80  # 50 + 30
        assert data['total_reservado'] == 15   # 10 + 5
        assert len(data['lotes']) == 2

    def test_obtener_inventario_producto_no_encontrado(self):
        self.mock_repositorio.obtener_por_producto_id.return_value = []
        
        response = self.client.get('/api/inventario/producto/prod-999')
        
        assert response.status_code == 404
        data = response.get_json()
        assert 'error' in data
        assert 'no encontrado' in data['error']

    def test_obtener_inventario_producto_error(self):
        self.mock_repositorio.obtener_por_producto_id.side_effect = Exception("Error de DB")
        
        response = self.client.get('/api/inventario/producto/prod-123')
        
        assert response.status_code == 500
        data = response.get_json()
        assert 'error' in data

    def test_obtener_todo_inventario_exitoso(self):
        # Mock de lotes de inventario
        mock_lote1 = Mock()
        mock_lote1.producto_id = 'prod-123'
        mock_lote1.cantidad_disponible = 50
        mock_lote1.cantidad_reservada = 10
        mock_lote1.fecha_vencimiento = datetime.now() + timedelta(days=30)
        
        mock_lote2 = Mock()
        mock_lote2.producto_id = 'prod-123'
        mock_lote2.cantidad_disponible = 30
        mock_lote2.cantidad_reservada = 5
        mock_lote2.fecha_vencimiento = datetime.now() + timedelta(days=60)
        
        mock_lote3 = Mock()
        mock_lote3.producto_id = 'prod-456'
        mock_lote3.cantidad_disponible = 100
        mock_lote3.cantidad_reservada = 20
        mock_lote3.fecha_vencimiento = datetime.now() + timedelta(days=90)
        
        self.mock_repositorio.obtener_todos.return_value = [mock_lote1, mock_lote2, mock_lote3]
        
        response = self.client.get('/api/inventario/')
        
        assert response.status_code == 200
        data = response.get_json()
        assert len(data) == 2  # 2 productos únicos
        
        # Verificar producto 1
        prod1 = next(p for p in data if p['producto_id'] == 'prod-123')
        assert prod1['total_disponible'] == 80  # 50 + 30
        assert prod1['total_reservado'] == 15   # 10 + 5
        assert len(prod1['lotes']) == 2
        
        # Verificar producto 2
        prod2 = next(p for p in data if p['producto_id'] == 'prod-456')
        assert prod2['total_disponible'] == 100
        assert prod2['total_reservado'] == 20
        assert len(prod2['lotes']) == 1

    def test_obtener_todo_inventario_vacio(self):
        self.mock_repositorio.obtener_todos.return_value = []
        
        response = self.client.get('/api/inventario/')
        
        assert response.status_code == 200
        data = response.get_json()
        assert data == []

    def test_obtener_todo_inventario_error(self):
        self.mock_repositorio.obtener_todos.side_effect = Exception("Error de DB")
        
        response = self.client.get('/api/inventario/')
        
        assert response.status_code == 500
        data = response.get_json()
        assert 'error' in data

    def test_reservar_inventario_multiple_items(self):
        mock_resultado = {
            'success': True,
            'message': 'Inventario reservado exitosamente'
        }
        self.mock_ejecutar_comando.return_value = mock_resultado
        
        data = {
            'items': [
                {'producto_id': 'prod-123', 'cantidad': 5},
                {'producto_id': 'prod-456', 'cantidad': 10}
            ]
        }
        
        response = self.client.post('/api/inventario/reservar', json=data)
        
        assert response.status_code == 200
        result = response.get_json()
        assert result['success'] == True

    def test_descontar_inventario_multiple_items(self):
        mock_resultado = {
            'success': True,
            'message': 'Inventario descontado exitosamente'
        }
        self.mock_ejecutar_comando.return_value = mock_resultado
        
        data = {
            'items': [
                {'producto_id': 'prod-123', 'cantidad': 5},
                {'producto_id': 'prod-456', 'cantidad': 10}
            ]
        }
        
        response = self.client.post('/api/inventario/descontar', json=data)
        
        assert response.status_code == 200
        result = response.get_json()
        assert result['success'] == True

    def test_buscar_productos_con_caracteres_especiales(self):
        self.mock_ejecutar_consulta.return_value = []
        
        response = self.client.get('/api/inventario/buscar?q=medicamento%20con%20ñ')
        
        assert response.status_code == 200
        self.mock_ejecutar_consulta.assert_called_once()

    def test_reservar_inventario_con_cantidad_cero(self):
        data = {
            'items': [
                {'producto_id': 'prod-123', 'cantidad': 0}
            ]
        }
        
        response = self.client.post('/api/inventario/reservar', json=data)
        
        # Debería pasar la validación de estructura pero fallar en el comando
        assert response.status_code in [200, 400]  # Depende de la validación del comando

    def test_descontar_inventario_con_cantidad_cero(self):
        data = {
            'items': [
                {'producto_id': 'prod-123', 'cantidad': 0}
            ]
        }
        
        response = self.client.post('/api/inventario/descontar', json=data)
        
        # Debería pasar la validación de estructura pero fallar en el comando
        assert response.status_code in [200, 400]  # Depende de la validación del comando
