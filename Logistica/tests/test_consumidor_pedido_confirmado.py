import pytest
import sys
import os
from unittest.mock import Mock, patch
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from aplicacion.eventos.consumidor_pedido_confirmado import ManejadorPedidoConfirmado

class TestManejadorPedidoConfirmado:
    def setup_method(self):
        self.manejador = ManejadorPedidoConfirmado()

    def test_crear_manejador(self):
        assert self.manejador is not None

    @patch('aplicacion.eventos.consumidor_pedido_confirmado.logger')
    @patch('aplicacion.eventos.consumidor_pedido_confirmado.ejecutar_comando')
    def test_manejar_evento_exitoso(self, mock_ejecutar_comando, mock_logger):
        mock_evento = Mock()
        mock_evento.pedido_id = 'pedido-123'
        mock_evento.items = [
            {'producto_id': 'prod-1', 'cantidad': 2},
            {'producto_id': 'prod-2', 'cantidad': 1}
        ]
        
        mock_ejecutar_comando.return_value = {'success': True}
        
        self.manejador.manejar(mock_evento)
        
        mock_logger.info.assert_called()
        mock_ejecutar_comando.assert_called_once()

    @patch('aplicacion.eventos.consumidor_pedido_confirmado.logger')
    @patch('aplicacion.eventos.consumidor_pedido_confirmado.ejecutar_comando')
    def test_manejar_evento_con_error_comando(self, mock_ejecutar_comando, mock_logger):
        mock_evento = Mock()
        mock_evento.pedido_id = 'pedido-123'
        mock_evento.items = [
            {'producto_id': 'prod-1', 'cantidad': 2}
        ]
        
        mock_ejecutar_comando.return_value = {'success': False, 'error': 'Error de inventario'}
        
        self.manejador.manejar(mock_evento)
        
        mock_logger.error.assert_called()
        mock_ejecutar_comando.assert_called_once()

    @patch('aplicacion.eventos.consumidor_pedido_confirmado.logger')
    def test_manejar_evento_con_excepcion(self, mock_logger):
        mock_evento = Mock()
        mock_evento.pedido_id = 'pedido-123'
        mock_evento.items = []
        mock_evento.side_effect = Exception("Error en evento")
        
        self.manejador.manejar(mock_evento)
        
        mock_logger.error.assert_called()

    @patch('aplicacion.eventos.consumidor_pedido_confirmado.logger')
    @patch('aplicacion.eventos.consumidor_pedido_confirmado.ejecutar_comando')
    def test_manejar_evento_con_items_vacios(self, mock_ejecutar_comando, mock_logger):
        mock_evento = Mock()
        mock_evento.pedido_id = 'pedido-123'
        mock_evento.items = []
        
        mock_ejecutar_comando.return_value = {'success': True}
        
        self.manejador.manejar(mock_evento)
        
        mock_ejecutar_comando.assert_called_once()
        # Verificar que se llama con items vacíos
        call_args = mock_ejecutar_comando.call_args[0][0]
        assert call_args.items == []

    @patch('aplicacion.eventos.consumidor_pedido_confirmado.logger')
    @patch('aplicacion.eventos.consumidor_pedido_confirmado.ejecutar_comando')
    def test_manejar_evento_con_items_con_cantidad_cero(self, mock_ejecutar_comando, mock_logger):
        mock_evento = Mock()
        mock_evento.pedido_id = 'pedido-123'
        mock_evento.items = [
            {'producto_id': 'prod-1', 'cantidad': 0}
        ]
        
        mock_ejecutar_comando.return_value = {'success': True}
        
        self.manejador.manejar(mock_evento)
        
        mock_ejecutar_comando.assert_called_once()
        # Verificar que se pasa la cantidad 0
        call_args = mock_ejecutar_comando.call_args[0][0]
        assert call_args.items[0]['cantidad'] == 0

    @patch('aplicacion.eventos.consumidor_pedido_confirmado.logger')
    @patch('aplicacion.eventos.consumidor_pedido_confirmado.ejecutar_comando')
    def test_manejar_evento_con_items_sin_cantidad(self, mock_ejecutar_comando, mock_logger):
        mock_evento = Mock()
        mock_evento.pedido_id = 'pedido-123'
        mock_evento.items = [
            {'producto_id': 'prod-1'}  # Sin cantidad
        ]
        
        mock_ejecutar_comando.return_value = {'success': True}
        
        self.manejador.manejar(mock_evento)
        
        mock_ejecutar_comando.assert_called_once()
        # Verificar que se usa cantidad por defecto 0
        call_args = mock_ejecutar_comando.call_args[0][0]
        assert call_args.items[0]['cantidad'] == 0

    @patch('aplicacion.eventos.consumidor_pedido_confirmado.logger')
    @patch('aplicacion.eventos.consumidor_pedido_confirmado.ejecutar_comando')
    def test_manejar_evento_con_items_sin_producto_id(self, mock_ejecutar_comando, mock_logger):
        mock_evento = Mock()
        mock_evento.pedido_id = 'pedido-123'
        mock_evento.items = [
            {'cantidad': 5}  # Sin producto_id
        ]
        
        mock_ejecutar_comando.return_value = {'success': True}
        
        self.manejador.manejar(mock_evento)
        
        mock_ejecutar_comando.assert_called_once()
        # Verificar que se pasa None para producto_id
        call_args = mock_ejecutar_comando.call_args[0][0]
        assert call_args.items[0]['producto_id'] is None

    @patch('aplicacion.eventos.consumidor_pedido_confirmado.logger')
    @patch('aplicacion.eventos.consumidor_pedido_confirmado.ejecutar_comando')
    def test_manejar_evento_con_multiple_items(self, mock_ejecutar_comando, mock_logger):
        mock_evento = Mock()
        mock_evento.pedido_id = 'pedido-123'
        mock_evento.items = [
            {'producto_id': 'prod-1', 'cantidad': 2},
            {'producto_id': 'prod-2', 'cantidad': 3},
            {'producto_id': 'prod-3', 'cantidad': 1}
        ]
        
        mock_ejecutar_comando.return_value = {'success': True}
        
        self.manejador.manejar(mock_evento)
        
        mock_ejecutar_comando.assert_called_once()
        # Verificar que se procesan todos los items
        call_args = mock_ejecutar_comando.call_args[0][0]
        assert len(call_args.items) == 3
        assert call_args.items[0]['producto_id'] == 'prod-1'
        assert call_args.items[0]['cantidad'] == 2
        assert call_args.items[1]['producto_id'] == 'prod-2'
        assert call_args.items[1]['cantidad'] == 3
        assert call_args.items[2]['producto_id'] == 'prod-3'
        assert call_args.items[2]['cantidad'] == 1