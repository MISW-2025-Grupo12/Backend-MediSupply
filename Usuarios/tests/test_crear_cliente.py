import pytest
import sys
import os
from unittest.mock import Mock, patch
from flask import Flask
import uuid

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from aplicacion.comandos.crear_cliente import CrearCliente, CrearClienteHandler
from aplicacion.dto import ClienteDTO


class TestCrearCliente:
    """Test para crear cliente"""
    
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
    
    def test_crear_cliente_exitoso(self):
        """Test crear cliente exitoso"""
        # Arrange
        comando = CrearCliente(
            nombre="Juan Pérez",
            email="juan@email.com",
            identificacion="1234567890",
            telefono="1234567890",
            direccion="Calle 123 #45-67"
        )
        
        with patch('aplicacion.comandos.crear_cliente.RepositorioClienteSQLite') as mock_repo_class:
            mock_repo = Mock()
            mock_repo_class.return_value = mock_repo
            mock_cliente = ClienteDTO(
                id=uuid.uuid4(),
                nombre="Juan Pérez",
                email="juan@email.com",
                identificacion="1234567890",
                telefono="1234567890",
                direccion="Calle 123 #45-67"
            )
            mock_repo.crear.return_value = mock_cliente
            
            handler = CrearClienteHandler()
            
            # Act
            resultado = handler.handle(comando)
            
            # Assert
            assert resultado is not None
            assert resultado.nombre == "Juan Pérez"
            assert resultado.email == "juan@email.com"
            assert resultado.identificacion == "1234567890"
            assert resultado.telefono == "1234567890"
            assert resultado.direccion == "Calle 123 #45-67"
            mock_repo.crear.assert_called_once()
    
    def test_crear_cliente_nombre_vacio(self):
        """Test crear cliente con nombre vacío lanza excepción"""
        # Arrange
        from dominio.excepciones import NombreInvalidoError
        comando = CrearCliente(
            nombre="",
            email="juan@email.com",
            identificacion="1234567890",
            telefono="1234567890",
            direccion="Calle 123 #45-67"
        )
        
        handler = CrearClienteHandler()
        
        # Act & Assert
        with pytest.raises(NombreInvalidoError):
            handler.handle(comando)
    
    def test_crear_cliente_email_invalido(self):
        """Test crear cliente con email inválido lanza excepción"""
        # Arrange
        from dominio.excepciones import EmailInvalidoError
        comando = CrearCliente(
            nombre="Juan Pérez",
            email="email_invalido",
            identificacion="1234567890",
            telefono="1234567890",
            direccion="Calle 123 #45-67"
        )
        
        handler = CrearClienteHandler()
        
        # Act & Assert
        with pytest.raises(EmailInvalidoError):
            handler.handle(comando)
    
    def test_crear_cliente_error_repositorio(self):
        """Test crear cliente con error en repositorio"""
        # Arrange
        comando = CrearCliente(
            nombre="Juan Pérez",
            email="juan@email.com",
            identificacion="1234567890",
            telefono="1234567890",
            direccion="Calle 123 #45-67"
        )
        
        with patch('aplicacion.comandos.crear_cliente.RepositorioClienteSQLite') as mock_repo_class:
            mock_repo = Mock()
            mock_repo_class.return_value = mock_repo
            mock_repo.crear.side_effect = Exception("Error de base de datos")
            
            handler = CrearClienteHandler()
            
            # Act & Assert
            with pytest.raises(Exception, match="Error de base de datos"):
                handler.handle(comando)
    
    def test_crear_cliente_con_repositorio_personalizado(self):
        """Test crear cliente con repositorio personalizado"""
        # Arrange
        comando = CrearCliente(
            nombre="Juan Pérez",
            email="juan@email.com",
            identificacion="1234567890",
            telefono="1234567890",
            direccion="Calle 123 #45-67"
        )
        
        mock_repo = Mock()
        mock_cliente = ClienteDTO(
            id=uuid.uuid4(),
            nombre="Juan Pérez",
            email="juan@email.com",
            identificacion="1234567890",
            telefono="1234567890",
            direccion="Calle 123 #45-67"
        )
        mock_repo.crear.return_value = mock_cliente
        
        handler = CrearClienteHandler(repositorio=mock_repo)
        
        # Act
        resultado = handler.handle(comando)
        
        # Assert
        assert resultado is not None
        assert resultado.nombre == "Juan Pérez"
        mock_repo.crear.assert_called_once()
