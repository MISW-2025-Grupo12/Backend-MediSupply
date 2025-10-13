import pytest
import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.api import create_app
from src.config.db import db

# Configuración centralizada de URLs para tests
BASE_URLS = {
    'ventas': os.getenv('TEST_VENTAS_BASE_URL', 'http://localhost:5002'),
    'usuarios': os.getenv('TEST_USUARIOS_BASE_URL', 'http://localhost:5001'),
    'productos': os.getenv('TEST_PRODUCTOS_BASE_URL', 'http://localhost:5000'),
    'logistica': os.getenv('TEST_LOGISTICA_BASE_URL', 'http://localhost:5003')
}

# Rutas de API
API_ROUTES = {
    'ventas': {
        'visitas': '/ventas/api/visitas',
        'pedidos': '/ventas/api/pedidos'
    },
    'usuarios': {
        'proveedores': '/usuarios/api/proveedores',
        'vendedores': '/usuarios/api/vendedores',
        'clientes': '/usuarios/api/clientes'
    },
    'productos': {
        'productos': '/productos/api/productos',
        'categorias': '/productos/api/categorias'
    },
    'logistica': {
        'entregas': '/logistica/api/entregas',
        'inventario': '/logistica/api/inventario'
    }
}

# URLs completas para servicios externos
SERVICE_URLS = {
    'usuarios_service': f"{BASE_URLS['usuarios']}{API_ROUTES['usuarios']['vendedores']}",
    'productos_service': f"{BASE_URLS['productos']}{API_ROUTES['productos']['productos']}",
    'logistica_service': f"{BASE_URLS['logistica']}{API_ROUTES['logistica']['inventario']}"
}

@pytest.fixture(scope='session')
def app():
    os.environ['TESTING'] = 'True'
    app = create_app()
    # No necesitamos llamar db.create_all() aquí porque ya se llama en init_db()
    yield app
    # No necesitamos llamar db.drop_all() aquí porque puede causar conflictos

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
def ventas_urls():
    """Fixture específico para URLs de ventas"""
    return {
        'visitas': f"{BASE_URLS['ventas']}{API_ROUTES['ventas']['visitas']}",
        'pedidos': f"{BASE_URLS['ventas']}{API_ROUTES['ventas']['pedidos']}"
    }

@pytest.fixture
def usuarios_service_url():
    """Fixture para la URL del servicio de usuarios"""
    return SERVICE_URLS['usuarios_service']

@pytest.fixture
def productos_service_url():
    """Fixture para la URL del servicio de productos"""
    return SERVICE_URLS['productos_service']

@pytest.fixture
def logistica_service_url():
    """Fixture para la URL del servicio de logística"""
    return SERVICE_URLS['logistica_service']

# Funciones de utilidad
def get_ventas_url(endpoint: str) -> str:
    """Obtiene la URL completa para un endpoint de ventas"""
    return f"{BASE_URLS['ventas']}{API_ROUTES['ventas'][endpoint]}"

def get_service_url(service: str) -> str:
    """Obtiene la URL completa para un servicio externo"""
    return SERVICE_URLS[service]