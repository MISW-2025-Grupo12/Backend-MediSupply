import pytest
import sys
import os
from unittest.mock import Mock, patch
from flask import Flask
import uuid

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from aplicacion.comandos.crear_vendedor import CrearVendedor, CrearVendedorHandler
from aplicacion.dto import VendedorDTO


class TestCrearVendedor:
    """Test para crear vendedor"""
    
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
    
    def test_crear_vendedor_exitoso(self):
        """Test crear vendedor exitoso"""
        # Arrange
        comando = CrearVendedor(
            nombre="María García",
            email="maria@email.com",
            identificacion="1234567890",
            telefono="0987654321",
            direccion="Avenida 456 #78-90"
        )
        
        with patch('aplicacion.comandos.crear_vendedor.RepositorioVendedorSQLite') as mock_repo_class:
            mock_repo = Mock()
            mock_repo_class.return_value = mock_repo
            mock_vendedor = VendedorDTO(
                id=uuid.uuid4(),
                nombre="María García",
                email="maria@email.com",
                identificacion="1234567890",
                telefono="0987654321",
                direccion="Avenida 456 #78-90"
            )
            mock_repo.crear.return_value = mock_vendedor
            
            handler = CrearVendedorHandler()
            
            # Act
            resultado = handler.handle(comando)
            
            # Assert
            assert resultado is not None
            assert resultado.nombre == "María García"
            assert resultado.email == "maria@email.com"
            assert resultado.identificacion == "1234567890"
            assert resultado.telefono == "0987654321"
            assert resultado.direccion == "Avenida 456 #78-90"
            mock_repo.crear.assert_called_once()
    
    def test_crear_vendedor_nombre_vacio(self):
        """Test crear vendedor con nombre vacío lanza excepción"""
        # Arrange
        from dominio.excepciones import NombreInvalidoError
        comando = CrearVendedor(
            nombre="",
            email="maria@email.com",
            identificacion="1234567890",
            telefono="0987654321",
            direccion="Avenida 456 #78-90"
        )
        
        handler = CrearVendedorHandler()
        
        # Act & Assert
        with pytest.raises(NombreInvalidoError):
            handler.handle(comando)
    
    def test_crear_vendedor_email_invalido(self):
        """Test crear vendedor con email inválido lanza excepción"""
        # Arrange
        from dominio.excepciones import EmailInvalidoError
        comando = CrearVendedor(
            nombre="María García",
            email="email_invalido",
            identificacion="1234567890",
            telefono="0987654321",
            direccion="Avenida 456 #78-90"
        )
        
        handler = CrearVendedorHandler()
        
        # Act & Assert
        with pytest.raises(EmailInvalidoError):
            handler.handle(comando)
    
    def test_crear_vendedor_error_repositorio(self):
        """Test crear vendedor con error en repositorio"""
        # Arrange
        comando = CrearVendedor(
            nombre="María García",
            email="maria@email.com",
            identificacion="1234567890",
            telefono="0987654321",
            direccion="Avenida 456 #78-90"
        )
        
        with patch('aplicacion.comandos.crear_vendedor.RepositorioVendedorSQLite') as mock_repo_class:
            mock_repo = Mock()
            mock_repo_class.return_value = mock_repo
            mock_repo.crear.side_effect = Exception("Error de base de datos")
            
            handler = CrearVendedorHandler()
            
            # Act & Assert
            with pytest.raises(Exception, match="Error de base de datos"):
                handler.handle(comando)
    
    def test_crear_vendedor_con_repositorio_personalizado(self):
        """Test crear vendedor con repositorio personalizado"""
        # Arrange
        comando = CrearVendedor(
            nombre="María García",
            email="maria@email.com",
            identificacion="1234567890",
            telefono="0987654321",
            direccion="Avenida 456 #78-90"
        )
        
        mock_repo = Mock()
        mock_vendedor = VendedorDTO(
            id=uuid.uuid4(),
            nombre="María García",
            email="maria@email.com",
            identificacion="1234567890",
            telefono="0987654321",
            direccion="Avenida 456 #78-90"
        )
        mock_repo.crear.return_value = mock_vendedor
        
        handler = CrearVendedorHandler(repositorio=mock_repo)
        
        # Act
        resultado = handler.handle(comando)
        
        # Assert
        assert resultado is not None
        assert resultado.nombre == "María García"
        mock_repo.crear.assert_called_once()
