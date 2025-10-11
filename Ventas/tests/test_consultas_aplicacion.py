import pytest
import uuid
from datetime import datetime, timedelta
from unittest.mock import patch, Mock

# Configurar el path para importar los módulos
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from aplicacion.consultas.obtener_pedido import ObtenerPedido, ObtenerPedidoHandler
from aplicacion.consultas.obtener_pedidos import ObtenerPedidos, ObtenerPedidosHandler
from aplicacion.consultas.obtener_visitas import ObtenerVisitas, ObtenerVisitasHandler
from aplicacion.consultas.obtener_visitas_por_vendedor import ObtenerVisitasPorVendedor, ObtenerVisitasPorVendedorHandler

class TestObtenerPedido:
    """Pruebas para la consulta ObtenerPedido"""
    
    def test_obtener_pedido_consulta(self):
        """Test crear consulta ObtenerPedido"""
        pedido_id = str(uuid.uuid4())
        
        consulta = ObtenerPedido(pedido_id=pedido_id)
        
        assert consulta.pedido_id == pedido_id
    
    
    def test_obtener_pedido_handler_pedido_no_existe(self):
        """Test manejar consulta ObtenerPedido cuando el pedido no existe"""
        pedido_id = str(uuid.uuid4())
        
        consulta = ObtenerPedido(pedido_id=pedido_id)
        
        with patch('src.infraestructura.repositorios.RepositorioPedidoSQLite') as mock_repo:
            mock_repo.return_value.obtener_por_id.return_value = None
            
            handler = ObtenerPedidoHandler()
            resultado = handler.handle(consulta)
            
            assert resultado is None
    

class TestObtenerPedidos:
    """Pruebas para la consulta ObtenerPedidos"""
    
    def test_obtener_pedidos_consulta(self):
        """Test crear consulta ObtenerPedidos"""
        vendedor_id = str(uuid.uuid4())
        estado = "borrador"
        
        consulta = ObtenerPedidos(
            vendedor_id=vendedor_id,
            estado=estado
        )
        
        assert consulta.vendedor_id == vendedor_id
        assert consulta.estado == estado
    
    def test_obtener_pedidos_consulta_sin_filtros(self):
        """Test crear consulta ObtenerPedidos sin filtros"""
        consulta = ObtenerPedidos()
        
        assert consulta.vendedor_id is None
        assert consulta.estado is None
    
    
    def test_obtener_pedidos_handler_sin_resultados(self):
        """Test manejar consulta ObtenerPedidos sin resultados"""
        consulta = ObtenerPedidos()
        
        with patch('src.infraestructura.repositorios.RepositorioPedidoSQLite') as mock_repo:
            mock_repo.return_value.obtener_todos.return_value = []
            
            handler = ObtenerPedidosHandler()
            resultado = handler.handle(consulta)
            
            assert resultado == []
    

class TestObtenerVisitas:
    """Pruebas para la consulta ObtenerVisitas"""
    
    def test_obtener_visitas_consulta(self):
        """Test crear consulta ObtenerVisitas"""
        estado = "pendiente"
        
        consulta = ObtenerVisitas(estado=estado)
        
        assert consulta.estado == estado
    
    def test_obtener_visitas_consulta_sin_filtros(self):
        """Test crear consulta ObtenerVisitas sin filtros"""
        consulta = ObtenerVisitas()
        
        assert consulta.estado is None
    
    
    def test_obtener_visitas_handler_sin_resultados(self, app_context):
        """Test manejar consulta ObtenerVisitas sin resultados"""
        consulta = ObtenerVisitas()
        
        with patch('src.infraestructura.repositorios.RepositorioVisitaSQLite') as mock_repo:
            mock_repo.return_value.obtener_todos.return_value = []
            
            handler = ObtenerVisitasHandler()
            resultado = handler.handle(consulta)
            
            assert resultado == []
    

class TestObtenerVisitasPorVendedor:
    """Pruebas para la consulta ObtenerVisitasPorVendedor"""
    
    def test_obtener_visitas_por_vendedor_consulta(self):
        """Test crear consulta ObtenerVisitasPorVendedor"""
        vendedor_id = str(uuid.uuid4())
        estado = "pendiente"
        
        consulta = ObtenerVisitasPorVendedor(
            vendedor_id=vendedor_id,
            estado=estado
        )
        
        assert consulta.vendedor_id == vendedor_id
        assert consulta.estado == estado
    
    def test_obtener_visitas_por_vendedor_consulta_sin_estado(self):
        """Test crear consulta ObtenerVisitasPorVendedor sin estado"""
        vendedor_id = str(uuid.uuid4())
        
        consulta = ObtenerVisitasPorVendedor(vendedor_id=vendedor_id)
        
        assert consulta.vendedor_id == vendedor_id
        assert consulta.estado is None
    
    
    def test_obtener_visitas_por_vendedor_handler_sin_resultados(self, app_context):
        """Test manejar consulta ObtenerVisitasPorVendedor sin resultados"""
        vendedor_id = str(uuid.uuid4())
        
        consulta = ObtenerVisitasPorVendedor(vendedor_id=vendedor_id)
        
        with patch('src.infraestructura.repositorios.RepositorioVisitaSQLite') as mock_repo:
            mock_repo.return_value.obtener_todos.return_value = []
            
            handler = ObtenerVisitasPorVendedorHandler()
            resultado = handler.handle(consulta)
            
            assert resultado == []
    
