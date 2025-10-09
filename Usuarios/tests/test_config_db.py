import pytest
import sys
import os
from unittest.mock import patch, Mock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from config.db import db, init_db


class TestConfigDB:
    
    def test_init_db_sqlite(self):
        """Test inicializar base de datos SQLite"""
        # Arrange
        mock_app = Mock()
        mock_app.config = {}
        mock_app.extensions = {}
        mock_app.instance_path = "/tmp"
        mock_app.app_context.return_value.__enter__ = Mock()
        mock_app.app_context.return_value.__exit__ = Mock()
        
        # Act
        result = init_db(mock_app)
        
        # Assert
        assert result is None  # init_db no retorna nada
        assert mock_app.config['SQLALCHEMY_DATABASE_URI'] == 'sqlite:///usuarios.db'
    
    @patch('config.db.SQLAlchemy')
    def test_db_creation(self, mock_sqlalchemy):
        """Test creación de instancia de SQLAlchemy"""
        # Arrange
        mock_db = Mock()
        mock_sqlalchemy.return_value = mock_db
        
        # Act
        from config.db import db
        
        # Assert
        assert db is not None
