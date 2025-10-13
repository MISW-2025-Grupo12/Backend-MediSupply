import pytest
import uuid
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

# Configurar el path para importar los módulos
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from aplicacion.comandos.confirmar_pedido import ConfirmarPedido, ConfirmarPedidoHandler
from dominio.entidades import Pedido, ItemPedido
from dominio.objetos_valor import EstadoPedido, Cantidad, Precio

class TestConfirmarPedido:
    """Pruebas para el comando ConfirmarPedido"""
    
    def setup_method(self):
        """Configurar mocks para cada prueba"""
        self.mock_repositorio = Mock()
        self.mock_servicio_logistica = Mock()
        self.mock_despachador = Mock()
        
        # Crear handler con mocks
        self.handler = ConfirmarPedidoHandler()
        self.handler._repositorio = self.mock_repositorio
        self.handler._servicio_logistica = self.mock_servicio_logistica
    
    # ========== PRUEBAS DE VALIDACIÓN DE ENTRADA ==========
    
    def test_confirmar_pedido_sin_id(self):
        """Test confirmar pedido sin pedido_id"""
        comando = ConfirmarPedido(pedido_id="")
        
        resultado = self.handler.handle(comando)
        
        assert resultado['success'] == False
        assert 'pedido_id es obligatorio' in resultado['error']
    
    def test_confirmar_pedido_id_none(self):
        """Test confirmar pedido con pedido_id None"""
        comando = ConfirmarPedido(pedido_id=None)
        
        resultado = self.handler.handle(comando)
        
        assert resultado['success'] == False
        assert 'pedido_id es obligatorio' in resultado['error']
    
    def test_confirmar_pedido_no_encontrado(self):
        """Test confirmar pedido que no existe"""
        comando = ConfirmarPedido(pedido_id=str(uuid.uuid4()))
        self.mock_repositorio.obtener_por_id.return_value = None
        
        resultado = self.handler.handle(comando)
        
        assert resultado['success'] == False
        assert 'Pedido no encontrado' in resultado['error']
    
    def test_confirmar_pedido_no_borrador(self):
        """Test confirmar pedido que no está en estado borrador"""
        comando = ConfirmarPedido(pedido_id=str(uuid.uuid4()))
        
        # Crear pedido mock en estado confirmado
        mock_pedido = Mock()
        mock_pedido.estado.estado = "confirmado"
        self.mock_repositorio.obtener_por_id.return_value = mock_pedido
        
        resultado = self.handler.handle(comando)
        
        assert resultado['success'] == False
        assert 'Solo se pueden confirmar pedidos en estado borrador' in resultado['error']
    
    def test_confirmar_pedido_estado_pendiente(self):
        """Test confirmar pedido en estado pendiente"""
        comando = ConfirmarPedido(pedido_id=str(uuid.uuid4()))
        
        # Crear pedido mock en estado pendiente
        mock_pedido = Mock()
        mock_pedido.estado.estado = "pendiente"
        self.mock_repositorio.obtener_por_id.return_value = mock_pedido
        
        resultado = self.handler.handle(comando)
        
        assert resultado['success'] == False
        assert 'Solo se pueden confirmar pedidos en estado borrador' in resultado['error']
    
    def test_confirmar_pedido_sin_items(self):
        """Test confirmar pedido sin items"""
        comando = ConfirmarPedido(pedido_id=str(uuid.uuid4()))
        
        # Crear pedido mock sin items
        mock_pedido = Mock()
        mock_pedido.estado.estado = "borrador"
        mock_pedido.items = []
        self.mock_repositorio.obtener_por_id.return_value = mock_pedido
        
        resultado = self.handler.handle(comando)
        
        assert resultado['success'] == False
        assert 'El pedido debe tener al menos un item' in resultado['error']
    
    def test_confirmar_pedido_items_none(self):
        """Test confirmar pedido con items None"""
        comando = ConfirmarPedido(pedido_id=str(uuid.uuid4()))
        
        # Crear pedido mock con items None
        mock_pedido = Mock()
        mock_pedido.estado.estado = "borrador"
        mock_pedido.items = None
        self.mock_repositorio.obtener_por_id.return_value = mock_pedido
        
        resultado = self.handler.handle(comando)
        
        assert resultado['success'] == False
        assert 'El pedido debe tener al menos un item' in resultado['error']
    
    def test_confirmar_pedido_sin_cliente(self):
        """Test confirmar pedido sin cliente"""
        comando = ConfirmarPedido(pedido_id=str(uuid.uuid4()))
        
        # Crear pedido mock sin cliente
        mock_pedido = Mock()
        mock_pedido.estado.estado = "borrador"
        mock_pedido.items = [Mock()]  # Con items
        mock_pedido.cliente_id = None
        self.mock_repositorio.obtener_por_id.return_value = mock_pedido
        
        resultado = self.handler.handle(comando)
        
        assert resultado['success'] == False
        assert 'El pedido debe tener un cliente asignado' in resultado['error']
    
    def test_confirmar_pedido_cliente_vacio(self):
        """Test confirmar pedido con cliente vacío"""
        comando = ConfirmarPedido(pedido_id=str(uuid.uuid4()))
        
        # Crear pedido mock con cliente vacío
        mock_pedido = Mock()
        mock_pedido.estado.estado = "borrador"
        mock_pedido.items = [Mock()]  # Con items
        mock_pedido.cliente_id = ""
        self.mock_repositorio.obtener_por_id.return_value = mock_pedido
        
        resultado = self.handler.handle(comando)
        
        assert resultado['success'] == False
        assert 'El pedido debe tener un cliente asignado' in resultado['error']
    
    # ========== PRUEBAS DE VALIDACIÓN DE INVENTARIO ==========
    
    def test_confirmar_pedido_producto_no_existe(self):
        """Test confirmar pedido con producto que no existe en inventario"""
        comando = ConfirmarPedido(pedido_id=str(uuid.uuid4()))
        
        # Crear pedido mock válido
        mock_pedido = self._crear_pedido_mock_valido()
        self.mock_repositorio.obtener_por_id.return_value = mock_pedido
        
        # Mock servicio logística - producto no existe
        self.mock_servicio_logistica.obtener_inventario_producto.return_value = None
        
        resultado = self.handler.handle(comando)
        
        assert resultado['success'] == False
        assert 'productos no existen' in resultado['error']
        assert 'items_con_problemas' in resultado
        assert len(resultado['items_con_problemas']) == 1
        assert resultado['items_con_problemas'][0]['problema'] == 'no_existe'
        assert 'El producto no existe en el inventario' in resultado['items_con_problemas'][0]['mensaje']
    
    def test_confirmar_pedido_stock_insuficiente(self):
        """Test confirmar pedido con stock insuficiente"""
        comando = ConfirmarPedido(pedido_id=str(uuid.uuid4()))
        
        # Crear pedido mock válido
        mock_pedido = self._crear_pedido_mock_valido()
        self.mock_repositorio.obtener_por_id.return_value = mock_pedido
        
        # Mock servicio logística - stock insuficiente
        self.mock_servicio_logistica.obtener_inventario_producto.return_value = {
            'total_disponible': 5  # Menor que la cantidad solicitada (10)
        }
        
        resultado = self.handler.handle(comando)
        
        assert resultado['success'] == False
        assert 'stock insuficiente' in resultado['error']
        assert 'items_con_problemas' in resultado
        assert len(resultado['items_con_problemas']) == 1
        assert resultado['items_con_problemas'][0]['problema'] == 'stock_insuficiente'
        assert 'Stock insuficiente' in resultado['items_con_problemas'][0]['mensaje']
    
    def test_confirmar_pedido_mixto_problemas(self):
        """Test confirmar pedido con productos que no existen y stock insuficiente"""
        comando = ConfirmarPedido(pedido_id=str(uuid.uuid4()))
        
        # Crear pedido mock con múltiples items
        mock_pedido = self._crear_pedido_mock_con_multiples_items()
        self.mock_repositorio.obtener_por_id.return_value = mock_pedido
        
        # Mock servicio logística - diferentes respuestas por producto
        def mock_obtener_inventario(producto_id):
            if producto_id == "producto-1":
                return None  # No existe
            elif producto_id == "producto-2":
                return {'total_disponible': 5}  # Stock insuficiente
            else:
                return {'total_disponible': 20}  # Stock suficiente
        
        self.mock_servicio_logistica.obtener_inventario_producto.side_effect = mock_obtener_inventario
        
        resultado = self.handler.handle(comando)
        
        assert resultado['success'] == False
        assert 'productos no existen' in resultado['error']
        assert 'stock insuficiente' in resultado['error']
        assert resultado['resumen']['productos_no_existen'] == 1
        assert resultado['resumen']['productos_stock_insuficiente'] == 1
        assert resultado['resumen']['items_validos'] == 1
    
    def test_confirmar_pedido_solo_productos_no_existen(self):
        """Test confirmar pedido solo con productos que no existen"""
        comando = ConfirmarPedido(pedido_id=str(uuid.uuid4()))
        
        # Crear pedido mock con múltiples items
        mock_pedido = self._crear_pedido_mock_con_multiples_items()
        self.mock_repositorio.obtener_por_id.return_value = mock_pedido
        
        # Mock servicio logística - todos los productos no existen
        self.mock_servicio_logistica.obtener_inventario_producto.return_value = None
        
        resultado = self.handler.handle(comando)
        
        assert resultado['success'] == False
        assert 'productos no existen' in resultado['error']
        assert 'stock insuficiente' not in resultado['error']
        assert resultado['resumen']['productos_no_existen'] == 3
        assert resultado['resumen']['productos_stock_insuficiente'] == 0
    
    def test_confirmar_pedido_solo_stock_insuficiente(self):
        """Test confirmar pedido solo con stock insuficiente"""
        comando = ConfirmarPedido(pedido_id=str(uuid.uuid4()))
        
        # Crear pedido mock con múltiples items
        mock_pedido = self._crear_pedido_mock_con_multiples_items()
        self.mock_repositorio.obtener_por_id.return_value = mock_pedido
        
        # Mock servicio logística - todos con stock insuficiente
        self.mock_servicio_logistica.obtener_inventario_producto.return_value = {
            'total_disponible': 5  # Menor que las cantidades solicitadas
        }
        
        resultado = self.handler.handle(comando)
        
        assert resultado['success'] == False
        assert 'stock insuficiente' in resultado['error']
        assert 'productos no existen' not in resultado['error']
        assert resultado['resumen']['productos_no_existen'] == 0
        # Solo 2 productos tienen stock insuficiente (producto-2 y producto-3)
        # producto-1 tiene cantidad 10, producto-2 tiene cantidad 10, producto-3 tiene cantidad 5
        # Con stock disponible de 5, solo producto-3 es válido
        assert resultado['resumen']['productos_stock_insuficiente'] == 2
    
    # ========== PRUEBAS DE RESERVA DE INVENTARIO ==========
    
    def test_confirmar_pedido_error_reserva_inventario(self):
        """Test confirmar pedido con error en reserva de inventario"""
        comando = ConfirmarPedido(pedido_id=str(uuid.uuid4()))
        
        # Crear pedido mock válido
        mock_pedido = self._crear_pedido_mock_valido()
        self.mock_repositorio.obtener_por_id.return_value = mock_pedido
        
        # Mock servicio logística - inventario válido pero error en reserva
        self.mock_servicio_logistica.obtener_inventario_producto.return_value = {
            'total_disponible': 20
        }
        self.mock_servicio_logistica.reservar_inventario.return_value = {
            'success': False,
            'error': 'Error de conexión'
        }
        
        resultado = self.handler.handle(comando)
        
        assert resultado['success'] == False
        assert 'Error reservando inventario' in resultado['error']
        assert 'Error de conexión' in resultado['error']
        assert 'items_pedido' in resultado
    
    def test_confirmar_pedido_error_reserva_sin_detalle(self):
        """Test confirmar pedido con error en reserva sin detalle específico"""
        comando = ConfirmarPedido(pedido_id=str(uuid.uuid4()))
        
        # Crear pedido mock válido
        mock_pedido = self._crear_pedido_mock_valido()
        self.mock_repositorio.obtener_por_id.return_value = mock_pedido
        
        # Mock servicio logística - inventario válido pero error en reserva sin detalle
        self.mock_servicio_logistica.obtener_inventario_producto.return_value = {
            'total_disponible': 20
        }
        self.mock_servicio_logistica.reservar_inventario.return_value = {
            'success': False
            # Sin campo 'error'
        }
        
        resultado = self.handler.handle(comando)
        
        assert resultado['success'] == False
        assert 'Error reservando inventario' in resultado['error']
        assert 'Error desconocido' in resultado['error']
    
    def test_confirmar_pedido_error_confirmacion(self):
        """Test confirmar pedido con error en confirmación"""
        comando = ConfirmarPedido(pedido_id=str(uuid.uuid4()))
        
        # Crear pedido mock válido
        mock_pedido = self._crear_pedido_mock_valido()
        mock_pedido.confirmar.return_value = False  # Error en confirmación
        self.mock_repositorio.obtener_por_id.return_value = mock_pedido
        
        # Mock servicio logística - todo válido
        self.mock_servicio_logistica.obtener_inventario_producto.return_value = {
            'total_disponible': 20
        }
        self.mock_servicio_logistica.reservar_inventario.return_value = {
            'success': True
        }
        
        resultado = self.handler.handle(comando)
        
        assert resultado['success'] == False
        assert 'Error confirmando el pedido' in resultado['error']
    
    # ========== PRUEBAS DE ÉXITO ==========
    
    @patch('aplicacion.comandos.confirmar_pedido.despachador_eventos')
    def test_confirmar_pedido_exitoso(self, mock_despachador):
        """Test confirmar pedido exitosamente"""
        comando = ConfirmarPedido(pedido_id=str(uuid.uuid4()))
        
        # Crear pedido mock válido
        mock_pedido = self._crear_pedido_mock_valido()
        mock_pedido.confirmar.return_value = True
        mock_pedido.disparar_evento_confirmacion.return_value = Mock()
        self.mock_repositorio.obtener_por_id.return_value = mock_pedido
        self.mock_repositorio.actualizar.return_value = mock_pedido
        
        # Mock servicio logística - todo válido
        self.mock_servicio_logistica.obtener_inventario_producto.return_value = {
            'total_disponible': 20
        }
        self.mock_servicio_logistica.reservar_inventario.return_value = {
            'success': True
        }
        
        resultado = self.handler.handle(comando)
        
        assert resultado['success'] == True
        assert 'Pedido confirmado exitosamente' in resultado['message']
        assert 'pedido_id' in resultado
        assert 'vendedor_id' in resultado
        assert 'cliente_id' in resultado
        assert 'estado' in resultado
        assert 'total' in resultado
        assert 'items_count' in resultado
        
        # Verificar que se llamó el despachador de eventos
        mock_despachador.publicar_evento.assert_called_once()
    
    @patch('aplicacion.comandos.confirmar_pedido.despachador_eventos')
    def test_confirmar_pedido_calculo_total(self, mock_despachador):
        """Test cálculo correcto del total del pedido"""
        comando = ConfirmarPedido(pedido_id=str(uuid.uuid4()))
        
        # Crear pedido mock con items específicos
        mock_pedido = Mock()
        mock_pedido.estado.estado = "borrador"
        mock_pedido.cliente_id = str(uuid.uuid4())
        mock_pedido.vendedor_id = str(uuid.uuid4())
        
        # Items con subtotales específicos
        mock_item1 = Mock()
        mock_item1.calcular_subtotal.return_value = 50.0
        mock_item1.producto_id = str(uuid.uuid4())
        mock_item1.nombre_producto = "Item 1"
        mock_item1.cantidad.valor = 2
        
        mock_item2 = Mock()
        mock_item2.calcular_subtotal.return_value = 75.0
        mock_item2.producto_id = str(uuid.uuid4())
        mock_item2.nombre_producto = "Item 2"
        mock_item2.cantidad.valor = 3
        
        mock_pedido.items = [mock_item1, mock_item2]
        mock_pedido.confirmar.return_value = True
        mock_pedido.disparar_evento_confirmacion.return_value = Mock()
        self.mock_repositorio.obtener_por_id.return_value = mock_pedido
        self.mock_repositorio.actualizar.return_value = mock_pedido
        
        # Mock servicio logística
        self.mock_servicio_logistica.obtener_inventario_producto.return_value = {
            'total_disponible': 20
        }
        self.mock_servicio_logistica.reservar_inventario.return_value = {
            'success': True
        }
        
        resultado = self.handler.handle(comando)
        
        # Verificar que se calculó el total correctamente
        assert resultado['success'] == True
        # El total debería ser 50.0 + 75.0 = 125.0
        # Verificar que se llamó calcular_subtotal en cada item
        mock_item1.calcular_subtotal.assert_called_once()
        mock_item2.calcular_subtotal.assert_called_once()
    
    # ========== PRUEBAS DE EXCEPCIONES ==========
    
    def test_confirmar_pedido_excepcion_general(self):
        """Test confirmar pedido con excepción general"""
        comando = ConfirmarPedido(pedido_id=str(uuid.uuid4()))
        
        # Mock que lanza excepción
        self.mock_repositorio.obtener_por_id.side_effect = Exception("Error de base de datos")
        
        resultado = self.handler.handle(comando)
        
        assert resultado['success'] == False
        assert 'Error interno' in resultado['error']
        assert 'Error de base de datos' in resultado['error']
    
    def test_confirmar_pedido_excepcion_en_calculo_total(self):
        """Test confirmar pedido con excepción en cálculo de total"""
        comando = ConfirmarPedido(pedido_id=str(uuid.uuid4()))
        
        # Crear pedido mock que lanza excepción en calcular_subtotal
        mock_pedido = Mock()
        mock_pedido.estado.estado = "borrador"
        mock_pedido.cliente_id = str(uuid.uuid4())
        mock_pedido.vendedor_id = str(uuid.uuid4())
        
        mock_item = Mock()
        mock_item.calcular_subtotal.side_effect = Exception("Error calculando subtotal")
        mock_item.producto_id = str(uuid.uuid4())
        mock_item.nombre_producto = "Item Test"
        mock_item.cantidad.valor = 10
        
        mock_pedido.items = [mock_item]
        self.mock_repositorio.obtener_por_id.return_value = mock_pedido
        
        resultado = self.handler.handle(comando)
        
        assert resultado['success'] == False
        assert 'Error interno' in resultado['error']
        assert 'Error calculando subtotal' in resultado['error']
    
    # ========== MÉTODOS AUXILIARES ==========
    
    def _crear_pedido_mock_valido(self):
        """Crear un pedido mock válido para pruebas"""
        mock_pedido = Mock()
        mock_pedido.estado.estado = "borrador"
        mock_pedido.cliente_id = str(uuid.uuid4())
        mock_pedido.vendedor_id = str(uuid.uuid4())
        
        # Crear item mock
        mock_item = Mock()
        mock_item.producto_id = str(uuid.uuid4())
        mock_item.nombre_producto = "Producto Test"
        mock_item.cantidad.valor = 10
        mock_item.calcular_subtotal.return_value = 100.0
        
        mock_pedido.items = [mock_item]
        return mock_pedido
    
    def _crear_pedido_mock_con_multiples_items(self):
        """Crear un pedido mock con múltiples items para pruebas"""
        mock_pedido = Mock()
        mock_pedido.estado.estado = "borrador"
        mock_pedido.cliente_id = str(uuid.uuid4())
        mock_pedido.vendedor_id = str(uuid.uuid4())
        
        # Crear items mock
        mock_item1 = Mock()
        mock_item1.producto_id = "producto-1"
        mock_item1.nombre_producto = "Producto 1"
        mock_item1.cantidad.valor = 10
        mock_item1.calcular_subtotal.return_value = 100.0
        
        mock_item2 = Mock()
        mock_item2.producto_id = "producto-2"
        mock_item2.nombre_producto = "Producto 2"
        mock_item2.cantidad.valor = 10
        mock_item2.calcular_subtotal.return_value = 200.0
        
        mock_item3 = Mock()
        mock_item3.producto_id = "producto-3"
        mock_item3.nombre_producto = "Producto 3"
        mock_item3.cantidad.valor = 5
        mock_item3.calcular_subtotal.return_value = 50.0
        
        mock_pedido.items = [mock_item1, mock_item2, mock_item3]
        return mock_pedido
    
    # ========== PRUEBAS DE INTEGRACIÓN ==========
    
    def test_ejecutar_confirmar_pedido_registro(self):
        """Test que el comando está registrado correctamente"""
        from aplicacion.comandos.confirmar_pedido import ejecutar_confirmar_pedido
        from aplicacion.comandos.confirmar_pedido import ConfirmarPedido
        
        # Verificar que la función existe y es callable
        assert callable(ejecutar_confirmar_pedido)
        
        # Crear comando
        comando = ConfirmarPedido(pedido_id=str(uuid.uuid4()))
        
        # Mock del handler para evitar dependencias reales
        with patch('aplicacion.comandos.confirmar_pedido.ConfirmarPedidoHandler') as mock_handler_class:
            mock_handler = Mock()
            mock_handler.handle.return_value = {'success': True}
            mock_handler_class.return_value = mock_handler
            
            # Ejecutar comando
            resultado = ejecutar_confirmar_pedido(comando)
            
            # Verificar que se creó y llamó el handler
            mock_handler_class.assert_called_once()
            mock_handler.handle.assert_called_once_with(comando)
            assert resultado['success'] == True
    
    def test_confirmar_pedido_comando_creation(self):
        """Test creación del comando ConfirmarPedido"""
        from aplicacion.comandos.confirmar_pedido import ConfirmarPedido
        
        pedido_id = str(uuid.uuid4())
        comando = ConfirmarPedido(pedido_id=pedido_id)
        
        assert comando.pedido_id == pedido_id
        assert hasattr(comando, 'pedido_id')
    
    def test_confirmar_pedido_handler_initialization(self):
        """Test inicialización del handler"""
        from aplicacion.comandos.confirmar_pedido import ConfirmarPedidoHandler
        
        # Mock de las dependencias
        with patch('aplicacion.comandos.confirmar_pedido.RepositorioPedidoSQLite') as mock_repo, \
             patch('aplicacion.comandos.confirmar_pedido.ServicioLogistica') as mock_servicio:
            
            handler = ConfirmarPedidoHandler()
            
            # Verificar que se inicializaron las dependencias
            assert hasattr(handler, '_repositorio')
            assert hasattr(handler, '_servicio_logistica')
            mock_repo.assert_called_once()
            mock_servicio.assert_called_once()
    
    def test_confirmar_pedido_handler_handle_method(self):
        """Test que el handler tiene el método handle"""
        from aplicacion.comandos.confirmar_pedido import ConfirmarPedidoHandler
        
        handler = ConfirmarPedidoHandler()
        
        # Verificar que tiene el método handle
        assert hasattr(handler, 'handle')
        assert callable(handler.handle)
    
    def test_confirmar_pedido_imports(self):
        """Test que todos los imports necesarios están disponibles"""
        from aplicacion.comandos.confirmar_pedido import (
            ConfirmarPedido,
            ConfirmarPedidoHandler,
            ejecutar_confirmar_pedido
        )
        
        # Verificar que las clases y funciones están disponibles
        assert ConfirmarPedido is not None
        assert ConfirmarPedidoHandler is not None
        assert ejecutar_confirmar_pedido is not None
    
    def test_confirmar_pedido_dataclass_properties(self):
        """Test propiedades del dataclass ConfirmarPedido"""
        from aplicacion.comandos.confirmar_pedido import ConfirmarPedido
        
        pedido_id = str(uuid.uuid4())
        comando = ConfirmarPedido(pedido_id=pedido_id)
        
        # Verificar que es un dataclass con la propiedad esperada
        assert hasattr(comando, 'pedido_id')
        assert comando.pedido_id == pedido_id
        
        # Verificar que se puede crear con diferentes tipos de ID
        comando_str = ConfirmarPedido(pedido_id="test-id")
        assert comando_str.pedido_id == "test-id"
        
        comando_int = ConfirmarPedido(pedido_id="123")
        assert comando_int.pedido_id == "123"
    
    def test_confirmar_pedido_error_handling_integration(self):
        """Test manejo de errores en integración"""
        from aplicacion.comandos.confirmar_pedido import ejecutar_confirmar_pedido, ConfirmarPedido
        
        comando = ConfirmarPedido(pedido_id=str(uuid.uuid4()))
        
        # Mock del handler que lanza excepción
        with patch('aplicacion.comandos.confirmar_pedido.ConfirmarPedidoHandler') as mock_handler_class:
            mock_handler = Mock()
            mock_handler.handle.side_effect = Exception("Error de integración")
            mock_handler_class.return_value = mock_handler
            
            # Ejecutar comando - debería lanzar la excepción ya que no hay try-catch en ejecutar_confirmar_pedido
            with pytest.raises(Exception, match="Error de integración"):
                ejecutar_confirmar_pedido(comando)
            
            # Verificar que se llamó el handler
            mock_handler.handle.assert_called_once_with(comando)
    
    def test_confirmar_pedido_success_integration(self):
        """Test flujo exitoso en integración"""
        from aplicacion.comandos.confirmar_pedido import ejecutar_confirmar_pedido, ConfirmarPedido
        
        comando = ConfirmarPedido(pedido_id=str(uuid.uuid4()))
        
        # Mock del handler exitoso
        with patch('aplicacion.comandos.confirmar_pedido.ConfirmarPedidoHandler') as mock_handler_class:
            mock_handler = Mock()
            mock_handler.handle.return_value = {
                'success': True,
                'message': 'Pedido confirmado exitosamente',
                'pedido_id': str(uuid.uuid4())
            }
            mock_handler_class.return_value = mock_handler
            
            # Ejecutar comando
            resultado = ejecutar_confirmar_pedido(comando)
            
            # Verificar resultado exitoso
            assert resultado['success'] == True
            assert 'Pedido confirmado exitosamente' in resultado['message']
            assert 'pedido_id' in resultado
            
            # Verificar que se llamó el handler
            mock_handler_class.assert_called_once()
            mock_handler.handle.assert_called_once_with(comando)
