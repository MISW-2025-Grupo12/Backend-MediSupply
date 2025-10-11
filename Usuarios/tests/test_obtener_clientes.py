import pytest
import sys
import os
from unittest.mock import Mock, patch
from flask import Flask
import uuid

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from aplicacion.consultas.obtener_clientes import ObtenerClientesHandler, ObtenerClientes
from aplicacion.dto import ClienteDTO


class TestObtenerClientes:
    """Test para obtener clientes"""
    
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
    
    def test_obtener_clientes_exitoso(self):
        """Test obtener clientes exitoso"""
        # Arrange
        mock_clientes = [
            ClienteDTO(
                id=uuid.uuid4(),
                nombre="Juan Pérez",
                email="juan@email.com",
                telefono="1234567890",
                direccion="Calle 123 #45-67"
            ),
            ClienteDTO(
                id=uuid.uuid4(),
                nombre="Ana López",
                email="ana@email.com",
                telefono="0987654321",
                direccion="Avenida 456 #78-90"
            )
        ]
        
        with patch('aplicacion.consultas.obtener_clientes.RepositorioClienteSQLite') as mock_repo_class:
            mock_repo = Mock()
            mock_repo_class.return_value = mock_repo
            mock_repo.obtener_todos.return_value = mock_clientes
            
            handler = ObtenerClientesHandler()
            consulta = ObtenerClientes()
            
            # Act
            resultado = handler.handle(consulta)
            
            # Assert
            assert resultado is not None
            assert len(resultado) == 2
            assert resultado[0].nombre == "Juan Pérez"
            assert resultado[1].nombre == "Ana López"
            mock_repo.obtener_todos.assert_called_once()
    
    def test_obtener_clientes_vacio(self):
        """Test obtener clientes cuando no hay clientes"""
        # Arrange
        with patch('aplicacion.consultas.obtener_clientes.RepositorioClienteSQLite') as mock_repo_class:
            mock_repo = Mock()
            mock_repo_class.return_value = mock_repo
            mock_repo.obtener_todos.return_value = []
            
            handler = ObtenerClientesHandler()
            consulta = ObtenerClientes()
            
            # Act
            resultado = handler.handle(consulta)
            
            # Assert
            assert resultado is not None
            assert len(resultado) == 0
            mock_repo.obtener_todos.assert_called_once()
    
    def test_obtener_clientes_error(self):
        """Test obtener clientes con error"""
        # Arrange
        with patch('aplicacion.consultas.obtener_clientes.RepositorioClienteSQLite') as mock_repo_class:
            mock_repo = Mock()
            mock_repo_class.return_value = mock_repo
            mock_repo.obtener_todos.side_effect = Exception("Error de base de datos")
            
            handler = ObtenerClientesHandler()
            
            # Act & Assert
            with pytest.raises(Exception, match="Error de base de datos"):
                handler.handle(consulta)
    
    def test_obtener_clientes_con_repositorio_personalizado(self):
        """Test obtener clientes con repositorio personalizado"""
        # Arrange
        mock_repo = Mock()
        mock_repo.obtener_todos.return_value = []
        
        handler = ObtenerClientesHandler(repositorio=mock_repo)
        consulta = ObtenerClientes()
        
        # Act
        resultado = handler.handle(consulta)
        
        # Assert
        assert resultado is not None
        assert len(resultado) == 0
        mock_repo.obtener_todos.assert_called_once()
