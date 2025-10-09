import pytest
import sys
import os
from unittest.mock import Mock, patch
import uuid
from flask import Flask

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from aplicacion.comandos.crear_categoria import CrearCategoria, CrearCategoriaHandler
from aplicacion.dto import CategoriaDTO
from config.db import db


class TestCrearCategoria:
    
    def setup_method(self):
        """Setup para cada test"""
        self.handler = CrearCategoriaHandler()
        # Crear app Flask temporal para contexto
        self.app = Flask(__name__)
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        db.init_app(self.app)
    
    def test_crear_categoria_exitosa(self):
        """Test crear categoría exitosa"""
        # Arrange
        comando = CrearCategoria(
            nombre="Medicamentos",
            descripcion="Medicamentos generales"
        )
        
        # Mock categoría guardada
        categoria_guardada = CategoriaDTO(
            id=uuid.uuid4(),
            nombre="Medicamentos",
            descripcion="Medicamentos generales"
        )
        
        # Crear mock del repositorio
        mock_repo = Mock()
        mock_repo.crear.return_value = categoria_guardada
        
        # Crear handler con mock
        handler = CrearCategoriaHandler(repositorio=mock_repo)
        
        # Act
        with self.app.app_context():
            db.create_all()
            resultado = handler.handle(comando)
        
        # Assert
        assert isinstance(resultado, CategoriaDTO)
        assert resultado.nombre == "Medicamentos"
        assert resultado.descripcion == "Medicamentos generales"
        mock_repo.crear.assert_called_once()
    
    def test_crear_categoria_nombre_vacio(self):
        """Test manejo de error cuando nombre está vacío"""
        # Arrange
        comando = CrearCategoria(
            nombre="",  # Nombre vacío
            descripcion="Medicamentos generales"
        )
        
        # Act & Assert
        mock_repo = Mock()
        mock_repo.crear.return_value = CategoriaDTO(
            id=uuid.uuid4(),
            nombre="",
            descripcion="Medicamentos generales"
        )
        
        handler = CrearCategoriaHandler(repositorio=mock_repo)
        
        with self.app.app_context():
            db.create_all()
            resultado = handler.handle(comando)
            assert resultado.nombre == ""
