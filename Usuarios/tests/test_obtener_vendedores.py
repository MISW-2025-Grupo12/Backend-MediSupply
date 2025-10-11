import pytest
import sys
import os
from unittest.mock import Mock, patch
from flask import Flask
import uuid

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from aplicacion.consultas.obtener_vendedores import ObtenerVendedoresHandler, ObtenerVendedores
from aplicacion.dto import VendedorDTO


class TestObtenerVendedores:
    """Test para obtener vendedores"""
    
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
    
    def test_obtener_vendedores_exitoso(self):
        """Test obtener vendedores exitoso"""
        # Arrange
        mock_vendedores = [
            VendedorDTO(
                id=uuid.uuid4(),
                nombre="María García",
                email="maria@email.com",
                telefono="0987654321",
                direccion="Avenida 456 #78-90"
            ),
            VendedorDTO(
                id=uuid.uuid4(),
                nombre="Carlos Ruiz",
                email="carlos@email.com",
                telefono="1122334455",
                direccion="Carrera 789 #12-34"
            )
        ]
        
        with patch('aplicacion.consultas.obtener_vendedores.RepositorioVendedorSQLite') as mock_repo_class:
            mock_repo = Mock()
            mock_repo_class.return_value = mock_repo
            mock_repo.obtener_todos.return_value = mock_vendedores
            
            handler = ObtenerVendedoresHandler()
            consulta = ObtenerVendedores()
            
            # Act
            resultado = handler.handle(consulta)
            
            # Assert
            assert resultado is not None
            assert len(resultado) == 2
            assert resultado[0].nombre == "María García"
            assert resultado[1].nombre == "Carlos Ruiz"
            mock_repo.obtener_todos.assert_called_once()
    
    def test_obtener_vendedores_vacio(self):
        """Test obtener vendedores cuando no hay vendedores"""
        # Arrange
        with patch('aplicacion.consultas.obtener_vendedores.RepositorioVendedorSQLite') as mock_repo_class:
            mock_repo = Mock()
            mock_repo_class.return_value = mock_repo
            mock_repo.obtener_todos.return_value = []
            
            handler = ObtenerVendedoresHandler()
            consulta = ObtenerVendedores()
            
            # Act
            resultado = handler.handle(consulta)
            
            # Assert
            assert resultado is not None
            assert len(resultado) == 0
            mock_repo.obtener_todos.assert_called_once()
    
    def test_obtener_vendedores_error(self):
        """Test obtener vendedores con error"""
        # Arrange
        with patch('aplicacion.consultas.obtener_vendedores.RepositorioVendedorSQLite') as mock_repo_class:
            mock_repo = Mock()
            mock_repo_class.return_value = mock_repo
            mock_repo.obtener_todos.side_effect = Exception("Error de base de datos")
            
            handler = ObtenerVendedoresHandler()
            
            # Act & Assert
            consulta = ObtenerVendedores()
            with pytest.raises(Exception, match="Error de base de datos"):
                handler.handle(consulta)
    
    def test_obtener_vendedores_con_repositorio_personalizado(self):
        """Test obtener vendedores con repositorio personalizado"""
        # Arrange
        mock_repo = Mock()
        mock_repo.obtener_todos.return_value = []
        
        handler = ObtenerVendedoresHandler(repositorio=mock_repo)
        consulta = ObtenerVendedores()
        
        # Act
        resultado = handler.handle(consulta)
        
        # Assert
        assert resultado is not None
        assert len(resultado) == 0
        mock_repo.obtener_todos.assert_called_once()
