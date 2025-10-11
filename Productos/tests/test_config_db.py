import pytest
import sys
import os
from unittest.mock import Mock, patch
from flask import Flask

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from config.db import db, init_db


class TestConfigDB:
    """Test para configuración de base de datos"""
    
    def setup_method(self):
        self.app = Flask(__name__)
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        self.app.config['TESTING'] = True
    
    def teardown_method(self):
        if hasattr(self, 'app') and self.app:
            with self.app.app_context():
                db.drop_all()
    
    def test_init_db_exitoso(self):
        """Test inicialización de base de datos exitosa"""
        # Arrange
        db.init_app(self.app)
        
        # Act
        with self.app.app_context():
            init_db(self.app)
        
        # Assert
        # Si no hay excepción, la inicialización fue exitosa
        assert True
    
    def test_init_db_con_error(self):
        """Test inicialización de base de datos con error"""
        # Arrange
        db.init_app(self.app)
        
        with patch.object(db, 'create_all') as mock_create_all:
            mock_create_all.side_effect = Exception("Error de base de datos")
            
            # Act & Assert
            with self.app.app_context():
                with pytest.raises(Exception, match="Error de base de datos"):
                    init_db(self.app)
    
    def test_db_configuracion_correcta(self):
        """Test que la configuración de la base de datos es correcta"""
        # Arrange & Act
        db.init_app(self.app)
        
        with self.app.app_context():
            # Assert
            assert db.app == self.app
            assert db.engine.url.database == ':memory:'
    
    def test_db_sesion_funciona(self):
        """Test que la sesión de base de datos funciona correctamente"""
        # Arrange
        db.init_app(self.app)
        
        with self.app.app_context():
            init_db(self.app)
            
            # Act
            session = db.session
            
            # Assert
            assert session is not None
            assert hasattr(session, 'add')
            assert hasattr(session, 'commit')
            assert hasattr(session, 'rollback')
    
    def test_db_metadata_tiene_tablas(self):
        """Test que el metadata de la base de datos tiene las tablas correctas"""
        # Arrange
        db.init_app(self.app)
        
        with self.app.app_context():
            init_db(self.app)
            
            # Act
            tables = db.metadata.tables.keys()
            
            # Assert
            assert 'productos' in tables
            assert 'categorias' in tables
