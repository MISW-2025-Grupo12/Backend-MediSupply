import pytest
import uuid
from unittest.mock import Mock, patch

# Configurar el path para importar los módulos
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from aplicacion.consultas.obtener_pedidos import ObtenerPedidos, ObtenerPedidosHandler, ejecutar_obtener_pedidos
from dominio.entidades import Pedido, ItemPedido
from dominio.objetos_valor import EstadoPedido, Cantidad, Precio

class TestObtenerPedidos:
    """Pruebas para la consulta ObtenerPedidos"""
    
    def test_crear_consulta_sin_filtros(self):
        """Test crear consulta sin filtros"""
        consulta = ObtenerPedidos()
        
        assert consulta.vendedor_id is None
        assert consulta.estado is None
    
    def test_crear_consulta_con_filtros(self):
        """Test crear consulta con filtros"""
        vendedor_id = str(uuid.uuid4())
        estado = "borrador"
        
        consulta = ObtenerPedidos(
            vendedor_id=vendedor_id,
            estado=estado
        )
        
        assert consulta.vendedor_id == vendedor_id
        assert consulta.estado == estado

class TestObtenerPedidosHandler:
    """Pruebas para el handler ObtenerPedidosHandler"""
    
    def setup_method(self):
        """Configurar para cada prueba"""
        self.handler = ObtenerPedidosHandler()
        self.vendedor_id = str(uuid.uuid4())
        self.cliente_id = str(uuid.uuid4())
    
    def test_handle_sin_filtros(self):
        """Test manejar consulta sin filtros"""
        consulta = ObtenerPedidos()
        
        # Crear mocks de pedidos
        mock_pedido1 = Mock()
        mock_pedido1.id = uuid.uuid4()
        mock_pedido1.vendedor_id = self.vendedor_id
        mock_pedido1.cliente_id = self.cliente_id
        mock_pedido1.estado.estado = "borrador"
        mock_pedido1.total.valor = 100.0
        mock_pedido1.items = []
        
        mock_pedido2 = Mock()
        mock_pedido2.id = uuid.uuid4()
        mock_pedido2.vendedor_id = str(uuid.uuid4())
        mock_pedido2.cliente_id = str(uuid.uuid4())
        mock_pedido2.estado.estado = "confirmado"
        mock_pedido2.total.valor = 200.0
        mock_pedido2.items = []
        
        pedidos = [mock_pedido1, mock_pedido2]
        
        with patch.object(self.handler._repositorio, 'obtener_todos', return_value=pedidos):
            with patch('aplicacion.consultas.obtener_pedidos.logger') as mock_logger:
                resultado = self.handler.handle(consulta)
                
                assert len(resultado) == 2
                assert resultado[0]['vendedor_id'] == self.vendedor_id
                assert resultado[0]['estado'] == "borrador"
                assert resultado[0]['total'] == 100.0
                assert resultado[1]['estado'] == "confirmado"
                assert resultado[1]['total'] == 200.0
                mock_logger.info.assert_called_once()
    
    def test_handle_con_filtro_vendedor(self):
        """Test manejar consulta con filtro por vendedor"""
        consulta = ObtenerPedidos(vendedor_id=self.vendedor_id)
        
        # Crear mocks de pedidos
        mock_pedido1 = Mock()
        mock_pedido1.id = uuid.uuid4()
        mock_pedido1.vendedor_id = self.vendedor_id
        mock_pedido1.cliente_id = self.cliente_id
        mock_pedido1.estado.estado = "borrador"
        mock_pedido1.total.valor = 100.0
        mock_pedido1.items = []
        
        mock_pedido2 = Mock()
        mock_pedido2.id = uuid.uuid4()
        mock_pedido2.vendedor_id = str(uuid.uuid4())  # Diferente vendedor
        mock_pedido2.cliente_id = str(uuid.uuid4())
        mock_pedido2.estado.estado = "confirmado"
        mock_pedido2.total.valor = 200.0
        mock_pedido2.items = []
        
        pedidos = [mock_pedido1, mock_pedido2]
        
        with patch.object(self.handler._repositorio, 'obtener_todos', return_value=pedidos):
            resultado = self.handler.handle(consulta)
            
            assert len(resultado) == 1
            assert resultado[0]['vendedor_id'] == self.vendedor_id
    
    def test_handle_con_filtro_estado(self):
        """Test manejar consulta con filtro por estado"""
        consulta = ObtenerPedidos(estado="borrador")
        
        # Crear mocks de pedidos
        mock_pedido1 = Mock()
        mock_pedido1.id = uuid.uuid4()
        mock_pedido1.vendedor_id = self.vendedor_id
        mock_pedido1.cliente_id = self.cliente_id
        mock_pedido1.estado.estado = "borrador"
        mock_pedido1.total.valor = 100.0
        mock_pedido1.items = []
        
        mock_pedido2 = Mock()
        mock_pedido2.id = uuid.uuid4()
        mock_pedido2.vendedor_id = str(uuid.uuid4())
        mock_pedido2.cliente_id = str(uuid.uuid4())
        mock_pedido2.estado.estado = "confirmado"
        mock_pedido2.total.valor = 200.0
        mock_pedido2.items = []
        
        pedidos = [mock_pedido1, mock_pedido2]
        
        with patch.object(self.handler._repositorio, 'obtener_todos', return_value=pedidos):
            resultado = self.handler.handle(consulta)
            
            assert len(resultado) == 1
            assert resultado[0]['estado'] == "borrador"
    
    def test_handle_con_ambos_filtros(self):
        """Test manejar consulta con ambos filtros"""
        consulta = ObtenerPedidos(vendedor_id=self.vendedor_id, estado="borrador")
        
        # Crear mocks de pedidos
        mock_pedido1 = Mock()
        mock_pedido1.id = uuid.uuid4()
        mock_pedido1.vendedor_id = self.vendedor_id
        mock_pedido1.cliente_id = self.cliente_id
        mock_pedido1.estado.estado = "borrador"
        mock_pedido1.total.valor = 100.0
        mock_pedido1.items = []
        
        mock_pedido2 = Mock()
        mock_pedido2.id = uuid.uuid4()
        mock_pedido2.vendedor_id = self.vendedor_id
        mock_pedido2.cliente_id = str(uuid.uuid4())
        mock_pedido2.estado.estado = "confirmado"  # Diferente estado
        mock_pedido2.total.valor = 200.0
        mock_pedido2.items = []
        
        pedidos = [mock_pedido1, mock_pedido2]
        
        with patch.object(self.handler._repositorio, 'obtener_todos', return_value=pedidos):
            resultado = self.handler.handle(consulta)
            
            assert len(resultado) == 1
            assert resultado[0]['vendedor_id'] == self.vendedor_id
            assert resultado[0]['estado'] == "borrador"
    
    def test_handle_con_items(self):
        """Test manejar consulta con pedidos que tienen items"""
        consulta = ObtenerPedidos()
        
        # Crear mock de item
        mock_item = Mock()
        mock_item.id = uuid.uuid4()
        mock_item.producto_id = str(uuid.uuid4())
        mock_item.nombre_producto = "Producto Test"
        mock_item.cantidad.valor = 2
        mock_item.precio_unitario.valor = 10.0
        mock_item.calcular_subtotal.return_value = 20.0
        
        # Crear mock de pedido con items
        mock_pedido = Mock()
        mock_pedido.id = uuid.uuid4()
        mock_pedido.vendedor_id = self.vendedor_id
        mock_pedido.cliente_id = self.cliente_id
        mock_pedido.estado.estado = "borrador"
        mock_pedido.total.valor = 20.0
        mock_pedido.items = [mock_item]
        
        pedidos = [mock_pedido]
        
        with patch.object(self.handler._repositorio, 'obtener_todos', return_value=pedidos):
            resultado = self.handler.handle(consulta)
            
            assert len(resultado) == 1
            assert len(resultado[0]['items']) == 1
            assert resultado[0]['items'][0]['producto_id'] == mock_item.producto_id
            assert resultado[0]['items'][0]['nombre_producto'] == "Producto Test"
            assert resultado[0]['items'][0]['cantidad'] == 2
            assert resultado[0]['items'][0]['precio_unitario'] == 10.0
            assert resultado[0]['items'][0]['subtotal'] == 20.0
    
    def test_handle_sin_pedidos(self):
        """Test manejar consulta cuando no hay pedidos"""
        consulta = ObtenerPedidos()
        
        with patch.object(self.handler._repositorio, 'obtener_todos', return_value=[]):
            with patch('aplicacion.consultas.obtener_pedidos.logger') as mock_logger:
                resultado = self.handler.handle(consulta)
                
                assert len(resultado) == 0
                mock_logger.info.assert_called_once_with("Retornando 0 pedidos")
    
    def test_handle_excepcion(self):
        """Test manejar consulta con excepción"""
        consulta = ObtenerPedidos()
        
        with patch.object(self.handler._repositorio, 'obtener_todos', side_effect=Exception("Error de base de datos")):
            with patch('aplicacion.consultas.obtener_pedidos.logger') as mock_logger:
                resultado = self.handler.handle(consulta)
                
                assert resultado == []
                mock_logger.error.assert_called_once()

class TestEjecutarObtenerPedidos:
    """Pruebas para la función ejecutar_obtener_pedidos"""
    
    def test_ejecutar_consulta(self):
        """Test ejecutar consulta ObtenerPedidos"""
        vendedor_id = str(uuid.uuid4())
        estado = "borrador"
        
        consulta = ObtenerPedidos(
            vendedor_id=vendedor_id,
            estado=estado
        )
        
        with patch('aplicacion.consultas.obtener_pedidos.ObtenerPedidosHandler') as mock_handler_class:
            mock_handler = Mock()
            mock_handler_class.return_value = mock_handler
            mock_handler.handle.return_value = [{'id': '123', 'estado': 'borrador'}]
            
            resultado = ejecutar_obtener_pedidos(consulta)
            
            assert len(resultado) == 1
            assert resultado[0]['id'] == '123'
            mock_handler.handle.assert_called_once_with(consulta)
