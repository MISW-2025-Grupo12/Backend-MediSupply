"""
Tests para el endpoint de versión del Auth-Service
"""

def test_version_endpoint_exists(client):
    """Test que verifica que el endpoint /version existe"""
    response = client.get('/version')
    assert response.status_code == 200


def test_version_endpoint_returns_json(client):
    """Test que verifica que el endpoint retorna JSON"""
    response = client.get('/version')
    assert response.content_type == 'application/json'


def test_version_endpoint_structure(client):
    """Test que verifica la estructura de la respuesta"""
    response = client.get('/version')
    data = response.get_json()
    
    # Verificar que todos los campos esperados están presentes
    assert 'version' in data
    assert 'build_date' in data
    assert 'commit_hash' in data
    assert 'environment' in data


def test_version_endpoint_default_values(client):
    """Test que verifica los valores por defecto en desarrollo"""
    response = client.get('/version')
    data = response.get_json()
    
    # En ambiente de prueba sin variables de entorno, debería tener valores por defecto
    assert isinstance(data['version'], str)
    assert isinstance(data['build_date'], str)
    assert isinstance(data['commit_hash'], str)
    assert isinstance(data['environment'], str)
    
    # Valores por defecto esperados
    assert data['version'] == '1.0.0-dev'
    assert data['commit_hash'] == 'unknown'
    assert data['environment'] == 'development'

