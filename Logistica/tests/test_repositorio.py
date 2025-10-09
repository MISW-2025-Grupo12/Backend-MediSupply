import pytest
import sys
import os
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from infraestructura.repositorios import RepositorioEntregaSQLite
from aplicacion.dto import EntregaDTO

class TestRepositorioEntregaSQLite:
    def setup_method(self):
        self.repositorio = RepositorioEntregaSQLite()

    @patch('infraestructura.repositorios.db')
    def test_crear_entrega(self, mock_db):
        entrega_dto = EntregaDTO(
            direccion="Calle 123 #45-67",
            fecha_entrega=datetime.now() + timedelta(days=1),
            producto_id="producto-123",
            cliente_id="cliente-456"
        )
        
        mock_entrega_model = Mock()
        mock_db.session.add.return_value = None
        mock_db.session.commit.return_value = None
        
        with patch('infraestructura.repositorios.EntregaModel') as mock_model_class:
            mock_model_class.return_value = mock_entrega_model
            
            resultado = self.repositorio.crear(entrega_dto)
            
            assert resultado == entrega_dto
            mock_db.session.add.assert_called_once()
            mock_db.session.commit.assert_called_once()

    @patch('infraestructura.repositorios.EntregaModel')
    def test_obtener_todos(self, mock_model_class):
        import uuid
        
        mock_entrega1 = Mock()
        mock_entrega1.id = str(uuid.uuid4())
        mock_entrega1.direccion = "Calle 123"
        mock_entrega1.fecha_entrega = datetime.now()
        mock_entrega1.producto_id = "producto-1"
        mock_entrega1.cliente_id = "cliente-1"
        
        mock_entrega2 = Mock()
        mock_entrega2.id = str(uuid.uuid4())
        mock_entrega2.direccion = "Calle 456"
        mock_entrega2.fecha_entrega = datetime.now()
        mock_entrega2.producto_id = "producto-2"
        mock_entrega2.cliente_id = "cliente-2"
        
        mock_model_class.query.all.return_value = [mock_entrega1, mock_entrega2]
        
        resultado = self.repositorio.obtener_todos()
        
        assert len(resultado) == 2
        assert resultado[0].direccion == "Calle 123"
        assert resultado[1].direccion == "Calle 456"
