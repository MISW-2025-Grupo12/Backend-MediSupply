import pytest
import sys
import os
from unittest.mock import Mock, patch
from flask import Flask

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from aplicacion.consultas.obtener_categoria_por_id import ObtenerCategoriaPorIdHandler, ObtenerCategoriaPorId
from aplicacion.dto import CategoriaDTO


class TestObtenerCategoriaPorId:
    """Test para obtener categoría por ID"""
    
    def setup_method(self):
        self.app = Flask(__name__)
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        self.app.config['TESTING'] = True
        from config.db import db
        self.db = db
        self.db.init_app(self.app)
        with self.app.app_context():
            self.db.create_all()
        self.client = self.app.test_client()
    
    def teardown_method(self):
        if self.app and self.db:
            with self.app.app_context():
                self.db.session.rollback()
                self.db.drop_all()
    
    def test_obtener_categoria_por_id_exitoso(self):
        """Test obtener categoría por ID exitoso"""
        # Arrange
        categoria_id = "123e4567-e89b-12d3-a456-426614174000"
        mock_categoria = CategoriaDTO(
            id=categoria_id,
            nombre="Medicamentos",
            descripcion="Medicamentos generales"
        )
        
        with patch('aplicacion.consultas.obtener_categoria_por_id.RepositorioCategoriaSQLite') as mock_repo_class:
            mock_repo = Mock()
            mock_repo_class.return_value = mock_repo
            mock_repo.obtener_por_id.return_value = mock_categoria
            
            handler = ObtenerCategoriaPorIdHandler()
            
            # Act
            consulta = ObtenerCategoriaPorId(categoria_id=categoria_id)
            resultado = handler.handle(consulta)
            
            # Assert
            assert resultado is not None
            assert resultado.id == categoria_id
            assert resultado.nombre == "Medicamentos"
            assert resultado.descripcion == "Medicamentos generales"
            mock_repo.obtener_por_id.assert_called_once_with(categoria_id)
    
    def test_obtener_categoria_por_id_no_existe(self):
        """Test obtener categoría por ID que no existe"""
        # Arrange
        categoria_id = "123e4567-e89b-12d3-a456-426614174000"
        
        with patch('aplicacion.consultas.obtener_categoria_por_id.RepositorioCategoriaSQLite') as mock_repo_class:
            mock_repo = Mock()
            mock_repo_class.return_value = mock_repo
            mock_repo.obtener_por_id.return_value = None
            
            handler = ObtenerCategoriaPorIdHandler()
            
            # Act
            consulta = ObtenerCategoriaPorId(categoria_id=categoria_id)
            resultado = handler.handle(consulta)
            
            # Assert
            assert resultado is None
            mock_repo.obtener_por_id.assert_called_once_with(categoria_id)
    
    def test_obtener_categoria_por_id_error(self):
        """Test obtener categoría por ID con error"""
        # Arrange
        categoria_id = "123e4567-e89b-12d3-a456-426614174000"
        
        with patch('aplicacion.consultas.obtener_categoria_por_id.RepositorioCategoriaSQLite') as mock_repo_class:
            mock_repo = Mock()
            mock_repo_class.return_value = mock_repo
            mock_repo.obtener_por_id.side_effect = Exception("Error de base de datos")
            
            handler = ObtenerCategoriaPorIdHandler()
            
            # Act & Assert
            consulta = ObtenerCategoriaPorId(categoria_id=categoria_id)
            with pytest.raises(Exception, match="Error de base de datos"):
                handler.handle(consulta)
