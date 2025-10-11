import pytest
import uuid
from unittest.mock import Mock, patch

# Configurar el path para importar los módulos
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from aplicacion.comandos.agregar_item_pedido import AgregarItemPedido, AgregarItemPedidoHandler, ejecutar_agregar_item_pedido
from dominio.entidades import ItemPedido
from dominio.objetos_valor import Cantidad, Precio
from dominio.eventos import ItemAgregado

class TestAgregarItemPedido:
    """Pruebas para el comando AgregarItemPedido"""
    
    def test_crear_comando(self):
        """Test crear comando AgregarItemPedido"""
        pedido_id = str(uuid.uuid4())
        producto_id = str(uuid.uuid4())
        cantidad = 5
        
        comando = AgregarItemPedido(
            pedido_id=pedido_id,
            producto_id=producto_id,
            cantidad=cantidad
        )
        
        assert comando.pedido_id == pedido_id
        assert comando.producto_id == producto_id
        assert comando.cantidad == cantidad

class TestAgregarItemPedidoHandler:
    """Pruebas para el handler AgregarItemPedidoHandler"""
    
    def setup_method(self):
        """Configurar para cada prueba"""
        self.handler = AgregarItemPedidoHandler()
        self.pedido_id = str(uuid.uuid4())
        self.producto_id = str(uuid.uuid4())
        self.cantidad = 5
    
    def test_handle_pedido_id_vacio(self):
        """Test manejar comando con pedido_id vacío"""
        comando = AgregarItemPedido(
            pedido_id="",
            producto_id=self.producto_id,
            cantidad=self.cantidad
        )
        
        resultado = self.handler.handle(comando)
        
        assert resultado['success'] == False
        assert 'pedido_id, producto_id y cantidad > 0 son obligatorios' in resultado['error']
    
    def test_handle_producto_id_vacio(self):
        """Test manejar comando con producto_id vacío"""
        comando = AgregarItemPedido(
            pedido_id=self.pedido_id,
            producto_id="",
            cantidad=self.cantidad
        )
        
        resultado = self.handler.handle(comando)
        
        assert resultado['success'] == False
        assert 'pedido_id, producto_id y cantidad > 0 son obligatorios' in resultado['error']
    
    def test_handle_cantidad_cero(self):
        """Test manejar comando con cantidad 0"""
        comando = AgregarItemPedido(
            pedido_id=self.pedido_id,
            producto_id=self.producto_id,
            cantidad=0
        )
        
        resultado = self.handler.handle(comando)
        
        assert resultado['success'] == False
        assert 'pedido_id, producto_id y cantidad > 0 son obligatorios' in resultado['error']
    
    def test_handle_cantidad_negativa(self):
        """Test manejar comando con cantidad negativa"""
        comando = AgregarItemPedido(
            pedido_id=self.pedido_id,
            producto_id=self.producto_id,
            cantidad=-1
        )
        
        resultado = self.handler.handle(comando)
        
        assert resultado['success'] == False
        assert 'pedido_id, producto_id y cantidad > 0 son obligatorios' in resultado['error']
    
    def test_handle_pedido_no_encontrado(self):
        """Test manejar comando cuando el pedido no existe"""
        comando = AgregarItemPedido(
            pedido_id=self.pedido_id,
            producto_id=self.producto_id,
            cantidad=self.cantidad
        )
        
        with patch.object(self.handler._repositorio, 'obtener_por_id', return_value=None):
            resultado = self.handler.handle(comando)
            
            assert resultado['success'] == False
            assert resultado['error'] == 'Pedido no encontrado'
    
    def test_handle_pedido_no_borrador(self):
        """Test manejar comando cuando el pedido no está en estado borrador"""
        comando = AgregarItemPedido(
            pedido_id=self.pedido_id,
            producto_id=self.producto_id,
            cantidad=self.cantidad
        )
        
        mock_pedido = Mock()
        mock_pedido.estado.estado = "confirmado"
        
        with patch.object(self.handler._repositorio, 'obtener_por_id', return_value=mock_pedido):
            resultado = self.handler.handle(comando)
            
            assert resultado['success'] == False
            assert 'Solo se pueden agregar items a pedidos en estado borrador' in resultado['error']
    
    def test_handle_producto_no_encontrado(self):
        """Test manejar comando cuando el producto no existe"""
        comando = AgregarItemPedido(
            pedido_id=self.pedido_id,
            producto_id=self.producto_id,
            cantidad=self.cantidad
        )
        
        mock_pedido = Mock()
        mock_pedido.estado.estado = "borrador"
        
        with patch.object(self.handler._repositorio, 'obtener_por_id', return_value=mock_pedido):
            with patch.object(self.handler._servicio_productos, 'obtener_producto_por_id', return_value=None):
                resultado = self.handler.handle(comando)
                
                assert resultado['success'] == False
                assert f'Producto {self.producto_id} no encontrado en el catálogo' in resultado['error']
    
    def test_handle_producto_precio_invalido(self):
        """Test manejar comando cuando el producto tiene precio inválido"""
        comando = AgregarItemPedido(
            pedido_id=self.pedido_id,
            producto_id=self.producto_id,
            cantidad=self.cantidad
        )
        
        mock_pedido = Mock()
        mock_pedido.estado.estado = "borrador"
        
        producto = {'nombre': 'Producto Test', 'precio': 0.0}
        
        with patch.object(self.handler._repositorio, 'obtener_por_id', return_value=mock_pedido):
            with patch.object(self.handler._servicio_productos, 'obtener_producto_por_id', return_value=producto):
                resultado = self.handler.handle(comando)
                
                assert resultado['success'] == False
                assert f'El producto {self.producto_id} no tiene un precio válido' in resultado['error']
    
    def test_handle_agregar_item_error(self):
        """Test manejar comando cuando falla agregar item al pedido"""
        comando = AgregarItemPedido(
            pedido_id=self.pedido_id,
            producto_id=self.producto_id,
            cantidad=self.cantidad
        )
        
        mock_pedido = Mock()
        mock_pedido.estado.estado = "borrador"
        mock_pedido.agregar_item.return_value = False  # Falla agregar item
        
        producto = {'nombre': 'Producto Test', 'precio': 10.0}
        
        with patch.object(self.handler._repositorio, 'obtener_por_id', return_value=mock_pedido):
            with patch.object(self.handler._servicio_productos, 'obtener_producto_por_id', return_value=producto):
                resultado = self.handler.handle(comando)
                
                assert resultado['success'] == False
                assert resultado['error'] == 'Error agregando item al pedido'
    
    def test_handle_exitoso(self):
        """Test manejar comando exitosamente"""
        comando = AgregarItemPedido(
            pedido_id=self.pedido_id,
            producto_id=self.producto_id,
            cantidad=self.cantidad
        )
        
        mock_pedido = Mock()
        mock_pedido.estado.estado = "borrador"
        mock_pedido.agregar_item.return_value = True
        mock_pedido.id = uuid.uuid4()
        
        mock_pedido_actualizado = Mock()
        
        producto = {'nombre': 'Producto Test', 'precio': 10.0}
        
        with patch.object(self.handler._repositorio, 'obtener_por_id', return_value=mock_pedido):
            with patch.object(self.handler._servicio_productos, 'obtener_producto_por_id', return_value=producto):
                with patch.object(self.handler._repositorio, 'actualizar', return_value=mock_pedido_actualizado):
                    with patch('aplicacion.comandos.agregar_item_pedido.despachador_eventos') as mock_despachador:
                        resultado = self.handler.handle(comando)
                        
                        assert resultado['success'] == True
                        assert resultado['producto_id'] == self.producto_id
                        assert resultado['nombre_producto'] == 'Producto Test'
                        assert resultado['cantidad'] == self.cantidad
                        assert resultado['precio_unitario'] == 10.0
                        assert 'Item agregado exitosamente' in resultado['mensaje']
                        mock_despachador.publicar_evento.assert_called_once()
    
    def test_handle_excepcion_general(self):
        """Test manejar comando con excepción general"""
        comando = AgregarItemPedido(
            pedido_id=self.pedido_id,
            producto_id=self.producto_id,
            cantidad=self.cantidad
        )
        
        with patch.object(self.handler._repositorio, 'obtener_por_id', side_effect=Exception("Error de base de datos")):
            with patch('aplicacion.comandos.agregar_item_pedido.logger') as mock_logger:
                resultado = self.handler.handle(comando)
                
                assert resultado['success'] == False
                assert 'Error interno' in resultado['error']
                assert 'Error de base de datos' in resultado['error']
                mock_logger.error.assert_called_once()

class TestEjecutarAgregarItemPedido:
    """Pruebas para la función ejecutar_agregar_item_pedido"""
    
    def test_ejecutar_comando(self):
        """Test ejecutar comando AgregarItemPedido"""
        pedido_id = str(uuid.uuid4())
        producto_id = str(uuid.uuid4())
        cantidad = 5
        
        comando = AgregarItemPedido(
            pedido_id=pedido_id,
            producto_id=producto_id,
            cantidad=cantidad
        )
        
        with patch('aplicacion.comandos.agregar_item_pedido.AgregarItemPedidoHandler') as mock_handler_class:
            mock_handler = Mock()
            mock_handler_class.return_value = mock_handler
            mock_handler.handle.return_value = {'success': True, 'message': 'Item agregado'}
            
            resultado = ejecutar_agregar_item_pedido(comando)
            
            assert resultado['success'] == True
            assert resultado['message'] == 'Item agregado'
            mock_handler.handle.assert_called_once_with(comando)
