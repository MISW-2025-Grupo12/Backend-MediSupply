import pytest
import sys
import os
from unittest.mock import Mock, patch
from flask import Flask
import uuid

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from aplicacion.consultas.obtener_cliente_por_id import ObtenerClientePorIdHandler, ObtenerClientePorId
from aplicacion.dto import ClienteDTO


class TestObtenerClientePorId:
    """Test para obtener cliente por ID"""
    
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
    
    def test_obtener_cliente_por_id_exitoso(self):
        """Test obtener cliente por ID exitoso"""
        # Arrange
        cliente_id = str(uuid.uuid4())
        mock_cliente = ClienteDTO(
            id=cliente_id,
            nombre="Juan Pérez",
            email="juan@email.com",
            telefono="1234567890",
            direccion="Calle 123 #45-67",
            identificacion="1001234567"
        )
        
        with patch('aplicacion.consultas.obtener_cliente_por_id.RepositorioClienteSQLite') as mock_repo_class:
            mock_repo = Mock()
            mock_repo_class.return_value = mock_repo
            mock_repo.obtener_por_id.return_value = mock_cliente
            
            handler = ObtenerClientePorIdHandler()
            consulta = ObtenerClientePorId(cliente_id=cliente_id)
            
            # Act
            resultado = handler.handle(consulta)
            
            # Assert
            assert resultado is not None
            assert resultado.id == cliente_id
            assert resultado.nombre == "Juan Pérez"
            assert resultado.email == "juan@email.com"
            mock_repo.obtener_por_id.assert_called_once_with(cliente_id)
    
    def test_obtener_cliente_por_id_no_existe(self):
        """Test obtener cliente por ID que no existe"""
        # Arrange
        cliente_id = str(uuid.uuid4())
        
        with patch('aplicacion.consultas.obtener_cliente_por_id.RepositorioClienteSQLite') as mock_repo_class:
            mock_repo = Mock()
            mock_repo_class.return_value = mock_repo
            mock_repo.obtener_por_id.return_value = None
            
            handler = ObtenerClientePorIdHandler()
            consulta = ObtenerClientePorId(cliente_id=cliente_id)
            
            # Act
            resultado = handler.handle(consulta)
            
            # Assert
            assert resultado is None
            mock_repo.obtener_por_id.assert_called_once_with(cliente_id)
    
    def test_obtener_cliente_por_id_error(self):
        """Test obtener cliente por ID con error"""
        # Arrange
        cliente_id = str(uuid.uuid4())
        
        with patch('aplicacion.consultas.obtener_cliente_por_id.RepositorioClienteSQLite') as mock_repo_class:
            mock_repo = Mock()
            mock_repo_class.return_value = mock_repo
            mock_repo.obtener_por_id.side_effect = Exception("Error de base de datos")
            
            handler = ObtenerClientePorIdHandler()
            
            # Act & Assert
            consulta = ObtenerClientePorId(cliente_id=cliente_id)
            with pytest.raises(Exception, match="Error de base de datos"):
                handler.handle(consulta)
    
    def test_obtener_cliente_por_id_con_repositorio_personalizado(self):
        """Test obtener cliente por ID con repositorio personalizado"""
        # Arrange
        cliente_id = str(uuid.uuid4())
        mock_repo = Mock()
        mock_repo.obtener_por_id.return_value = None
        
        handler = ObtenerClientePorIdHandler(repositorio=mock_repo)
        consulta = ObtenerClientePorId(cliente_id=cliente_id)
        
        # Act
        resultado = handler.handle(consulta)
        
        # Assert
        assert resultado is None
        mock_repo.obtener_por_id.assert_called_once_with(cliente_id)
