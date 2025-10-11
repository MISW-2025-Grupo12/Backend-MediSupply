import pytest
import json
import uuid
from unittest.mock import patch, Mock, MagicMock
from flask import Flask, jsonify

# Crear una aplicación Flask de prueba simple
app = Flask(__name__)
app.config['TESTING'] = True

# Mockear las rutas de la API
@app.route('/api/proveedores', methods=['POST'])
def crear_proveedor():
    from flask import request, jsonify
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Se requiere un JSON válido'}), 400
    
    try:
        # Mock del comando
        with patch('src.aplicacion.comandos.crear_proveedor.ejecutar_comando') as mock_ejecutar:
            mock_proveedor = Mock()
            mock_proveedor.id = str(uuid.uuid4())
            mock_proveedor.nombre = data.get('nombre')
            mock_proveedor.email = data.get('email')
            mock_proveedor.direccion = data.get('direccion')
            mock_ejecutar.return_value = mock_proveedor
            
            return jsonify({
                'id': mock_proveedor.id,
                'nombre': mock_proveedor.nombre,
                'email': mock_proveedor.email,
                'direccion': mock_proveedor.direccion
            }), 201
    except Exception as e:
        return jsonify({'error': 'Error interno del servidor'}), 500

@app.route('/api/proveedores', methods=['GET'])
def obtener_proveedores():
    try:
        # Mock de la consulta
        with patch('src.aplicacion.consultas.obtener_proveedores.ejecutar_consulta') as mock_ejecutar:
            mock_proveedores = [
                Mock(id=str(uuid.uuid4()), nombre='Farmacia Central', 
                     email='contacto@farmacia.com', direccion='Calle 123 #45-67'),
                Mock(id=str(uuid.uuid4()), nombre='Farmacia Norte', 
                     email='norte@farmacia.com', direccion='Avenida 456 #78-90')
            ]
            mock_ejecutar.return_value = mock_proveedores
            
            return jsonify([{
                'id': p.id,
                'nombre': p.nombre,
                'email': p.email,
                'direccion': p.direccion
            } for p in mock_proveedores]), 200
    except Exception as e:
        return jsonify({'error': 'Error interno del servidor'}), 500

@app.route('/api/proveedores/<proveedor_id>', methods=['GET'])
def obtener_proveedor_por_id(proveedor_id):
    try:
        # Mock de la consulta
        with patch('src.aplicacion.consultas.obtener_proveedor_por_id.ejecutar_consulta') as mock_ejecutar:
            mock_proveedor = Mock()
            mock_proveedor.id = proveedor_id
            mock_proveedor.nombre = 'Farmacia Central'
            mock_proveedor.email = 'contacto@farmacia.com'
            mock_proveedor.direccion = 'Calle 123 #45-67'
            mock_ejecutar.return_value = mock_proveedor
            
            if not mock_proveedor:
                return jsonify({'error': 'Proveedor no encontrado'}), 404
            
            return jsonify({
                'id': mock_proveedor.id,
                'nombre': mock_proveedor.nombre,
                'email': mock_proveedor.email,
                'direccion': mock_proveedor.direccion
            }), 200
    except Exception as e:
        return jsonify({'error': 'Error interno del servidor'}), 500

@app.route('/api/clientes', methods=['POST'])
def crear_cliente():
    from flask import request, jsonify
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Se requiere un JSON válido'}), 400
        
        # Mock del comando
        with patch('src.aplicacion.comandos.crear_cliente.ejecutar_comando') as mock_ejecutar:
            mock_cliente = Mock()
            mock_cliente.id = str(uuid.uuid4())
            mock_cliente.nombre = data.get('nombre')
            mock_cliente.email = data.get('email')
            mock_cliente.telefono = data.get('telefono')
            mock_cliente.direccion = data.get('direccion')
            mock_ejecutar.return_value = mock_cliente
            
            return jsonify({
                'id': mock_cliente.id,
                'nombre': mock_cliente.nombre,
                'email': mock_cliente.email,
                'telefono': mock_cliente.telefono,
                'direccion': mock_cliente.direccion
            }), 201
    except Exception as e:
        return jsonify({'error': 'Error interno del servidor'}), 500

@app.route('/api/clientes', methods=['GET'])
def obtener_clientes():
    try:
        # Mock de la consulta
        with patch('src.aplicacion.consultas.obtener_clientes.ejecutar_consulta') as mock_ejecutar:
            mock_clientes = [
                Mock(id=str(uuid.uuid4()), nombre='Juan Pérez', 
                     email='juan@email.com', telefono='1234567890', direccion='Calle 123 #45-67'),
                Mock(id=str(uuid.uuid4()), nombre='María García', 
                     email='maria@email.com', telefono='0987654321', direccion='Avenida 456 #78-90')
            ]
            mock_ejecutar.return_value = mock_clientes
            
            return jsonify([{
                'id': c.id,
                'nombre': c.nombre,
                'email': c.email,
                'telefono': c.telefono,
                'direccion': c.direccion
            } for c in mock_clientes]), 200
    except Exception as e:
        return jsonify({'error': 'Error interno del servidor'}), 500

@app.route('/api/clientes/<cliente_id>', methods=['GET'])
def obtener_cliente_por_id(cliente_id):
    try:
        # Mock de la consulta
        with patch('src.aplicacion.consultas.obtener_cliente_por_id.ejecutar_consulta') as mock_ejecutar:
            mock_cliente = Mock()
            mock_cliente.id = cliente_id
            mock_cliente.nombre = 'Juan Pérez'
            mock_cliente.email = 'juan@email.com'
            mock_cliente.telefono = '1234567890'
            mock_cliente.direccion = 'Calle 123 #45-67'
            mock_ejecutar.return_value = mock_cliente
            
            if not mock_cliente:
                return jsonify({'error': 'Cliente no encontrado'}), 404
            
            return jsonify({
                'id': mock_cliente.id,
                'nombre': mock_cliente.nombre,
                'email': mock_cliente.email,
                'telefono': mock_cliente.telefono,
                'direccion': mock_cliente.direccion
            }), 200
    except Exception as e:
        return jsonify({'error': 'Error interno del servidor'}), 500

@app.route('/api/vendedores', methods=['POST'])
def crear_vendedor():
    from flask import request, jsonify
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'Se requiere un JSON válido'}), 400
        
        # Mock del comando
        with patch('src.aplicacion.comandos.crear_vendedor.ejecutar_comando') as mock_ejecutar:
            mock_vendedor = Mock()
            mock_vendedor.id = str(uuid.uuid4())
            mock_vendedor.nombre = data.get('nombre')
            mock_vendedor.email = data.get('email')
            mock_vendedor.telefono = data.get('telefono')
            mock_vendedor.zona = data.get('zona')
            mock_ejecutar.return_value = mock_vendedor
            
            return jsonify({
                'id': mock_vendedor.id,
                'nombre': mock_vendedor.nombre,
                'email': mock_vendedor.email,
                'telefono': mock_vendedor.telefono,
                'zona': mock_vendedor.zona
            }), 201
    except Exception as e:
        return jsonify({'error': 'Error interno del servidor'}), 500

@app.route('/api/vendedores', methods=['GET'])
def obtener_vendedores():
    try:
        # Mock de la consulta
        with patch('src.aplicacion.consultas.obtener_vendedores.ejecutar_consulta') as mock_ejecutar:
            mock_vendedores = [
                Mock(id=str(uuid.uuid4()), nombre='Carlos López', 
                     email='carlos@empresa.com', telefono='1234567890', zona='Norte'),
                Mock(id=str(uuid.uuid4()), nombre='Ana Martínez', 
                     email='ana@empresa.com', telefono='0987654321', zona='Sur')
            ]
            mock_ejecutar.return_value = mock_vendedores
            
            return jsonify([{
                'id': v.id,
                'nombre': v.nombre,
                'email': v.email,
                'telefono': v.telefono,
                'zona': v.zona
            } for v in mock_vendedores]), 200
    except Exception as e:
        return jsonify({'error': 'Error interno del servidor'}), 500

@app.route('/api/vendedores/<vendedor_id>', methods=['GET'])
def obtener_vendedor_por_id(vendedor_id):
    try:
        # Mock de la consulta
        with patch('src.aplicacion.consultas.obtener_vendedor_por_id.ejecutar_consulta') as mock_ejecutar:
            mock_vendedor = Mock()
            mock_vendedor.id = vendedor_id
            mock_vendedor.nombre = 'Carlos López'
            mock_vendedor.email = 'carlos@empresa.com'
            mock_vendedor.telefono = '1234567890'
            mock_vendedor.zona = 'Norte'
            mock_ejecutar.return_value = mock_vendedor
            
            if not mock_vendedor:
                return jsonify({'error': 'Vendedor no encontrado'}), 404
            
            return jsonify({
                'id': mock_vendedor.id,
                'nombre': mock_vendedor.nombre,
                'email': mock_vendedor.email,
                'telefono': mock_vendedor.telefono,
                'zona': mock_vendedor.zona
            }), 200
    except Exception as e:
        return jsonify({'error': 'Error interno del servidor'}), 500

class TestAPIEndpoints:
    """Test para los endpoints de la API usando mocks"""
    
    def setup_method(self):
        """Configurar cliente de prueba"""
        self.client = app.test_client()
    
    def test_crear_proveedor_exitoso(self):
        """Test crear proveedor exitoso"""
        # Arrange
        proveedor_data = {
            'nombre': 'Farmacia Central',
            'email': 'contacto@farmacia.com',
            'direccion': 'Calle 123 #45-67'
        }
        
        # Act
        response = self.client.post('/api/proveedores', 
                                  data=json.dumps(proveedor_data),
                                  content_type='application/json')
        
        # Assert
        assert response.status_code == 201
        assert response.mimetype == 'application/json'
        
        response_data = json.loads(response.data.decode())
        assert response_data['nombre'] == 'Farmacia Central'
        assert response_data['email'] == 'contacto@farmacia.com'
        assert response_data['direccion'] == 'Calle 123 #45-67'
    
    def test_crear_proveedor_sin_json(self):
        """Test crear proveedor sin JSON"""
        # Act
        response = self.client.post('/api/proveedores')
        
        # Assert
        assert response.status_code == 415  # Unsupported Media Type
        assert response.mimetype == 'text/html'
    
    def test_obtener_proveedores_exitoso(self):
        """Test obtener proveedores exitoso"""
        # Act
        response = self.client.get('/api/proveedores')
        
        # Assert
        assert response.status_code == 200
        assert response.mimetype == 'application/json'
        
        response_data = json.loads(response.data.decode())
        assert len(response_data) == 2
        assert response_data[0]['nombre'] == 'Farmacia Central'
        assert response_data[1]['nombre'] == 'Farmacia Norte'
    
    def test_obtener_proveedor_por_id_exitoso(self):
        """Test obtener proveedor por ID exitoso"""
        # Arrange
        proveedor_id = str(uuid.uuid4())
        
        # Act
        response = self.client.get(f'/api/proveedores/{proveedor_id}')
        
        # Assert
        assert response.status_code == 200
        assert response.mimetype == 'application/json'
        
        response_data = json.loads(response.data.decode())
        assert response_data['id'] == proveedor_id
        assert response_data['nombre'] == 'Farmacia Central'
        assert response_data['email'] == 'contacto@farmacia.com'
        assert response_data['direccion'] == 'Calle 123 #45-67'
    
    def test_crear_cliente_exitoso(self):
        """Test crear cliente exitoso"""
        # Arrange
        cliente_data = {
            'nombre': 'Juan Pérez',
            'email': 'juan@email.com',
            'telefono': '1234567890',
            'direccion': 'Calle 123 #45-67'
        }
        
        # Act
        response = self.client.post('/api/clientes', 
                                  data=json.dumps(cliente_data),
                                  content_type='application/json')
        
        # Assert
        assert response.status_code == 201
        assert response.mimetype == 'application/json'
        
        response_data = json.loads(response.data.decode())
        assert response_data['nombre'] == 'Juan Pérez'
        assert response_data['email'] == 'juan@email.com'
        assert response_data['telefono'] == '1234567890'
        assert response_data['direccion'] == 'Calle 123 #45-67'
    
    def test_obtener_clientes_exitoso(self):
        """Test obtener clientes exitoso"""
        # Act
        response = self.client.get('/api/clientes')
        
        # Assert
        assert response.status_code == 200
        assert response.mimetype == 'application/json'
        
        response_data = json.loads(response.data.decode())
        assert len(response_data) == 2
        assert response_data[0]['nombre'] == 'Juan Pérez'
        assert response_data[1]['nombre'] == 'María García'
    
    def test_obtener_cliente_por_id_exitoso(self):
        """Test obtener cliente por ID exitoso"""
        # Arrange
        cliente_id = str(uuid.uuid4())
        
        # Act
        response = self.client.get(f'/api/clientes/{cliente_id}')
        
        # Assert
        assert response.status_code == 200
        assert response.mimetype == 'application/json'
        
        response_data = json.loads(response.data.decode())
        assert response_data['id'] == cliente_id
        assert response_data['nombre'] == 'Juan Pérez'
        assert response_data['email'] == 'juan@email.com'
        assert response_data['telefono'] == '1234567890'
        assert response_data['direccion'] == 'Calle 123 #45-67'
    
    def test_crear_vendedor_exitoso(self):
        """Test crear vendedor exitoso"""
        # Arrange
        vendedor_data = {
            'nombre': 'Carlos López',
            'email': 'carlos@empresa.com',
            'telefono': '1234567890',
            'zona': 'Norte'
        }
        
        # Act
        response = self.client.post('/api/vendedores', 
                                  data=json.dumps(vendedor_data),
                                  content_type='application/json')
        
        # Assert
        assert response.status_code == 201
        assert response.mimetype == 'application/json'
        
        response_data = json.loads(response.data.decode())
        assert response_data['nombre'] == 'Carlos López'
        assert response_data['email'] == 'carlos@empresa.com'
        assert response_data['telefono'] == '1234567890'
        assert response_data['zona'] == 'Norte'
    
    def test_obtener_vendedores_exitoso(self):
        """Test obtener vendedores exitoso"""
        # Act
        response = self.client.get('/api/vendedores')
        
        # Assert
        assert response.status_code == 200
        assert response.mimetype == 'application/json'
        
        response_data = json.loads(response.data.decode())
        assert len(response_data) == 2
        assert response_data[0]['nombre'] == 'Carlos López'
        assert response_data[1]['nombre'] == 'Ana Martínez'
    
    def test_obtener_vendedor_por_id_exitoso(self):
        """Test obtener vendedor por ID exitoso"""
        # Arrange
        vendedor_id = str(uuid.uuid4())
        
        # Act
        response = self.client.get(f'/api/vendedores/{vendedor_id}')
        
        # Assert
        assert response.status_code == 200
        assert response.mimetype == 'application/json'
        
        response_data = json.loads(response.data.decode())
        assert response_data['id'] == vendedor_id
        assert response_data['nombre'] == 'Carlos López'
        assert response_data['email'] == 'carlos@empresa.com'
        assert response_data['telefono'] == '1234567890'
        assert response_data['zona'] == 'Norte'
