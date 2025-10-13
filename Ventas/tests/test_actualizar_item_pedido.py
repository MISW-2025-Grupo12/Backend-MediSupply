import pytest
import uuid
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock

# Configurar el path para importar los módulos
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from aplicacion.comandos.actualizar_item_pedido import ActualizarItemPedido, ActualizarItemPedidoHandler, ejecutar_actualizar_item_pedido
from dominio.entidades import Pedido, ItemPedido
from dominio.objetos_valor import EstadoPedido, Cantidad, Precio
from dominio.eventos import ItemQuitado

class TestActualizarItemPedido:
    """Pruebas para el comando ActualizarItemPedido"""
    
    def test_crear_comando(self):
        """Test crear comando ActualizarItemPedido"""
        pedido_id = str(uuid.uuid4())
        item_id = str(uuid.uuid4())
        cantidad = 5
        
        comando = ActualizarItemPedido(
            pedido_id=pedido_id,
            item_id=item_id,
            cantidad=cantidad
        )
        
        assert comando.pedido_id == pedido_id
        assert comando.item_id == item_id
        assert comando.cantidad == cantidad

class TestActualizarItemPedidoHandler:
    """Pruebas para el handler ActualizarItemPedidoHandler"""
    
    def setup_method(self):
        """Configurar para cada prueba"""
        self.handler = ActualizarItemPedidoHandler()
        self.pedido_id = str(uuid.uuid4())
        self.item_id = str(uuid.uuid4())
        self.producto_id = str(uuid.uuid4())
    
    def test_handle_pedido_id_vacio(self):
        """Test manejar comando con pedido_id vacío"""
        comando = ActualizarItemPedido(
            pedido_id="",
            item_id=self.item_id,
            cantidad=5
        )
        
        resultado = self.handler.handle(comando)
        
        assert resultado['success'] == False
        assert 'pedido_id e item_id son obligatorios' in resultado['error']
    
    def test_handle_item_id_vacio(self):
        """Test manejar comando con item_id vacío"""
        comando = ActualizarItemPedido(
            pedido_id=self.pedido_id,
            item_id="",
            cantidad=5
        )
        
        resultado = self.handler.handle(comando)
        
        assert resultado['success'] == False
        assert 'pedido_id e item_id son obligatorios' in resultado['error']
    
    def test_handle_pedido_no_encontrado(self):
        """Test manejar comando cuando el pedido no existe"""
        comando = ActualizarItemPedido(
            pedido_id=self.pedido_id,
            item_id=self.item_id,
            cantidad=5
        )
        
        with patch.object(self.handler._repositorio, 'obtener_por_id', return_value=None):
            resultado = self.handler.handle(comando)
            
            assert resultado['success'] == False
            assert resultado['error'] == 'Pedido no encontrado'
    
    def test_handle_pedido_no_borrador(self):
        """Test manejar comando cuando el pedido no está en estado borrador"""
        comando = ActualizarItemPedido(
            pedido_id=self.pedido_id,
            item_id=self.item_id,
            cantidad=5
        )
        
        mock_pedido = Mock()
        mock_pedido.estado.estado = "confirmado"
        
        with patch.object(self.handler._repositorio, 'obtener_por_id', return_value=mock_pedido):
            resultado = self.handler.handle(comando)
            
            assert resultado['success'] == False
            assert 'Solo se pueden actualizar items de pedidos en estado borrador' in resultado['error']
    
    def test_handle_item_no_encontrado(self):
        """Test manejar comando cuando el item no existe en el pedido"""
        comando = ActualizarItemPedido(
            pedido_id=self.pedido_id,
            item_id=self.item_id,
            cantidad=5
        )
        
        mock_pedido = Mock()
        mock_pedido.estado.estado = "borrador"
        mock_pedido.items = []  # Sin items
        
        with patch.object(self.handler._repositorio, 'obtener_por_id', return_value=mock_pedido):
            resultado = self.handler.handle(comando)
            
            assert resultado['success'] == False
            assert resultado['error'] == 'Item no encontrado en el pedido'
    
    def test_handle_cantidad_cero_elimina_item(self):
        """Test manejar comando con cantidad 0 elimina el item"""
        comando = ActualizarItemPedido(
            pedido_id=self.pedido_id,
            item_id=self.item_id,
            cantidad=0
        )
        
        mock_item = Mock()
        mock_item.id = uuid.UUID(self.item_id)
        mock_item.producto_id = self.producto_id
        
        mock_pedido = Mock()
        mock_pedido.estado.estado = "borrador"
        mock_pedido.items = [mock_item]
        mock_pedido.total.valor = 100.0
        mock_pedido.quitar_item.return_value = True
        
        with patch.object(self.handler._repositorio, 'obtener_por_id', return_value=mock_pedido):
            with patch.object(self.handler._repositorio, 'actualizar', return_value=mock_pedido):
                with patch('aplicacion.comandos.actualizar_item_pedido.despachador_eventos') as mock_despachador:
                    resultado = self.handler.handle(comando)
                    
                    assert resultado['success'] == True
                    assert resultado['message'] == 'Item eliminado del pedido'
                    assert resultado['total_pedido'] == 100.0
                    mock_pedido.quitar_item.assert_called_once_with(self.item_id)
                    mock_despachador.publicar_evento.assert_called_once()
    
    def test_handle_cantidad_cero_error_eliminando(self):
        """Test manejar comando con cantidad 0 cuando falla la eliminación"""
        comando = ActualizarItemPedido(
            pedido_id=self.pedido_id,
            item_id=self.item_id,
            cantidad=0
        )
        
        mock_item = Mock()
        mock_item.id = uuid.UUID(self.item_id)
        mock_item.producto_id = self.producto_id
        
        mock_pedido = Mock()
        mock_pedido.estado.estado = "borrador"
        mock_pedido.items = [mock_item]
        mock_pedido.quitar_item.return_value = False  # Falla la eliminación
        
        with patch.object(self.handler._repositorio, 'obtener_por_id', return_value=mock_pedido):
            resultado = self.handler.handle(comando)
            
            assert resultado['success'] == False
            assert resultado['error'] == 'Error eliminando item del pedido'
    
    def test_handle_cantidad_negativa(self):
        """Test manejar comando con cantidad negativa"""
        comando = ActualizarItemPedido(
            pedido_id=self.pedido_id,
            item_id=self.item_id,
            cantidad=-1
        )
        
        mock_item = Mock()
        mock_item.id = uuid.UUID(self.item_id)
        mock_item.producto_id = self.producto_id
        
        mock_pedido = Mock()
        mock_pedido.estado.estado = "borrador"
        mock_pedido.items = [mock_item]
        mock_pedido.quitar_item.return_value = True
        
        with patch.object(self.handler._repositorio, 'obtener_por_id', return_value=mock_pedido):
            with patch.object(self.handler._repositorio, 'actualizar', return_value=mock_pedido):
                with patch('aplicacion.comandos.actualizar_item_pedido.despachador_eventos'):
                    resultado = self.handler.handle(comando)
                    
                    assert resultado['success'] == True
                    assert resultado['message'] == 'Item eliminado del pedido'
    
    def test_handle_cantidad_menor_uno(self):
        """Test manejar comando con cantidad menor a 1"""
        comando = ActualizarItemPedido(
            pedido_id=self.pedido_id,
            item_id=self.item_id,
            cantidad=0.5
        )
        
        mock_item = Mock()
        mock_item.id = uuid.UUID(self.item_id)
        mock_item.producto_id = self.producto_id
        
        mock_pedido = Mock()
        mock_pedido.estado.estado = "borrador"
        mock_pedido.items = [mock_item]
        
        with patch.object(self.handler._repositorio, 'obtener_por_id', return_value=mock_pedido):
            resultado = self.handler.handle(comando)
            
            assert resultado['success'] == False
            assert resultado['error'] == 'La cantidad mínima es 1'
    
    def test_handle_producto_no_encontrado_inventario(self):
        """Test manejar comando cuando el producto no existe en inventario"""
        comando = ActualizarItemPedido(
            pedido_id=self.pedido_id,
            item_id=self.item_id,
            cantidad=5
        )
        
        mock_item = Mock()
        mock_item.id = uuid.UUID(self.item_id)
        mock_item.producto_id = self.producto_id
        
        mock_pedido = Mock()
        mock_pedido.estado.estado = "borrador"
        mock_pedido.items = [mock_item]
        
        with patch.object(self.handler._repositorio, 'obtener_por_id', return_value=mock_pedido):
            with patch.object(self.handler._servicio_logistica, 'obtener_inventario_producto', return_value=None):
                resultado = self.handler.handle(comando)
                
                assert resultado['success'] == False
                assert resultado['error'] == 'Producto no encontrado en inventario'
    
    def test_handle_stock_insuficiente(self):
        """Test manejar comando cuando no hay stock suficiente"""
        comando = ActualizarItemPedido(
            pedido_id=self.pedido_id,
            item_id=self.item_id,
            cantidad=10
        )
        
        mock_item = Mock()
        mock_item.id = uuid.UUID(self.item_id)
        mock_item.producto_id = self.producto_id
        
        mock_pedido = Mock()
        mock_pedido.estado.estado = "borrador"
        mock_pedido.items = [mock_item]
        
        inventario = {'cantidad_disponible': 5}
        
        with patch.object(self.handler._repositorio, 'obtener_por_id', return_value=mock_pedido):
            with patch.object(self.handler._servicio_logistica, 'obtener_inventario_producto', return_value=inventario):
                resultado = self.handler.handle(comando)
                
                assert resultado['success'] == False
                assert 'Stock insuficiente' in resultado['error']
                assert 'Disponible: 5' in resultado['error']
                assert 'Solicitado: 10' in resultado['error']
    
    def test_handle_actualizar_cantidad_error(self):
        """Test manejar comando cuando falla la actualización de cantidad"""
        comando = ActualizarItemPedido(
            pedido_id=self.pedido_id,
            item_id=self.item_id,
            cantidad=5
        )
        
        mock_item = Mock()
        mock_item.id = uuid.UUID(self.item_id)
        mock_item.producto_id = self.producto_id
        
        mock_pedido = Mock()
        mock_pedido.estado.estado = "borrador"
        mock_pedido.items = [mock_item]
        mock_pedido.actualizar_cantidad_item.return_value = False  # Falla la actualización
        
        inventario = {'cantidad_disponible': 10}
        
        with patch.object(self.handler._repositorio, 'obtener_por_id', return_value=mock_pedido):
            with patch.object(self.handler._servicio_logistica, 'obtener_inventario_producto', return_value=inventario):
                resultado = self.handler.handle(comando)
                
                assert resultado['success'] == False
                assert resultado['error'] == 'Error actualizando cantidad del item'
    
    def test_handle_exitoso(self):
        """Test manejar comando exitosamente"""
        comando = ActualizarItemPedido(
            pedido_id=self.pedido_id,
            item_id=self.item_id,
            cantidad=5
        )
        
        mock_item = Mock()
        mock_item.id = uuid.UUID(self.item_id)
        mock_item.producto_id = self.producto_id
        mock_item.calcular_subtotal.return_value = 50.0
        
        mock_pedido = Mock()
        mock_pedido.estado.estado = "borrador"
        mock_pedido.items = [mock_item]
        mock_pedido.actualizar_cantidad_item.return_value = True
        
        mock_pedido_actualizado = Mock()
        mock_pedido_actualizado.total.valor = 100.0
        
        inventario = {'cantidad_disponible': 10}
        
        with patch.object(self.handler._repositorio, 'obtener_por_id', return_value=mock_pedido):
            with patch.object(self.handler._servicio_logistica, 'obtener_inventario_producto', return_value=inventario):
                with patch.object(self.handler._repositorio, 'actualizar', return_value=mock_pedido_actualizado):
                    resultado = self.handler.handle(comando)
                    
                    assert resultado['success'] == True
                    assert resultado['item_id'] == self.item_id
                    assert resultado['producto_id'] == self.producto_id
                    assert resultado['cantidad'] == 5
                    assert resultado['subtotal'] == 50.0
                    assert resultado['total_pedido'] == 100.0
    
    def test_handle_excepcion_general(self):
        """Test manejar comando con excepción general"""
        comando = ActualizarItemPedido(
            pedido_id=self.pedido_id,
            item_id=self.item_id,
            cantidad=5
        )
        
        with patch.object(self.handler._repositorio, 'obtener_por_id', side_effect=Exception("Error de base de datos")):
            with patch('aplicacion.comandos.actualizar_item_pedido.logger') as mock_logger:
                resultado = self.handler.handle(comando)
                
                assert resultado['success'] == False
                assert 'Error interno' in resultado['error']
                assert 'Error de base de datos' in resultado['error']
                mock_logger.error.assert_called_once()

class TestEjecutarActualizarItemPedido:
    """Pruebas para la función ejecutar_actualizar_item_pedido"""
    
    def test_ejecutar_comando(self):
        """Test ejecutar comando ActualizarItemPedido"""
        pedido_id = str(uuid.uuid4())
        item_id = str(uuid.uuid4())
        cantidad = 5
        
        comando = ActualizarItemPedido(
            pedido_id=pedido_id,
            item_id=item_id,
            cantidad=cantidad
        )
        
        with patch('aplicacion.comandos.actualizar_item_pedido.ActualizarItemPedidoHandler') as mock_handler_class:
            mock_handler = Mock()
            mock_handler_class.return_value = mock_handler
            mock_handler.handle.return_value = {'success': True, 'message': 'Item actualizado'}
            
            resultado = ejecutar_actualizar_item_pedido(comando)
            
            assert resultado['success'] == True
            assert resultado['message'] == 'Item actualizado'
            mock_handler.handle.assert_called_once_with(comando)
