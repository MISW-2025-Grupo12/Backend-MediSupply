import pytest
import uuid
from unittest.mock import Mock, patch

# Configurar el path para importar los módulos
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from aplicacion.comandos.quitar_item_pedido import QuitarItemPedido, QuitarItemPedidoHandler, ejecutar_quitar_item_pedido
from dominio.eventos import ItemQuitado

class TestQuitarItemPedido:
    """Pruebas para el comando QuitarItemPedido"""
    
    def test_crear_comando(self):
        """Test crear comando QuitarItemPedido"""
        pedido_id = str(uuid.uuid4())
        item_id = str(uuid.uuid4())
        
        comando = QuitarItemPedido(
            pedido_id=pedido_id,
            item_id=item_id
        )
        
        assert comando.pedido_id == pedido_id
        assert comando.item_id == item_id

class TestQuitarItemPedidoHandler:
    """Pruebas para el handler QuitarItemPedidoHandler"""
    
    def setup_method(self):
        """Configurar para cada prueba"""
        self.handler = QuitarItemPedidoHandler()
        self.pedido_id = str(uuid.uuid4())
        self.item_id = str(uuid.uuid4())
        self.producto_id = str(uuid.uuid4())
    
    def test_handle_pedido_id_vacio(self):
        """Test manejar comando con pedido_id vacío"""
        comando = QuitarItemPedido(
            pedido_id="",
            item_id=self.item_id
        )
        
        resultado = self.handler.handle(comando)
        
        assert resultado['success'] == False
        assert 'pedido_id e item_id son obligatorios' in resultado['error']
    
    def test_handle_item_id_vacio(self):
        """Test manejar comando con item_id vacío"""
        comando = QuitarItemPedido(
            pedido_id=self.pedido_id,
            item_id=""
        )
        
        resultado = self.handler.handle(comando)
        
        assert resultado['success'] == False
        assert 'pedido_id e item_id son obligatorios' in resultado['error']
    
    def test_handle_pedido_no_encontrado(self):
        """Test manejar comando cuando el pedido no existe"""
        comando = QuitarItemPedido(
            pedido_id=self.pedido_id,
            item_id=self.item_id
        )
        
        with patch.object(self.handler._repositorio, 'obtener_por_id', return_value=None):
            resultado = self.handler.handle(comando)
            
            assert resultado['success'] == False
            assert resultado['error'] == 'Pedido no encontrado'
    
    def test_handle_pedido_no_borrador(self):
        """Test manejar comando cuando el pedido no está en estado borrador"""
        comando = QuitarItemPedido(
            pedido_id=self.pedido_id,
            item_id=self.item_id
        )
        
        mock_pedido = Mock()
        mock_pedido.estado.estado = "confirmado"
        
        with patch.object(self.handler._repositorio, 'obtener_por_id', return_value=mock_pedido):
            resultado = self.handler.handle(comando)
            
            assert resultado['success'] == False
            assert 'Solo se pueden quitar items de pedidos en estado borrador' in resultado['error']
    
    def test_handle_item_no_encontrado(self):
        """Test manejar comando cuando el item no existe en el pedido"""
        comando = QuitarItemPedido(
            pedido_id=self.pedido_id,
            item_id=self.item_id
        )
        
        mock_pedido = Mock()
        mock_pedido.estado.estado = "borrador"
        mock_pedido.items = []  # Sin items
        
        with patch.object(self.handler._repositorio, 'obtener_por_id', return_value=mock_pedido):
            resultado = self.handler.handle(comando)
            
            assert resultado['success'] == False
            assert resultado['error'] == 'Item no encontrado en el pedido'
    
    def test_handle_quitar_item_error(self):
        """Test manejar comando cuando falla quitar item del pedido"""
        comando = QuitarItemPedido(
            pedido_id=self.pedido_id,
            item_id=self.item_id
        )
        
        mock_item = Mock()
        mock_item.id = uuid.UUID(self.item_id)
        mock_item.producto_id = self.producto_id
        
        mock_pedido = Mock()
        mock_pedido.estado.estado = "borrador"
        mock_pedido.items = [mock_item]
        mock_pedido.quitar_item.return_value = False  # Falla quitar item
        
        with patch.object(self.handler._repositorio, 'obtener_por_id', return_value=mock_pedido):
            resultado = self.handler.handle(comando)
            
            assert resultado['success'] == False
            assert resultado['error'] == 'Error quitando item del pedido'
    
    def test_handle_exitoso(self):
        """Test manejar comando exitosamente"""
        comando = QuitarItemPedido(
            pedido_id=self.pedido_id,
            item_id=self.item_id
        )
        
        mock_item = Mock()
        mock_item.id = uuid.UUID(self.item_id)
        mock_item.producto_id = self.producto_id
        
        mock_pedido = Mock()
        mock_pedido.estado.estado = "borrador"
        mock_pedido.items = [mock_item]
        mock_pedido.quitar_item.return_value = True
        mock_pedido.id = uuid.uuid4()
        
        mock_pedido_actualizado = Mock()
        mock_pedido_actualizado.total.valor = 100.0
        
        with patch.object(self.handler._repositorio, 'obtener_por_id', return_value=mock_pedido):
            with patch.object(self.handler._repositorio, 'actualizar', return_value=mock_pedido_actualizado):
                with patch('aplicacion.comandos.quitar_item_pedido.despachador_eventos') as mock_despachador:
                    resultado = self.handler.handle(comando)
                    
                    assert resultado['success'] == True
                    assert resultado['message'] == 'Item quitado del pedido exitosamente'
                    assert resultado['total_pedido'] == 100.0
                    mock_pedido.quitar_item.assert_called_once_with(self.item_id)
                    mock_despachador.publicar_evento.assert_called_once()
    
    def test_handle_excepcion_general(self):
        """Test manejar comando con excepción general"""
        comando = QuitarItemPedido(
            pedido_id=self.pedido_id,
            item_id=self.item_id
        )
        
        with patch.object(self.handler._repositorio, 'obtener_por_id', side_effect=Exception("Error de base de datos")):
            with patch('aplicacion.comandos.quitar_item_pedido.logger') as mock_logger:
                resultado = self.handler.handle(comando)
                
                assert resultado['success'] == False
                assert 'Error interno' in resultado['error']
                assert 'Error de base de datos' in resultado['error']
                mock_logger.error.assert_called_once()

class TestEjecutarQuitarItemPedido:
    """Pruebas para la función ejecutar_quitar_item_pedido"""
    
    def test_ejecutar_comando(self):
        """Test ejecutar comando QuitarItemPedido"""
        pedido_id = str(uuid.uuid4())
        item_id = str(uuid.uuid4())
        
        comando = QuitarItemPedido(
            pedido_id=pedido_id,
            item_id=item_id
        )
        
        with patch('aplicacion.comandos.quitar_item_pedido.QuitarItemPedidoHandler') as mock_handler_class:
            mock_handler = Mock()
            mock_handler_class.return_value = mock_handler
            mock_handler.handle.return_value = {'success': True, 'message': 'Item quitado'}
            
            resultado = ejecutar_quitar_item_pedido(comando)
            
            assert resultado['success'] == True
            assert resultado['message'] == 'Item quitado'
            mock_handler.handle.assert_called_once_with(comando)
