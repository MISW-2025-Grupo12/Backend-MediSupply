import pytest
import uuid
from datetime import datetime, timedelta
from unittest.mock import patch, Mock

# Configurar el path para importar los módulos
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from aplicacion.comandos.crear_pedido import CrearPedido, CrearPedidoHandler
from aplicacion.comandos.crear_visita import CrearVisita, CrearVisitaHandler
from aplicacion.comandos.registrar_visita import RegistrarVisita, RegistrarVisitaHandler

class TestCrearPedido:
    """Pruebas para el comando CrearPedido"""
    
    def test_crear_pedido_comando(self):
        """Test crear comando CrearPedido"""
        vendedor_id = str(uuid.uuid4())
        cliente_id = str(uuid.uuid4())
        
        comando = CrearPedido(
            vendedor_id=vendedor_id,
            cliente_id=cliente_id
        )
        
        assert comando.vendedor_id == vendedor_id
        assert comando.cliente_id == cliente_id
    
    def test_crear_pedido_handler_handle_exitoso(self, app_context):
        """Test manejar comando CrearPedido exitosamente"""
        vendedor_id = str(uuid.uuid4())
        cliente_id = str(uuid.uuid4())
        
        comando = CrearPedido(
            vendedor_id=vendedor_id,
            cliente_id=cliente_id
        )
        
        with patch('src.infraestructura.repositorios.RepositorioPedidoSQLite') as mock_repo:
            mock_pedido = Mock()
            mock_pedido.id = str(uuid.uuid4())
            mock_repo.return_value.crear.return_value = mock_pedido
            
            handler = CrearPedidoHandler()
            resultado = handler.handle(comando)
            
            assert resultado is not None
            assert resultado['success'] == True
            assert resultado['pedido_id'] is not None
    

class TestCrearVisita:
    """Pruebas para el comando CrearVisita"""
    
    def test_crear_visita_comando(self):
        """Test crear comando CrearVisita"""
        vendedor_id = str(uuid.uuid4())
        cliente_id = str(uuid.uuid4())
        fecha_programada = datetime.now() + timedelta(days=1)
        
        comando = CrearVisita(
            vendedor_id=vendedor_id,
            cliente_id=cliente_id,
            fecha_programada=fecha_programada,
            direccion="Calle 123",
            telefono="3001234567",
            estado="pendiente",
            descripcion="Visita de seguimiento"
        )
        
        assert comando.vendedor_id == vendedor_id
        assert comando.cliente_id == cliente_id
        assert comando.fecha_programada == fecha_programada
    
    

class TestRegistrarVisita:
    """Pruebas para el comando RegistrarVisita"""
    
    def test_registrar_visita_comando(self):
        """Test crear comando RegistrarVisita"""
        visita_id = str(uuid.uuid4())
        cliente_id = str(uuid.uuid4())
        fecha_realizada = datetime.now().date()
        hora_realizada = datetime.now().time()
        novedades = "Visita completada"
        
        comando = RegistrarVisita(
            visita_id=visita_id,
            cliente_id=cliente_id,
            fecha_realizada=fecha_realizada.isoformat(),
            hora_realizada=hora_realizada.isoformat(),
            novedades=novedades
        )
        
        assert comando.visita_id == visita_id
        assert comando.cliente_id == cliente_id
        assert comando.fecha_realizada == fecha_realizada.isoformat()
        assert comando.hora_realizada == hora_realizada.isoformat()
        assert comando.novedades == novedades
    
    
