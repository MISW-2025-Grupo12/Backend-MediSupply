import pytest
import sys
import os
from unittest.mock import Mock, patch
import uuid
from flask import Flask

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from aplicacion.comandos.crear_proveedor import CrearProveedor, CrearProveedorHandler
from aplicacion.dto import ProveedorDTO
from config.db import db


class TestCrearProveedor:
    
    def setup_method(self):
        """Setup para cada test"""
        self.handler = CrearProveedorHandler()

        self.app = Flask(__name__)
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        db.init_app(self.app)
    
    def test_crear_proveedor_exitoso(self):
        """Test crear proveedor exitoso"""
        # Arrange
        comando = CrearProveedor(
            nombre="Farmacia Central",
            email="contacto@farmacia.com",
            identificacion="9005678901",
            telefono="6017654321",
            direccion="Calle 123 #45-67"
        )
        
        # Mock proveedor guardado
        proveedor_guardado = ProveedorDTO(
            id=uuid.uuid4(),
            nombre="Farmacia Central",
            email="contacto@farmacia.com",
            identificacion="9005678901",
            telefono="6017654321",
            direccion="Calle 123 #45-67"
        )
        
        # Crear mock del repositorio
        mock_repo = Mock()
        mock_repo.crear.return_value = proveedor_guardado
        
        # Crear handler con mock
        handler = CrearProveedorHandler(repositorio=mock_repo)
        
        # Act
        with self.app.app_context():
            db.create_all()
            resultado = handler.handle(comando)
        
        # Assert
        assert isinstance(resultado, ProveedorDTO)
        assert resultado.nombre == "Farmacia Central"
        assert resultado.email == "contacto@farmacia.com"
        assert resultado.identificacion == "9005678901"
        assert resultado.telefono == "6017654321"
        assert resultado.direccion == "Calle 123 #45-67"
        mock_repo.crear.assert_called_once()
    
    def test_crear_proveedor_nombre_vacio(self):
        """Test validación de nombre vacío lanza excepción"""
        # Arrange
        from dominio.excepciones import NombreInvalidoError
        comando = CrearProveedor(
            nombre="",  # Nombre vacío
            email="contacto@farmacia.com",
            identificacion="9005678901",
            telefono="6017654321",
            direccion="Calle 123 #45-67"
        )
        
        # Act & Assert
        with pytest.raises(NombreInvalidoError):
            self.handler.handle(comando)
    
    def test_crear_proveedor_email_vacio(self):
        """Test validación de email vacío lanza excepción"""
        # Arrange
        from dominio.excepciones import EmailInvalidoError
        comando = CrearProveedor(
            nombre="Farmacia Central",
            email="",  # Email vacío
            identificacion="9005678901",
            telefono="6017654321",
            direccion="Calle 123 #45-67"
        )
        
        # Act & Assert
        with pytest.raises(EmailInvalidoError):
            self.handler.handle(comando)
    
    def test_crear_proveedor_direccion_vacia(self):
        """Test validación de dirección vacía lanza excepción"""
        # Arrange
        from seedwork.dominio.excepciones import ReglaNegocioExcepcion
        comando = CrearProveedor(
            nombre="Farmacia Central",
            email="contacto@farmacia.com",
            identificacion="9005678901",
            telefono="6017654321",
            direccion=""  # Dirección vacía
        )
        
        # Act & Assert
        with pytest.raises(ReglaNegocioExcepcion):
            self.handler.handle(comando)
