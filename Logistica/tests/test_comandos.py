import pytest
import sys
import os
from unittest.mock import Mock, patch
from datetime import datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from aplicacion.comandos.descontar_inventario import DescontarInventario, DescontarInventarioHandler
from aplicacion.comandos.reservar_inventario import ReservarInventario, ReservarInventarioHandler
from aplicacion.dto import InventarioDTO

class TestDescontarInventario:
    def setup_method(self):
        self.handler = DescontarInventarioHandler()
        self.mock_repositorio = Mock()
        self.handler._repositorio = self.mock_repositorio

    def test_crear_comando(self):
        comando = DescontarInventario(items=[{"producto_id": "prod-1", "cantidad": 5}])
        assert comando.items[0]["producto_id"] == "prod-1"
        assert comando.items[0]["cantidad"] == 5

    def test_handle_datos_invalidos(self):
        comando = DescontarInventario(items=[{"producto_id": "", "cantidad": 0}])
        resultado = self.handler.handle(comando)
        
        assert resultado['success'] == False
        assert 'Datos inválidos' in resultado['error']

    def test_handle_producto_no_encontrado(self):
        comando = DescontarInventario(items=[{"producto_id": "prod-1", "cantidad": 5}])
        self.mock_repositorio.obtener_por_producto_id.return_value = None
        
        resultado = self.handler.handle(comando)
        
        assert resultado['success'] == False
        assert 'no encontrado en inventario' in resultado['error']

    def test_handle_cantidad_reservada_insuficiente(self):
        comando = DescontarInventario(items=[{"producto_id": "prod-1", "cantidad": 10}])
        inventario_dto = InventarioDTO(
            producto_id="prod-1",
            cantidad_disponible=20,
            cantidad_reservada=5,
            fecha_vencimiento=datetime.now() + timedelta(days=30)
        )
        self.mock_repositorio.obtener_por_producto_id.return_value = [inventario_dto]
        
        resultado = self.handler.handle(comando)
        
        assert resultado['success'] == False
        assert 'Cantidad reservada insuficiente' in resultado['error']

    def test_handle_exitoso(self):
        comando = DescontarInventario(items=[{"producto_id": "prod-1", "cantidad": 5}])
        inventario_dto = InventarioDTO(
            producto_id="prod-1",
            cantidad_disponible=20,
            cantidad_reservada=10,
            fecha_vencimiento=datetime.now() + timedelta(days=30),
            bodega_id="bodega-1"
        )
        self.mock_repositorio.obtener_por_producto_id.return_value = [inventario_dto]
        
        with patch('infraestructura.modelos.InventarioModel') as mock_inventario_model, \
             patch('config.db.db') as mock_db:
            # Mock del modelo de inventario
            mock_lote = Mock()
            mock_lote.cantidad_disponible = 20
            mock_lote.cantidad_reservada = 10
            mock_lote.fecha_vencimiento = datetime.now() + timedelta(days=30)
            mock_inventario_model.query.filter_by.return_value.first.return_value = mock_lote
            
            # Mock de la sesión de DB
            mock_db.session.commit.return_value = None
            
            resultado = self.handler.handle(comando)
            
            assert resultado['success'] == True
            assert 'Inventario descontado exitosamente' in resultado['message']
            mock_db.session.commit.assert_called()

    def test_handle_error_descontar_cantidad(self):
        comando = DescontarInventario(items=[{"producto_id": "prod-1", "cantidad": 5}])
        inventario_dto = InventarioDTO(
            producto_id="prod-1",
            cantidad_disponible=20,
            cantidad_reservada=10,
            fecha_vencimiento=datetime.now() + timedelta(days=30),
            bodega_id="bodega-1"
        )
        self.mock_repositorio.obtener_por_producto_id.return_value = [inventario_dto]
        
        with patch('infraestructura.modelos.InventarioModel') as mock_inventario_model, \
             patch('config.db.db') as mock_db:
            # Mock del modelo de inventario
            mock_lote = Mock()
            mock_lote.cantidad_disponible = 20
            mock_lote.cantidad_reservada = 10
            mock_lote.fecha_vencimiento = datetime.now() + timedelta(days=30)
            mock_inventario_model.query.filter_by.return_value.first.return_value = mock_lote
            
            # Mock de la sesión de DB que falla
            mock_db.session.commit.side_effect = Exception("Error en DB")
            
            resultado = self.handler.handle(comando)
            
            assert resultado['success'] == False
            assert 'Error interno' in resultado['error']

    def test_handle_excepcion(self):
        comando = DescontarInventario(items=[{"producto_id": "prod-1", "cantidad": 5}])
        self.mock_repositorio.obtener_por_producto_id.side_effect = Exception("Error de BD")
        
        resultado = self.handler.handle(comando)
        
        assert resultado['success'] == False
        assert 'Error interno' in resultado['error']

class TestReservarInventario:
    def setup_method(self):
        self.handler = ReservarInventarioHandler()
        self.mock_repositorio = Mock()
        self.handler._repositorio = self.mock_repositorio

    def test_crear_comando(self):
        comando = ReservarInventario(items=[{"producto_id": "prod-1", "cantidad": 5}])
        assert comando.items[0]["producto_id"] == "prod-1"
        assert comando.items[0]["cantidad"] == 5

    def test_handle_datos_invalidos(self):
        comando = ReservarInventario(items=[{"producto_id": "", "cantidad": 0}])
        resultado = self.handler.handle(comando)
        
        assert resultado['success'] == False
        assert 'Datos inválidos' in resultado['error']

    def test_handle_producto_no_encontrado(self):
        comando = ReservarInventario(items=[{"producto_id": "prod-1", "cantidad": 5}])
        self.mock_repositorio.obtener_por_producto_id.return_value = None
        
        resultado = self.handler.handle(comando)
        
        assert resultado['success'] == False
        assert 'no encontrado en inventario' in resultado['error']

    def test_handle_stock_insuficiente(self):
        comando = ReservarInventario(items=[{"producto_id": "prod-1", "cantidad": 10}])
        inventario_dto = InventarioDTO(
            producto_id="prod-1",
            cantidad_disponible=5,
            cantidad_reservada=0,
            fecha_vencimiento=datetime.now() + timedelta(days=30)
        )
        self.mock_repositorio.obtener_por_producto_id.return_value = [inventario_dto]
        
        resultado = self.handler.handle(comando)
        
        assert resultado['success'] == False
        assert 'Stock insuficiente' in resultado['error']

    def test_handle_exitoso(self):
        comando = ReservarInventario(items=[{"producto_id": "prod-1", "cantidad": 5}])
        inventario_dto = InventarioDTO(
            producto_id="prod-1",
            cantidad_disponible=10,
            cantidad_reservada=0,
            fecha_vencimiento=datetime.now() + timedelta(days=30)
        )
        self.mock_repositorio.obtener_por_producto_id.return_value = [inventario_dto]
        
        with patch('aplicacion.comandos.reservar_inventario.Inventario') as mock_inventario_class:
            mock_inventario = Mock()
            mock_inventario.reservar_cantidad.return_value = True
            mock_inventario.producto_id.valor = "prod-1"
            mock_inventario.cantidad_disponible.valor = 5
            mock_inventario.cantidad_reservada.valor = 5
            mock_inventario_class.return_value = mock_inventario
            
            resultado = self.handler.handle(comando)
            
            assert resultado['success'] == True
            assert 'Inventario reservado exitosamente' in resultado['message']
            self.mock_repositorio.crear_o_actualizar.assert_called_once()

    def test_handle_error_reservar_cantidad(self):
        comando = ReservarInventario(items=[{"producto_id": "prod-1", "cantidad": 5}])
        inventario_dto = InventarioDTO(
            producto_id="prod-1",
            cantidad_disponible=10,
            cantidad_reservada=0,
            fecha_vencimiento=datetime.now() + timedelta(days=30)
        )
        self.mock_repositorio.obtener_por_producto_id.return_value = [inventario_dto]
        
        with patch('aplicacion.comandos.reservar_inventario.Inventario') as mock_inventario_class:
            mock_inventario = Mock()
            mock_inventario.reservar_cantidad.return_value = False
            mock_inventario_class.return_value = mock_inventario
            
            resultado = self.handler.handle(comando)
            
            assert resultado['success'] == False
            assert 'Error reservando inventario' in resultado['error']

    def test_handle_excepcion(self):
        comando = ReservarInventario(items=[{"producto_id": "prod-1", "cantidad": 5}])
        self.mock_repositorio.obtener_por_producto_id.side_effect = Exception("Error de BD")
        
        resultado = self.handler.handle(comando)
        
        assert resultado['success'] == False
        assert 'Error interno' in resultado['error']
