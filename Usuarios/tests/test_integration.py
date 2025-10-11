import pytest
import json
import uuid
import tempfile
import os
from unittest.mock import patch, Mock

# Configurar el path para importar los módulos
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

class TestIntegration:
    """Pruebas de integración usando la aplicación Flask completa con SQLite"""
    
    def setup_method(self):
        """Configurar aplicación Flask real para cada prueba"""
        # Establecer variable de entorno para modo de pruebas
        os.environ['TESTING'] = 'True'
        
        # Importar y crear la aplicación real
        from api import create_app
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['WTF_CSRF_ENABLED'] = False
        
        self.client = self.app.test_client()
    
    def teardown_method(self):
        """Limpiar después de cada prueba"""
        # Limpiar variable de entorno
        if 'TESTING' in os.environ:
            del os.environ['TESTING']
    
    def test_health_endpoint(self):
        """Prueba de integración: endpoint de salud"""
        response = self.client.get('/health')
        assert response.status_code == 200
        assert response.mimetype == 'application/json'
        
        response_data = json.loads(response.data.decode())
        assert response_data['status'] == 'up'
        assert 'endpoints' in response_data
        assert len(response_data['endpoints']) > 0
    
    def test_proveedor_workflow(self):
        """Prueba de integración: flujo completo de proveedores"""
        # Mock de los comandos y consultas para simular el flujo real
        with patch('src.aplicacion.comandos.crear_proveedor.ejecutar_comando') as mock_crear, \
             patch('src.aplicacion.consultas.obtener_proveedores.ejecutar_consulta') as mock_obtener, \
             patch('src.aplicacion.consultas.obtener_proveedor_por_id.ejecutar_consulta') as mock_obtener_id:
            
            # Configurar mocks
            proveedor_id = str(uuid.uuid4())
            mock_proveedor = Mock()
            mock_proveedor.id = proveedor_id
            mock_proveedor.nombre = 'Farmacia Central'
            mock_proveedor.email = 'contacto@farmacia.com'
            mock_proveedor.direccion = 'Calle 123 #45-67'
            
            mock_crear.return_value = mock_proveedor
            mock_obtener.return_value = [mock_proveedor]
            mock_obtener_id.return_value = mock_proveedor
            
            # 1. Crear proveedor
            proveedor_data = {
                'nombre': 'Farmacia Central',
                'email': 'contacto@farmacia.com',
                'direccion': 'Calle 123 #45-67'
            }
            
            response = self.client.post('/api/proveedores', 
                                      data=json.dumps(proveedor_data),
                                      content_type='application/json')
            assert response.status_code == 201
            
            # 2. Obtener lista de proveedores
            response = self.client.get('/api/proveedores')
            assert response.status_code == 200
            response_data = json.loads(response.data.decode())
            assert len(response_data) == 1
            assert response_data[0]['nombre'] == 'Farmacia Central'
            
            # 3. Obtener proveedor por ID
            response = self.client.get(f'/api/proveedores/{proveedor_id}')
            assert response.status_code == 200
            response_data = json.loads(response.data.decode())
            assert response_data['id'] == proveedor_id
    
    def test_cliente_workflow(self):
        """Prueba de integración: flujo completo de clientes"""
        with patch('src.aplicacion.comandos.crear_cliente.ejecutar_comando') as mock_crear, \
             patch('src.aplicacion.consultas.obtener_clientes.ejecutar_consulta') as mock_obtener, \
             patch('src.aplicacion.consultas.obtener_cliente_por_id.ejecutar_consulta') as mock_obtener_id:
            
            cliente_id = str(uuid.uuid4())
            mock_cliente = Mock()
            mock_cliente.id = cliente_id
            mock_cliente.nombre = 'Juan Pérez'
            mock_cliente.email = 'juan@email.com'
            mock_cliente.telefono = '1234567890'
            mock_cliente.direccion = 'Calle 123 #45-67'
            
            mock_crear.return_value = mock_cliente
            mock_obtener.return_value = [mock_cliente]
            mock_obtener_id.return_value = mock_cliente
            
            # 1. Crear cliente
            cliente_data = {
                'nombre': 'Juan Pérez',
                'email': 'juan@email.com',
                'telefono': '1234567890',
                'direccion': 'Calle 123 #45-67'
            }
            
            response = self.client.post('/api/clientes', 
                                      data=json.dumps(cliente_data),
                                      content_type='application/json')
            assert response.status_code == 201
            
            # 2. Obtener lista de clientes
            response = self.client.get('/api/clientes')
            assert response.status_code == 200
            response_data = json.loads(response.data.decode())
            assert len(response_data) == 1
            assert response_data[0]['nombre'] == 'Juan Pérez'
            
            # 3. Obtener cliente por ID
            response = self.client.get(f'/api/clientes/{cliente_id}')
            assert response.status_code == 200
            response_data = json.loads(response.data.decode())
            assert response_data['id'] == cliente_id
    
    def test_vendedor_workflow(self):
        """Prueba de integración: flujo completo de vendedores"""
        with patch('src.aplicacion.comandos.crear_vendedor.ejecutar_comando') as mock_crear, \
             patch('src.aplicacion.consultas.obtener_vendedores.ejecutar_consulta') as mock_obtener, \
             patch('src.aplicacion.consultas.obtener_vendedor_por_id.ejecutar_consulta') as mock_obtener_id:
            
            vendedor_id = str(uuid.uuid4())
            mock_vendedor = Mock()
            mock_vendedor.id = vendedor_id
            mock_vendedor.nombre = 'Carlos López'
            mock_vendedor.email = 'carlos@empresa.com'
            mock_vendedor.telefono = '1234567890'
            mock_vendedor.zona = 'Norte'
            
            mock_crear.return_value = mock_vendedor
            mock_obtener.return_value = [mock_vendedor]
            mock_obtener_id.return_value = mock_vendedor
            
            # 1. Crear vendedor
            vendedor_data = {
                'nombre': 'Carlos López',
                'email': 'carlos@empresa.com',
                'telefono': '1234567890',
                'zona': 'Norte'
            }
            
            response = self.client.post('/api/vendedores', 
                                      data=json.dumps(vendedor_data),
                                      content_type='application/json')
            assert response.status_code == 201
            
            # 2. Obtener lista de vendedores
            response = self.client.get('/api/vendedores')
            assert response.status_code == 200
            response_data = json.loads(response.data.decode())
            assert len(response_data) == 1
            assert response_data[0]['nombre'] == 'Carlos López'
            
            # 3. Obtener vendedor por ID
            response = self.client.get(f'/api/vendedores/{vendedor_id}')
            assert response.status_code == 200
            response_data = json.loads(response.data.decode())
            assert response_data['id'] == vendedor_id
    
    def test_error_scenarios(self):
        """Prueba de integración: escenarios de error"""
        # Test 404 - Proveedor no encontrado
        with patch('src.aplicacion.consultas.obtener_proveedor_por_id.ejecutar_consulta') as mock_obtener:
            mock_obtener.return_value = None
            
            response = self.client.get(f'/api/proveedores/{str(uuid.uuid4())}')
            assert response.status_code == 404
            response_data = json.loads(response.data.decode())
            assert 'error' in response_data
        
        # Test 500 - Error interno
        with patch('src.aplicacion.comandos.crear_proveedor.ejecutar_comando') as mock_crear:
            mock_crear.side_effect = Exception("Error de base de datos")
            
            proveedor_data = {
                'nombre': 'Farmacia Central',
                'email': 'contacto@farmacia.com',
                'direccion': 'Calle 123 #45-67'
            }
            
            response = self.client.post('/api/proveedores',
                                      data=json.dumps(proveedor_data),
                                      content_type='application/json')
            assert response.status_code == 500
            response_data = json.loads(response.data.decode())
            assert 'error' in response_data
    
    def test_database_connection(self):
        """Prueba de integración: verificar que la conexión a SQLite funciona"""
        # Verificar que la aplicación se creó correctamente
        assert self.app is not None
        assert self.app.config['TESTING'] == True
        
        # Verificar que la base de datos está configurada
        assert 'SQLALCHEMY_DATABASE_URI' in self.app.config
        assert 'sqlite:///' in self.app.config['SQLALCHEMY_DATABASE_URI']
        
        # Verificar que las tablas se crearon
        with self.app.app_context():
            from src.config.db import db
            # Verificar que la base de datos está inicializada
            assert db.engine is not None
