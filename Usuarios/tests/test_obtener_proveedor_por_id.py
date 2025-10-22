import pytest
import sys
import os
from unittest.mock import Mock, patch
import uuid
from flask import Flask

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from aplicacion.consultas.obtener_proveedor_por_id import ObtenerProveedorPorId, ObtenerProveedorPorIdHandler
from aplicacion.dto import ProveedorDTO
from config.db import db


class TestObtenerProveedorPorId:
    
    def setup_method(self):
        """Setup para cada test"""
        self.handler = ObtenerProveedorPorIdHandler()
        self.proveedor_id = str(uuid.uuid4())

        self.app = Flask(__name__)
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        db.init_app(self.app)
    
    def test_obtener_proveedor_por_id_exitoso(self):
        """Test obtener proveedor por ID exitoso"""
        # Arrange
        consulta = ObtenerProveedorPorId(proveedor_id=self.proveedor_id)
        
        # Mock proveedor
        proveedor = ProveedorDTO(
            id=uuid.UUID(self.proveedor_id),
            nombre="Farmacia Central",
            email="contacto@farmacia.com",
            direccion="Calle 123 #45-67",
            identificacion="9001234567",
            telefono="3001234567"
        )
        
        # Crear mock del repositorio
        mock_repo = Mock()
        mock_repo.obtener_por_id.return_value = proveedor
        
        # Crear handler con mock
        handler = ObtenerProveedorPorIdHandler(repositorio=mock_repo)
        
        # Act
        with self.app.app_context():
            db.create_all()
            resultado = handler.handle(consulta)
        
        # Assert
        assert isinstance(resultado, ProveedorDTO)
        assert resultado.nombre == "Farmacia Central"
        assert resultado.email == "contacto@farmacia.com"
        mock_repo.obtener_por_id.assert_called_once_with(self.proveedor_id)
    
    def test_obtener_proveedor_por_id_no_encontrado(self):
        """Test obtener proveedor por ID que no existe"""
        # Arrange
        consulta = ObtenerProveedorPorId(proveedor_id=self.proveedor_id)
        
        # Crear mock del repositorio
        mock_repo = Mock()
        mock_repo.obtener_por_id.return_value = None
        
        # Crear handler con mock
        handler = ObtenerProveedorPorIdHandler(repositorio=mock_repo)
        
        # Act
        with self.app.app_context():
            db.create_all()
            resultado = handler.handle(consulta)
        
        # Assert
        assert resultado is None
        mock_repo.obtener_por_id.assert_called_once_with(self.proveedor_id)