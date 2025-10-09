import pytest
import sys
import os
from unittest.mock import Mock, patch
import uuid
from flask import Flask

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from aplicacion.consultas.obtener_categorias import ObtenerCategorias, ObtenerCategoriasHandler
from aplicacion.dto import CategoriaDTO
from config.db import db


class TestObtenerCategorias:
    
    def setup_method(self):
        """Setup para cada test"""
        self.handler = ObtenerCategoriasHandler()

        self.app = Flask(__name__)
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        db.init_app(self.app)
    
    def test_obtener_categorias_exitoso(self):
        """Test obtener categorías exitoso"""
        # Arrange
        consulta = ObtenerCategorias()
        
        # Mock categorías
        categorias = [
            CategoriaDTO(
                id=uuid.uuid4(),
                nombre="Medicamentos",
                descripcion="Medicamentos generales"
            ),
            CategoriaDTO(
                id=uuid.uuid4(),
                nombre="Suplementos",
                descripcion="Suplementos vitamínicos"
            )
        ]
        
        # Crear mock del repositorio
        mock_repo = Mock()
        mock_repo.obtener_todos.return_value = categorias
        
        # Crear handler con mock
        handler = ObtenerCategoriasHandler(repositorio=mock_repo)
        
        # Act
        with self.app.app_context():
            db.create_all()
            resultado = handler.handle(consulta)
        
        # Assert
        assert isinstance(resultado, list)
        assert len(resultado) == 2
        assert isinstance(resultado[0], CategoriaDTO)
        assert resultado[0].nombre == "Medicamentos"
        assert resultado[1].nombre == "Suplementos"
        mock_repo.obtener_todos.assert_called_once()
    
    def test_obtener_categorias_vacio(self):
        """Test obtener categorías cuando no hay categorías"""
        # Arrange
        consulta = ObtenerCategorias()
        
        # Crear mock del repositorio
        mock_repo = Mock()
        mock_repo.obtener_todos.return_value = []
        
        # Crear handler con mock
        handler = ObtenerCategoriasHandler(repositorio=mock_repo)
        
        # Act
        with self.app.app_context():
            db.create_all()
            resultado = handler.handle(consulta)
        
        # Assert
        assert isinstance(resultado, list)
        assert len(resultado) == 0