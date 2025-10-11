import pytest
import sys
import os
from unittest.mock import Mock, patch
from datetime import datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from infraestructura.repositorios import RepositorioInventarioSQLite
from aplicacion.dto import InventarioDTO

class TestRepositorioInventarioSQLite:
    def setup_method(self):
        with patch('infraestructura.repositorios.db') as mock_db:
            self.mock_db = mock_db
            self.repositorio = RepositorioInventarioSQLite()

    def test_crear_repositorio(self):
        assert self.repositorio is not None

    def test_obtener_por_producto_id_exitoso(self):
        mock_inventario = Mock()
        mock_inventario.producto_id = 'prod-123'
        mock_inventario.cantidad_disponible = 100
        mock_inventario.cantidad_reservada = 10
        mock_inventario.fecha_vencimiento = datetime.now() + timedelta(days=30)
        
        self.mock_db.session.query.return_value.filter.return_value.all.return_value = [mock_inventario]
        
        resultado = self.repositorio.obtener_por_producto_id('prod-123')
        
        assert len(resultado) == 1
        assert resultado[0].producto_id == 'prod-123'

    def test_obtener_por_producto_id_no_encontrado(self):
        self.mock_db.session.query.return_value.filter.return_value.all.return_value = []
        
        resultado = self.repositorio.obtener_por_producto_id('prod-999')
        
        assert resultado == []

    def test_obtener_por_producto_id_error(self):
        self.mock_db.session.query.side_effect = Exception("Error de DB")
        
        resultado = self.repositorio.obtener_por_producto_id('prod-123')
        
        assert resultado == []

    def test_crear_o_actualizar_nuevo(self):
        inventario_dto = InventarioDTO(
            producto_id='prod-123',
            cantidad_disponible=100,
            cantidad_reservada=10,
            fecha_vencimiento=datetime.now() + timedelta(days=30)
        )
        
        self.mock_db.session.query.return_value.filter.return_value.first.return_value = None
        
        self.repositorio.crear_o_actualizar(inventario_dto)
        
        self.mock_db.session.add.assert_called_once()
        self.mock_db.session.commit.assert_called_once()

    def test_crear_o_actualizar_existente(self):
        inventario_dto = InventarioDTO(
            producto_id='prod-123',
            cantidad_disponible=100,
            cantidad_reservada=10,
            fecha_vencimiento=datetime.now() + timedelta(days=30)
        )
        
        mock_inventario_existente = Mock()
        mock_inventario_existente.producto_id = 'prod-123'
        self.mock_db.session.query.return_value.filter.return_value.first.return_value = mock_inventario_existente
        
        self.repositorio.crear_o_actualizar(inventario_dto)
        
        self.mock_db.session.add.assert_not_called()
        self.mock_db.session.commit.assert_called_once()

    def test_crear_o_actualizar_error(self):
        inventario_dto = InventarioDTO(
            producto_id='prod-123',
            cantidad_disponible=100,
            cantidad_reservada=10,
            fecha_vencimiento=datetime.now() + timedelta(days=30)
        )
        
        self.mock_db.session.query.side_effect = Exception("Error de DB")
        
        self.repositorio.crear_o_actualizar(inventario_dto)
        
        self.mock_db.session.rollback.assert_called_once()

    def test_obtener_todos(self):
        mock_inventario1 = Mock()
        mock_inventario1.producto_id = 'prod-123'
        mock_inventario2 = Mock()
        mock_inventario2.producto_id = 'prod-456'
        
        self.mock_db.session.query.return_value.all.return_value = [mock_inventario1, mock_inventario2]
        
        resultado = self.repositorio.obtener_todos()
        
        assert len(resultado) == 2

    def test_obtener_todos_error(self):
        self.mock_db.session.query.side_effect = Exception("Error de DB")
        
        resultado = self.repositorio.obtener_todos()
        
        assert resultado == []

    def test_eliminar_exitoso(self):
        mock_inventario = Mock()
        mock_inventario.producto_id = 'prod-123'
        self.mock_db.session.query.return_value.filter.return_value.first.return_value = mock_inventario
        
        self.repositorio.eliminar('prod-123')
        
        self.mock_db.session.delete.assert_called_once_with(mock_inventario)
        self.mock_db.session.commit.assert_called_once()

    def test_eliminar_no_encontrado(self):
        self.mock_db.session.query.return_value.filter.return_value.first.return_value = None
        
        self.repositorio.eliminar('prod-999')
        
        self.mock_db.session.delete.assert_not_called()

    def test_eliminar_error(self):
        self.mock_db.session.query.side_effect = Exception("Error de DB")
        
        self.repositorio.eliminar('prod-123')
        
        self.mock_db.session.rollback.assert_called_once()
