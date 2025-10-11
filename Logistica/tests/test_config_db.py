import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from config.db import init_db

class TestConfigDB:
    def test_init_db_con_app_valida(self):
        mock_app = Mock()
        mock_app.config = {
            'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
            'SQLALCHEMY_TRACK_MODIFICATIONS': False
        }
        
        with patch('config.db.db') as mock_db:
            mock_db.init_app = Mock()
            mock_db.create_all = Mock()
            
            init_db(mock_app)
            
            mock_db.init_app.assert_called_once_with(mock_app)
            mock_db.create_all.assert_called_once()

    def test_init_db_con_app_none(self):
        with patch('config.db.db') as mock_db:
            mock_db.init_app = Mock()
            mock_db.create_all = Mock()
            
            # No debería lanzar excepción
            init_db(None)
            
            mock_db.init_app.assert_called_once_with(None)
            mock_db.create_all.assert_called_once()

    def test_init_db_con_error_en_init_app(self):
        mock_app = Mock()
        mock_app.config = {}
        
        with patch('config.db.db') as mock_db:
            mock_db.init_app.side_effect = Exception("Error en init_app")
            mock_db.create_all = Mock()
            
            # No debería lanzar excepción
            init_db(mock_app)
            
            mock_db.init_app.assert_called_once_with(mock_app)
            mock_db.create_all.assert_called_once()

    def test_init_db_con_error_en_create_all(self):
        mock_app = Mock()
        mock_app.config = {}
        
        with patch('config.db.db') as mock_db:
            mock_db.init_app = Mock()
            mock_db.create_all.side_effect = Exception("Error en create_all")
            
            # No debería lanzar excepción
            init_db(mock_app)
            
            mock_db.init_app.assert_called_once_with(mock_app)
            mock_db.create_all.assert_called_once()

    def test_init_db_con_configuracion_completa(self):
        mock_app = Mock()
        mock_app.config = {
            'SQLALCHEMY_DATABASE_URI': 'postgresql://user:pass@localhost/db',
            'SQLALCHEMY_TRACK_MODIFICATIONS': True,
            'SQLALCHEMY_ECHO': True
        }
        
        with patch('config.db.db') as mock_db:
            mock_db.init_app = Mock()
            mock_db.create_all = Mock()
            
            init_db(mock_app)
            
            mock_db.init_app.assert_called_once_with(mock_app)
            mock_db.create_all.assert_called_once()

    def test_init_db_con_configuracion_minima(self):
        mock_app = Mock()
        mock_app.config = {}
        
        with patch('config.db.db') as mock_db:
            mock_db.init_app = Mock()
            mock_db.create_all = Mock()
            
            init_db(mock_app)
            
            mock_db.init_app.assert_called_once_with(mock_app)
            mock_db.create_all.assert_called_once()

    def test_init_db_con_app_sin_config(self):
        mock_app = Mock()
        mock_app.config = None
        
        with patch('config.db.db') as mock_db:
            mock_db.init_app = Mock()
            mock_db.create_all = Mock()
            
            # No debería lanzar excepción
            init_db(mock_app)
            
            mock_db.init_app.assert_called_once_with(mock_app)
            mock_db.create_all.assert_called_once()

    def test_init_db_multiples_llamadas(self):
        mock_app1 = Mock()
        mock_app1.config = {}
        mock_app2 = Mock()
        mock_app2.config = {}
        
        with patch('config.db.db') as mock_db:
            mock_db.init_app = Mock()
            mock_db.create_all = Mock()
            
            init_db(mock_app1)
            init_db(mock_app2)
            
            assert mock_db.init_app.call_count == 2
            assert mock_db.create_all.call_count == 2
