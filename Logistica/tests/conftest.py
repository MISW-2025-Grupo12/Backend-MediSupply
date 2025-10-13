import pytest
import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from src.api import create_app
from src.config.db import db

# Configuración centralizada de URLs para tests
BASE_URLS = {
    'logistica': os.getenv('TEST_LOGISTICA_BASE_URL', 'http://localhost:5003'),
    'productos': os.getenv('TEST_PRODUCTOS_BASE_URL', 'http://localhost:5000'),
    'usuarios': os.getenv('TEST_USUARIOS_BASE_URL', 'http://localhost:5001'),
    'ventas': os.getenv('TEST_VENTAS_BASE_URL', 'http://localhost:5002')
}

# Rutas de API
API_ROUTES = {
    'logistica': {
        'entregas': '/logistica/api/entregas',
        'inventario': '/logistica/api/inventario',
        'inventario_buscar': '/logistica/api/inventario/buscar',
        'inventario_reservar': '/logistica/api/inventario/reservar',
        'inventario_descontar': '/logistica/api/inventario/descontar',
        'inventario_producto': '/logistica/api/inventario/producto'
    },
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
    }
}

# URLs completas para servicios externos
SERVICE_URLS = {
    'productos_service': f"{BASE_URLS['productos']}{API_ROUTES['productos']['productos']}",
    'usuarios_service': f"{BASE_URLS['usuarios']}{API_ROUTES['usuarios']['proveedores']}",
    'ventas_service': f"{BASE_URLS['ventas']}{API_ROUTES['ventas']['pedidos']}"
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
def logistica_urls():
    """Fixture específico para URLs de logística"""
    return {
        'entregas': f"{BASE_URLS['logistica']}{API_ROUTES['logistica']['entregas']}",
        'inventario': f"{BASE_URLS['logistica']}{API_ROUTES['logistica']['inventario']}",
        'inventario_buscar': f"{BASE_URLS['logistica']}{API_ROUTES['logistica']['inventario_buscar']}",
        'inventario_reservar': f"{BASE_URLS['logistica']}{API_ROUTES['logistica']['inventario_reservar']}",
        'inventario_descontar': f"{BASE_URLS['logistica']}{API_ROUTES['logistica']['inventario_descontar']}",
        'inventario_producto': f"{BASE_URLS['logistica']}{API_ROUTES['logistica']['inventario_producto']}"
    }

@pytest.fixture
def productos_service_url():
    """Fixture para la URL del servicio de productos"""
    return SERVICE_URLS['productos_service']

@pytest.fixture
def usuarios_service_url():
    """Fixture para la URL del servicio de usuarios"""
    return SERVICE_URLS['usuarios_service']

# Funciones de utilidad
def get_logistica_url(endpoint: str) -> str:
    """Obtiene la URL completa para un endpoint de logística"""
    return f"{BASE_URLS['logistica']}{API_ROUTES['logistica'][endpoint]}"

def get_service_url(service: str) -> str:
    """Obtiene la URL completa para un servicio externo"""
    return SERVICE_URLS[service]
