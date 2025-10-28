"""
Tests para el API de bodegas
"""

import pytest
import json
from unittest.mock import patch, MagicMock
from src.api.bodegas import bp
from src.aplicacion.comandos.inicializar_bodegas import InicializarBodegas
from src.aplicacion.consultas.obtener_bodegas import ObtenerBodegas
from src.aplicacion.consultas.obtener_productos_por_bodega import ObtenerProductosPorBodega
from src.aplicacion.consultas.obtener_ubicaciones_producto import ObtenerUbicacionesProducto
from .conftest import get_bodegas_url, get_bodegas_inicializar_url, get_bodega_productos_url, get_producto_ubicaciones_url


class TestApiBodegas:
    """Tests para el API de bodegas"""

    @pytest.fixture
    def client(self, app):
        """Cliente de prueba para el API de bodegas"""

        return app.test_client()

    def test_obtener_bodegas_exitoso(self, client):
        """Test para obtener bodegas exitosamente"""
        # Mock de la consulta
        bodegas_mock = [
            {
                'id': 'bodega-1',
                'nombre': 'Bodega Central',
                'direccion': 'Av. Principal #123',
                'created_at': '2025-01-01T00:00:00',
                'updated_at': '2025-01-01T00:00:00'
            },
            {
                'id': 'bodega-2',
                'nombre': 'Bodega Norte',
                'direccion': 'Av. Norte #456',
                'created_at': '2025-01-01T00:00:00',
                'updated_at': '2025-01-01T00:00:00'
            }
        ]
        
        with patch('src.api.bodegas.ejecutar_consulta') as mock_ejecutar:
            mock_ejecutar.return_value = bodegas_mock
            
            response = client.get(get_bodegas_url())
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert isinstance(data, dict)
            assert 'items' in data
            assert 'pagination' in data
            assert len(data['items']) == 2
            assert data['items'][0]['nombre'] == 'Bodega Central'
            assert data['items'][1]['nombre'] == 'Bodega Norte'

    def test_obtener_bodegas_error(self, client):
        """Test para manejo de errores al obtener bodegas"""
        with patch('src.api.bodegas.ejecutar_consulta') as mock_ejecutar:
            mock_ejecutar.side_effect = Exception("Error de base de datos")
            
            response = client.get(get_bodegas_url())
            
            assert response.status_code == 500
            data = json.loads(response.data)
            assert 'error' in data

    def test_inicializar_bodegas_exitoso(self, client):
        """Test para inicializar bodegas exitosamente"""
        resultado_mock = {
            'message': 'Bodegas inicializadas exitosamente',
            'count': 3
        }
        
        with patch('src.api.bodegas.ejecutar_comando') as mock_ejecutar:
            mock_ejecutar.return_value = resultado_mock
            
            response = client.post(get_bodegas_inicializar_url())
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['message'] == 'Bodegas inicializadas exitosamente'
            assert data['count'] == 3

    def test_inicializar_bodegas_error(self, client):
        """Test para manejo de errores al inicializar bodegas"""
        with patch('src.api.bodegas.ejecutar_comando') as mock_ejecutar:
            mock_ejecutar.side_effect = Exception("Error al crear bodegas")
            
            response = client.post(get_bodegas_inicializar_url())
            
            assert response.status_code == 500
            data = json.loads(response.data)
            assert 'error' in data

    def test_obtener_productos_por_bodega_exitoso(self, client):
        """Test para obtener productos por bodega exitosamente"""
        productos_mock = {
            'bodega_id': 'bodega-1',
            'nombre_bodega': 'Bodega Central',
            'direccion_bodega': 'Av. Principal #123',
            'productos': [
                {
                    'producto_id': 'prod-1',
                    'total_disponible': 50,
                    'total_reservado': 10,
                    'ubicaciones': [
                        {
                            'pasillo': 'A',
                            'estante': '5',
                            'cantidad_disponible': 50,
                            'cantidad_reservada': 10
                        }
                    ]
                }
            ]
        }
        
        with patch('src.api.bodegas.ejecutar_consulta') as mock_ejecutar:
            mock_ejecutar.return_value = productos_mock
            
            response = client.get(get_bodega_productos_url('bodega-1'))
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['bodega_id'] == 'bodega-1'
            assert data['nombre_bodega'] == 'Bodega Central'
            assert len(data['productos']) == 1

    def test_obtener_productos_por_bodega_error(self, client):
        """Test para manejo de errores al obtener productos por bodega"""
        with patch('src.api.bodegas.ejecutar_consulta') as mock_ejecutar:
            mock_ejecutar.side_effect = Exception("Error al consultar productos")
            
            response = client.get(get_bodega_productos_url('bodega-1'))
            
            assert response.status_code == 500
            data = json.loads(response.data)
            assert 'error' in data

    def test_obtener_ubicaciones_producto_exitoso(self, client):
        """Test para obtener ubicaciones de producto exitosamente"""
        ubicaciones_mock = {
            'producto_id': 'prod-1',
            'ubicaciones': [
                {
                    'bodega_id': 'bodega-1',
                    'bodega_nombre': 'Bodega Central',
                    'bodega_direccion': 'Av. Principal #123',
                    'total_cantidad_disponible': 50,
                    'total_cantidad_reservada': 10,
                    'ubicaciones_fisicas': [
                        {
                            'pasillo': 'A',
                            'estante': '5',
                            'cantidad_disponible': 50,
                            'cantidad_reservada': 10,
                            'fecha_vencimiento': '2025-12-31T00:00:00',
                            'ubicacion_descripcion': 'Bodega Central - Pasillo A - Estante 5'
                        }
                    ]
                }
            ],
            'total_bodegas': 1,
            'total_cantidad_disponible': 50,
            'total_cantidad_reservada': 10,
            'mensaje': 'Producto encontrado en 1 bodega(s)'
        }
        
        with patch('src.api.bodegas.ejecutar_consulta') as mock_ejecutar:
            mock_ejecutar.return_value = ubicaciones_mock
            
            response = client.get(get_producto_ubicaciones_url('prod-1'))
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['producto_id'] == 'prod-1'
            assert data['total_bodegas'] == 1
            assert len(data['ubicaciones']) == 1
            assert data['ubicaciones'][0]['bodega_nombre'] == 'Bodega Central'

    def test_obtener_ubicaciones_producto_error(self, client):
        """Test para manejo de errores al obtener ubicaciones de producto"""
        with patch('src.api.bodegas.ejecutar_consulta') as mock_ejecutar:
            mock_ejecutar.side_effect = Exception("Error al consultar ubicaciones")
            
            response = client.get(get_producto_ubicaciones_url('prod-1'))
            
            assert response.status_code == 500
            data = json.loads(response.data)
            assert 'error' in data
