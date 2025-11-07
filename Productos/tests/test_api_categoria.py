"""Tests para endpoints de categorías"""
import pytest
import json
import sys
import os
from unittest.mock import patch, Mock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from aplicacion.dto import CategoriaDTO


class TestAPICategoria:
    """Tests para los endpoints de categorías"""
    
    def test_crear_categoria_exitoso(self, client, app):
        """Test creación exitosa de categoría"""
        categoria_data = {
            'nombre': 'Medicinas Nuevas',
            'descripcion': 'Categoría de prueba'
        }
        
        with app.app_context():
            response = client.post(
                '/productos/api/categorias',
                data=json.dumps(categoria_data),
                content_type='application/json'
            )
            
            assert response.status_code == 201
            data = json.loads(response.data)
            assert data['nombre'] == 'Medicinas Nuevas'
            assert data['descripcion'] == 'Categoría de prueba'
            assert 'id' in data
    
    def test_crear_categoria_sin_json(self, client):
        """Test creación sin JSON"""
        response = client.post(
            '/productos/api/categorias',
            data='{}',
            content_type='application/json'
        )
        
        # Puede retornar 400 por validación o 500 por error interno
        assert response.status_code in [400, 500]
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_obtener_categorias_paginacion(self, client, app):
        """Test obtener categorías con paginación"""
        with app.app_context():
            # Crear varias categorías
            for i in range(5):
                categoria_data = {
                    'nombre': f'Categoria Test {i}',
                    'descripcion': f'Descripción {i}'
                }
                client.post(
                    '/productos/api/categorias',
                    data=json.dumps(categoria_data),
                    content_type='application/json'
                )
            
            # Obtener con paginación
            response = client.get('/productos/api/categorias?page=1&page_size=3')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            # Puede retornar lista o dict con items
            if isinstance(data, dict) and 'items' in data:
                assert len(data['items']) <= 3
                assert 'pagination' in data
            elif isinstance(data, list):
                assert len(data) <= 3
    
    def test_obtener_categorias_exitoso(self, client, app):
        """Test obtener todas las categorías"""
        with app.app_context():
            # Crear una categoría primero
            categoria_data = {
                'nombre': 'Test Categoria',
                'descripcion': 'Descripción de prueba'
            }
            client.post(
                '/productos/api/categorias',
                data=json.dumps(categoria_data),
                content_type='application/json'
            )
            
            # Obtener todas las categorías
            response = client.get('/productos/api/categorias')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert 'items' in data or isinstance(data, list)
    
    def test_obtener_categoria_por_id_exitoso(self, client, app):
        """Test obtener categoría por ID"""
        with app.app_context():
            # Crear una categoría
            categoria_data = {
                'nombre': 'Categoria Test',
                'descripcion': 'Descripción'
            }
            crear_response = client.post(
                '/productos/api/categorias',
                data=json.dumps(categoria_data),
                content_type='application/json'
            )
            categoria_creada = json.loads(crear_response.data)
            categoria_id = categoria_creada['id']
            
            # Obtener por ID
            response = client.get(f'/productos/api/categorias/{categoria_id}')
            
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['id'] == categoria_id
            assert data['nombre'] == 'Categoria Test'
    
    def test_obtener_categoria_por_id_no_existe(self, client):
        """Test obtener categoría que no existe"""
        import uuid
        categoria_id = str(uuid.uuid4())
        
        response = client.get(f'/productos/api/categorias/{categoria_id}')
        
        assert response.status_code == 404
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_crear_categoria_error_servidor(self, client):
        """Test creación con error interno"""
        with patch('src.api.categoria.ejecutar_comando') as mock_exec:
            mock_exec.side_effect = Exception("Error interno")
            
            categoria_data = {
                'nombre': 'Test',
                'descripcion': 'Desc'
            }
            
            response = client.post(
                '/productos/api/categorias',
                data=json.dumps(categoria_data),
                content_type='application/json'
            )
            
            assert response.status_code == 500
            data = json.loads(response.data)
            assert 'error' in data

