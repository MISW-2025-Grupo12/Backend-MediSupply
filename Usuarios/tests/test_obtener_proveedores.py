import pytest
import sys
import os
from unittest.mock import Mock, patch
import uuid
from flask import Flask

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from aplicacion.consultas.obtener_proveedores import ObtenerProveedores, ObtenerProveedoresHandler
from aplicacion.dto import ProveedorDTO
from config.db import db


class TestObtenerProveedores:
    
    def setup_method(self):
        """Setup para cada test"""
        self.handler = ObtenerProveedoresHandler()

        self.app = Flask(__name__)
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        db.init_app(self.app)
    
    def test_obtener_proveedores_exitoso(self):
        """Test obtener proveedores exitoso"""
        # Arrange
        consulta = ObtenerProveedores()
        
        # Mock proveedores
        proveedores = [
            ProveedorDTO(
                id=uuid.uuid4(),
                nombre="Farmacia Central",
                email="contacto@farmacia.com",
                direccion="Calle 123 #45-67"
            ),
            ProveedorDTO(
                id=uuid.uuid4(),
                nombre="Droguería Norte",
                email="info@drogueria.com",
                direccion="Avenida 456 #78-90"
            )
        ]
        
        # Crear mock del repositorio
        mock_repo = Mock()
        mock_repo.obtener_todos.return_value = proveedores
        
        # Crear handler con mock
        handler = ObtenerProveedoresHandler(repositorio=mock_repo)
        
        # Act
        with self.app.app_context():
            db.create_all()
            resultado = handler.handle(consulta)
        
        # Assert
        assert isinstance(resultado, list)
        assert len(resultado) == 2
        assert isinstance(resultado[0], ProveedorDTO)
        assert resultado[0].nombre == "Farmacia Central"
        assert resultado[1].nombre == "Droguería Norte"
        mock_repo.obtener_todos.assert_called_once()
    
    def test_obtener_proveedores_vacio(self):
        """Test obtener proveedores cuando no hay proveedores"""
        # Arrange
        consulta = ObtenerProveedores()
        
        # Crear mock del repositorio
        mock_repo = Mock()
        mock_repo.obtener_todos.return_value = []
        
        # Crear handler con mock
        handler = ObtenerProveedoresHandler(repositorio=mock_repo)
        
        # Act
        with self.app.app_context():
            db.create_all()
            resultado = handler.handle(consulta)
        
        # Assert
        assert isinstance(resultado, list)
        assert len(resultado) == 0