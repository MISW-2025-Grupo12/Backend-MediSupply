import pytest
import sys
import os
import json
from unittest.mock import Mock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from api import create_app
from aplicacion.dto import CategoriaDTO


class TestAPICategoria:
    
    def setup_method(self):
        """Setup para cada test"""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.client = self.app.test_client()
    
    def test_crear_categoria_exitoso(self):
        """Test crear categoría exitoso via API"""
        # Arrange
        categoria_data = {
            "nombre": "Medicamentos",
            "descripcion": "Medicamentos generales"
        }
        
        with patch('aplicacion.comandos.crear_categoria.CrearCategoriaHandler') as mock_handler_class:
            mock_handler = Mock()
            mock_handler_class.return_value = mock_handler
            
            # Mock del resultado
            mock_resultado = CategoriaDTO(
                id="123e4567-e89b-12d3-a456-426614174000",
                nombre="Medicamentos",
                descripcion="Medicamentos generales"
            )
            mock_handler.handle.return_value = mock_resultado
            
            # Act
            response = self.client.post('/api/productos/categorias/', 
                                      data=json.dumps(categoria_data),
                                      content_type='application/json')
            
            # Assert
            assert response.status_code == 201
            data = json.loads(response.data)
            assert data['nombre'] == "Medicamentos"
            assert data['descripcion'] == "Medicamentos generales"
    
    def test_crear_categoria_nombre_vacio(self):
        """Test crear categoría con nombre vacío"""
        # Arrange
        categoria_data = {
            "nombre": "",  # Nombre vacío
            "descripcion": "Medicamentos generales"
        }
        
        with patch('aplicacion.comandos.crear_categoria.CrearCategoriaHandler') as mock_handler_class:
            mock_handler = Mock()
            mock_handler_class.return_value = mock_handler
            mock_handler.handle.side_effect = ValueError("El nombre no puede estar vacío")
            
            # Act
            response = self.client.post('/api/productos/categorias/', 
                                      data=json.dumps(categoria_data),
                                      content_type='application/json')
            
            # Assert
            assert response.status_code == 400
            data = json.loads(response.data)
            assert 'error' in data
    
    def test_obtener_categorias_exitoso(self):
        """Test obtener todas las categorías via API"""
        # Arrange
        with patch('aplicacion.consultas.obtener_categorias.ObtenerCategoriasHandler') as mock_handler_class:
            mock_handler = Mock()
            mock_handler_class.return_value = mock_handler
            
            # Mock del resultado
            mock_categorias = [
                CategoriaDTO(
                    id="123e4567-e89b-12d3-a456-426614174000",
                    nombre="Medicamentos",
                    descripcion="Medicamentos generales"
                ),
                CategoriaDTO(
                    id="456e7890-e89b-12d3-a456-426614174001",
                    nombre="Suplementos",
                    descripcion="Suplementos vitamínicos"
                )
            ]
            mock_handler.handle.return_value = mock_categorias
            
            # Act
            response = self.client.get('/api/productos/categorias/')
            
            # Assert
            assert response.status_code == 200
            data = json.loads(response.data)
            assert len(data) == 2
            assert data[0]['nombre'] == "Medicamentos"
            assert data[1]['nombre'] == "Suplementos"
    
    def test_obtener_categorias_vacio(self):
        """Test obtener categorías cuando no hay categorías"""
        # Arrange
        with patch('aplicacion.consultas.obtener_categorias.ObtenerCategoriasHandler') as mock_handler_class:
            mock_handler = Mock()
            mock_handler_class.return_value = mock_handler
            mock_handler.handle.return_value = []
            
            # Act
            response = self.client.get('/api/productos/categorias/')
            
            # Assert
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data == []
    
    def test_obtener_categoria_por_id_exitoso(self):
        """Test obtener categoría por ID via API"""
        # Arrange
        categoria_id = "123e4567-e89b-12d3-a456-426614174000"
        
        with patch('aplicacion.consultas.obtener_categoria_por_id.ObtenerCategoriaPorIdHandler') as mock_handler_class:
            mock_handler = Mock()
            mock_handler_class.return_value = mock_handler
            
            # Mock del resultado
            mock_categoria = CategoriaDTO(
                id=categoria_id,
                nombre="Medicamentos",
                descripcion="Medicamentos generales"
            )
            mock_handler.handle.return_value = mock_categoria
            
            # Act
            response = self.client.get(f'/api/productos/categorias/{categoria_id}')
            
            # Assert
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['id'] == categoria_id
            assert data['nombre'] == "Medicamentos"
    
    def test_obtener_categoria_por_id_no_encontrado(self):
        """Test obtener categoría por ID cuando no existe"""
        # Arrange
        categoria_id = "123e4567-e89b-12d3-a456-426614174000"
        
        with patch('aplicacion.consultas.obtener_categoria_por_id.ObtenerCategoriaPorIdHandler') as mock_handler_class:
            mock_handler = Mock()
            mock_handler_class.return_value = mock_handler
            mock_handler.handle.return_value = None
            
            # Act
            response = self.client.get(f'/api/productos/categorias/{categoria_id}')
            
            # Assert
            assert response.status_code == 404
            data = json.loads(response.data)
            assert 'error' in data
