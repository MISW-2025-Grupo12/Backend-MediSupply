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
        """Test manejar evento exitoso - ahora ejecuta dos comandos: ReservarInventario y CrearEntrega"""
        mock_evento = Mock()
        mock_evento.pedido_id = 'pedido-123'
        mock_evento.cliente_id = 'cliente-456'
        mock_evento.vendedor_id = 'vendedor-789'
        mock_evento.items = [
            {'producto_id': 'prod-1', 'cantidad': 2},
            {'producto_id': 'prod-2', 'cantidad': 1}
        ]
        mock_evento.total = 150.0
        
        # Simular que ambos comandos son exitosos
        mock_ejecutar_comando.return_value = {'success': True}
        
        self.manejador.manejar(mock_evento)
        
        # Verificar que se llamó ejecutar_comando dos veces (ReservarInventario + CrearEntrega)
        assert mock_ejecutar_comando.call_count == 2
        mock_logger.info.assert_called()

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
    @patch('aplicacion.eventos.consumidor_pedido_confirmado.ejecutar_comando')
    def test_manejar_evento_con_excepcion(self, mock_ejecutar_comando, mock_logger):
        mock_evento = Mock()
        mock_evento.pedido_id = 'pedido-123'
        mock_evento.items = []
        
        # Simular excepción en ejecutar_comando
        mock_ejecutar_comando.side_effect = Exception("Error en comando")
        
        self.manejador.manejar(mock_evento)
        
        mock_logger.error.assert_called()

    @patch('aplicacion.eventos.consumidor_pedido_confirmado.logger')
    @patch('aplicacion.eventos.consumidor_pedido_confirmado.ejecutar_comando')
    def test_manejar_evento_con_items_vacios(self, mock_ejecutar_comando, mock_logger):
        """Test manejar evento con items vacíos - ahora ejecuta dos comandos"""
        mock_evento = Mock()
        mock_evento.pedido_id = 'pedido-123'
        mock_evento.cliente_id = 'cliente-456'
        mock_evento.vendedor_id = 'vendedor-789'
        mock_evento.items = []
        mock_evento.total = 0.0
        
        mock_ejecutar_comando.return_value = {'success': True}
        
        self.manejador.manejar(mock_evento)
        
        # Verificar que se llamó ejecutar_comando dos veces (ReservarInventario + CrearEntrega)
        assert mock_ejecutar_comando.call_count == 2
        
        # Verificar que la primera llamada es ReservarInventario con items vacíos
        primera_llamada = mock_ejecutar_comando.call_args_list[0][0][0]
        from aplicacion.comandos.reservar_inventario import ReservarInventario
        assert isinstance(primera_llamada, ReservarInventario)
        assert primera_llamada.items == []

    @patch('aplicacion.eventos.consumidor_pedido_confirmado.logger')
    @patch('aplicacion.eventos.consumidor_pedido_confirmado.ejecutar_comando')
    def test_manejar_evento_con_items_con_cantidad_cero(self, mock_ejecutar_comando, mock_logger):
        """Test manejar evento con items con cantidad cero - ahora ejecuta dos comandos"""
        mock_evento = Mock()
        mock_evento.pedido_id = 'pedido-123'
        mock_evento.cliente_id = 'cliente-456'
        mock_evento.vendedor_id = 'vendedor-789'
        mock_evento.items = [
            {'producto_id': 'prod-1', 'cantidad': 0}
        ]
        mock_evento.total = 0.0
        
        mock_ejecutar_comando.return_value = {'success': True}
        
        self.manejador.manejar(mock_evento)
        
        # Verificar que se llamó ejecutar_comando dos veces (ReservarInventario + CrearEntrega)
        assert mock_ejecutar_comando.call_count == 2
        
        # Verificar que se pasa la cantidad 0 en ReservarInventario
        primera_llamada = mock_ejecutar_comando.call_args_list[0][0][0]
        from aplicacion.comandos.reservar_inventario import ReservarInventario
        assert isinstance(primera_llamada, ReservarInventario)
        assert primera_llamada.items[0]['cantidad'] == 0

    @patch('aplicacion.eventos.consumidor_pedido_confirmado.logger')
    @patch('aplicacion.eventos.consumidor_pedido_confirmado.ejecutar_comando')
    def test_manejar_evento_con_items_sin_cantidad(self, mock_ejecutar_comando, mock_logger):
        """Test manejar evento con items sin cantidad - ahora ejecuta dos comandos"""
        mock_evento = Mock()
        mock_evento.pedido_id = 'pedido-123'
        mock_evento.cliente_id = 'cliente-456'
        mock_evento.vendedor_id = 'vendedor-789'
        mock_evento.items = [
            {'producto_id': 'prod-1'}  # Sin cantidad
        ]
        mock_evento.total = 0.0
        
        mock_ejecutar_comando.return_value = {'success': True}
        
        self.manejador.manejar(mock_evento)
        
        # Verificar que se llamó ejecutar_comando dos veces (ReservarInventario + CrearEntrega)
        assert mock_ejecutar_comando.call_count == 2
        
        # Verificar que se usa cantidad por defecto 0 en ReservarInventario
        primera_llamada = mock_ejecutar_comando.call_args_list[0][0][0]
        from aplicacion.comandos.reservar_inventario import ReservarInventario
        assert isinstance(primera_llamada, ReservarInventario)
        assert primera_llamada.items[0]['cantidad'] == 0

    @patch('aplicacion.eventos.consumidor_pedido_confirmado.logger')
    @patch('aplicacion.eventos.consumidor_pedido_confirmado.ejecutar_comando')
    def test_manejar_evento_con_items_sin_producto_id(self, mock_ejecutar_comando, mock_logger):
        """Test manejar evento con items sin producto_id - ahora ejecuta dos comandos"""
        mock_evento = Mock()
        mock_evento.pedido_id = 'pedido-123'
        mock_evento.cliente_id = 'cliente-456'
        mock_evento.vendedor_id = 'vendedor-789'
        mock_evento.items = [
            {'cantidad': 5}  # Sin producto_id
        ]
        mock_evento.total = 0.0
        
        mock_ejecutar_comando.return_value = {'success': True}
        
        self.manejador.manejar(mock_evento)
        
        # Verificar que se llamó ejecutar_comando dos veces (ReservarInventario + CrearEntrega)
        assert mock_ejecutar_comando.call_count == 2
        
        # Verificar que se pasa None para producto_id en ReservarInventario
        primera_llamada = mock_ejecutar_comando.call_args_list[0][0][0]
        from aplicacion.comandos.reservar_inventario import ReservarInventario
        assert isinstance(primera_llamada, ReservarInventario)
        assert primera_llamada.items[0]['producto_id'] is None

    @patch('aplicacion.eventos.consumidor_pedido_confirmado.logger')
    @patch('aplicacion.eventos.consumidor_pedido_confirmado.ejecutar_comando')
    def test_manejar_evento_con_multiple_items(self, mock_ejecutar_comando, mock_logger):
        """Test manejar evento con múltiples items - ahora ejecuta dos comandos"""
        mock_evento = Mock()
        mock_evento.pedido_id = 'pedido-123'
        mock_evento.cliente_id = 'cliente-456'
        mock_evento.vendedor_id = 'vendedor-789'
        mock_evento.items = [
            {'producto_id': 'prod-1', 'cantidad': 2},
            {'producto_id': 'prod-2', 'cantidad': 3},
            {'producto_id': 'prod-3', 'cantidad': 1}
        ]
        mock_evento.total = 300.0
        
        mock_ejecutar_comando.return_value = {'success': True}
        
        self.manejador.manejar(mock_evento)
        
        # Verificar que se llamó ejecutar_comando dos veces (ReservarInventario + CrearEntrega)
        assert mock_ejecutar_comando.call_count == 2
        
        # Verificar que se procesan todos los items en ReservarInventario
        primera_llamada = mock_ejecutar_comando.call_args_list[0][0][0]
        from aplicacion.comandos.reservar_inventario import ReservarInventario
        assert isinstance(primera_llamada, ReservarInventario)
        assert len(primera_llamada.items) == 3
        assert primera_llamada.items[0]['producto_id'] == 'prod-1'
        assert primera_llamada.items[0]['cantidad'] == 2
        assert primera_llamada.items[1]['producto_id'] == 'prod-2'
        assert primera_llamada.items[1]['cantidad'] == 3
        assert primera_llamada.items[2]['producto_id'] == 'prod-3'
        assert primera_llamada.items[2]['cantidad'] == 1

    @patch('aplicacion.eventos.consumidor_pedido_confirmado.logger')
    @patch('aplicacion.eventos.consumidor_pedido_confirmado.ejecutar_comando')
    def test_manejar_evento_error_reservar_inventario_con_detalle(self, mock_ejecutar_comando, mock_logger):
        """Test manejar evento con error en reserva de inventario con detalle específico"""
        mock_evento = Mock()
        mock_evento.pedido_id = 'pedido-123'
        mock_evento.cliente_id = 'cliente-456'
        mock_evento.vendedor_id = 'vendedor-789'
        mock_evento.items = [
            {'producto_id': 'prod-1', 'cantidad': 2}
        ]
        mock_evento.total = 100.0
        
        # Simular error en ReservarInventario con detalle
        mock_ejecutar_comando.return_value = {
            'success': False,
            'error': 'Error de conexión'
        }
        
        self.manejador.manejar(mock_evento)
        
        # Verificar que se llamó ejecutar_comando una vez (solo ReservarInventario)
        assert mock_ejecutar_comando.call_count == 1
        
        # Verificar que se registró el error
        mock_logger.error.assert_called()
        error_call_args = str(mock_logger.error.call_args)
        assert 'Error reservando inventario' in error_call_args or 'pedido-123' in error_call_args
        
        # Verificar que NO se intentó crear entrega (porque falló la reserva)
        # El segundo comando (CrearEntrega) no debería ejecutarse
        assert mock_ejecutar_comando.call_count == 1

    @patch('aplicacion.eventos.consumidor_pedido_confirmado.logger')
    @patch('aplicacion.eventos.consumidor_pedido_confirmado.ejecutar_comando')
    def test_manejar_evento_error_reservar_inventario_sin_detalle(self, mock_ejecutar_comando, mock_logger):
        """Test manejar evento con error en reserva de inventario sin detalle específico"""
        mock_evento = Mock()
        mock_evento.pedido_id = 'pedido-123'
        mock_evento.cliente_id = 'cliente-456'
        mock_evento.vendedor_id = 'vendedor-789'
        mock_evento.items = [
            {'producto_id': 'prod-1', 'cantidad': 2}
        ]
        mock_evento.total = 100.0
        
        # Simular error en ReservarInventario sin campo 'error'
        mock_ejecutar_comando.return_value = {
            'success': False
            # Sin campo 'error'
        }
        
        self.manejador.manejar(mock_evento)
        
        # Verificar que se llamó ejecutar_comando una vez (solo ReservarInventario)
        assert mock_ejecutar_comando.call_count == 1
        
        # Verificar que se registró el error
        mock_logger.error.assert_called()
        
        # Verificar que NO se intentó crear entrega (porque falló la reserva)
        assert mock_ejecutar_comando.call_count == 1

    @patch('aplicacion.eventos.consumidor_pedido_confirmado.logger')
    @patch('aplicacion.eventos.consumidor_pedido_confirmado.ejecutar_comando')
    def test_manejar_evento_error_crear_entrega_despues_reserva_exitosa(self, mock_ejecutar_comando, mock_logger):
        """Test manejar evento con error al crear entrega después de reservar inventario exitosamente"""
        mock_evento = Mock()
        mock_evento.pedido_id = 'pedido-123'
        mock_evento.cliente_id = 'cliente-456'
        mock_evento.vendedor_id = 'vendedor-789'
        mock_evento.items = [
            {'producto_id': 'prod-1', 'cantidad': 2}
        ]
        mock_evento.total = 100.0
        
        # Simular que ReservarInventario es exitoso pero CrearEntrega falla
        def side_effect(comando):
            # Primera llamada: ReservarInventario (exitoso)
            from aplicacion.comandos.reservar_inventario import ReservarInventario
            if isinstance(comando, ReservarInventario):
                return {'success': True}
            # Segunda llamada: CrearEntrega (falla)
            else:
                return {'success': False, 'error': 'Error creando entrega: Cliente no encontrado'}
        
        mock_ejecutar_comando.side_effect = side_effect
        
        self.manejador.manejar(mock_evento)
        
        # Verificar que se llamó ejecutar_comando dos veces (ReservarInventario + CrearEntrega)
        assert mock_ejecutar_comando.call_count == 2
        
        # Verificar que se registró el error de crear entrega
        mock_logger.error.assert_called()
        error_call_args = str(mock_logger.error.call_args)
        assert 'Error creando entrega' in error_call_args or 'pedido-123' in error_call_args

    @patch('aplicacion.eventos.consumidor_pedido_confirmado.logger')
    @patch('aplicacion.eventos.consumidor_pedido_confirmado.ejecutar_comando')
    def test_manejar_evento_flujo_completo_exitoso(self, mock_ejecutar_comando, mock_logger):
        """Test manejar evento con flujo completo exitoso (reserva + creación de entrega)"""
        mock_evento = Mock()
        mock_evento.pedido_id = 'pedido-123'
        mock_evento.cliente_id = 'cliente-456'
        mock_evento.vendedor_id = 'vendedor-789'
        mock_evento.items = [
            {'producto_id': 'prod-1', 'cantidad': 2},
            {'producto_id': 'prod-2', 'cantidad': 3}
        ]
        mock_evento.total = 250.0
        
        # Simular que ambos comandos son exitosos
        def side_effect(comando):
            # Primera llamada: ReservarInventario (exitoso)
            from aplicacion.comandos.reservar_inventario import ReservarInventario
            if isinstance(comando, ReservarInventario):
                return {'success': True, 'message': 'Inventario reservado exitosamente'}
            # Segunda llamada: CrearEntrega (exitoso)
            else:
                return {'success': True, 'message': 'Entrega creada exitosamente', 'entrega_id': 'entrega-999'}
        
        mock_ejecutar_comando.side_effect = side_effect
        
        self.manejador.manejar(mock_evento)
        
        # Verificar que se llamó ejecutar_comando dos veces (ReservarInventario + CrearEntrega)
        assert mock_ejecutar_comando.call_count == 2
        
        # Verificar que se registraron los mensajes de éxito
        info_calls = [str(call) for call in mock_logger.info.call_args_list]
        assert any('Inventario reservado exitosamente' in call or 'pedido-123' in call for call in info_calls)
        assert any('Entrega creada exitosamente' in call or 'pedido-123' in call for call in info_calls)