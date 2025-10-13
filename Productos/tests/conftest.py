import pytest
import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.api import create_app
from src.config.db import db

# Configuración centralizada de URLs para tests
BASE_URLS = {
    'productos': os.getenv('TEST_PRODUCTOS_BASE_URL', 'http://localhost:5000'),
    'usuarios': os.getenv('TEST_USUARIOS_BASE_URL', 'http://localhost:5001'),
    'ventas': os.getenv('TEST_VENTAS_BASE_URL', 'http://localhost:5002'),
    'logistica': os.getenv('TEST_LOGISTICA_BASE_URL', 'http://localhost:5003')
}

# Rutas de API
API_ROUTES = {
    'productos': {
        'productos': '/productos/api/productos',
        'categorias': '/productos/api/categorias'
    },
    'usuarios': {
        'proveedores': '/usuarios/api/proveedores',
        'vendedores': '/usuarios/api/vendedores',
        'clientes': '/usuarios/api/clientes'
    },
    'ventas': {
        'visitas': '/ventas/api/visitas',
        'pedidos': '/ventas/api/pedidos'
    },
    'logistica': {
        'entregas': '/logistica/api/entregas',
        'inventario': '/logistica/api/inventario'
    }
}

# URLs completas para servicios externos
SERVICE_URLS = {
    'usuarios_service': f"{BASE_URLS['usuarios']}{API_ROUTES['usuarios']['proveedores']}",
    'ventas_service': f"{BASE_URLS['ventas']}{API_ROUTES['ventas']['pedidos']}",
    'logistica_service': f"{BASE_URLS['logistica']}{API_ROUTES['logistica']['inventario']}"
}

@pytest.fixture(scope='session')
def app():
    os.environ['TESTING'] = 'True'
    app = create_app()
    with app.app_context():
        db.create_all()
    yield app
    with app.app_context():
        db.drop_all()

@pytest.fixture(scope='function')
def client(app):
    return app.test_client()

@pytest.fixture(scope='function')
def app_context(app):
    with app.app_context():
        yield app

# Fixtures para URLs y configuración
@pytest.fixture
def base_urls():
    """Fixture que proporciona las URLs base para todos los servicios"""
    return BASE_URLS

@pytest.fixture
def api_routes():
    """Fixture que proporciona las rutas de API para todos los servicios"""
    return API_ROUTES

@pytest.fixture
def service_urls():
    """Fixture que proporciona las URLs completas de servicios externos"""
    return SERVICE_URLS

@pytest.fixture
def productos_urls():
    """Fixture específico para URLs de productos"""
    return {
        'productos': f"{BASE_URLS['productos']}{API_ROUTES['productos']['productos']}",
        'categorias': f"{BASE_URLS['productos']}{API_ROUTES['productos']['categorias']}"
    }

@pytest.fixture
def usuarios_service_url():
    """Fixture para la URL del servicio de usuarios"""
    return SERVICE_URLS['usuarios_service']

@pytest.fixture
def ventas_service_url():
    """Fixture para la URL del servicio de ventas"""
    return SERVICE_URLS['ventas_service']

@pytest.fixture
def logistica_service_url():
    """Fixture para la URL del servicio de logística"""
    return SERVICE_URLS['logistica_service']

# Funciones de utilidad
def get_productos_url(endpoint: str) -> str:
    """Obtiene la URL completa para un endpoint de productos"""
    return f"{BASE_URLS['productos']}{API_ROUTES['productos'][endpoint]}"

def get_service_url(service: str) -> str:
    """Obtiene la URL completa para un servicio externo"""
    return SERVICE_URLS[service]