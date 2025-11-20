import pytest
import sys
import os
from unittest.mock import Mock, patch
from datetime import datetime, timedelta
import uuid
from flask import Flask

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from aplicacion.consultas.obtener_informe_ventas_por_vendedor import ObtenerInformeVentasPorVendedor, ObtenerInformeVentasPorVendedorHandler
from dominio.entidades import Pedido, ItemPedido
from dominio.objetos_valor import EstadoPedido, Cantidad, Precio
from config.db import db


class TestObtenerInformeVentasPorVendedor:
    
    def setup_method(self):
        self.handler = ObtenerInformeVentasPorVendedorHandler()
        self.vendedor_id = str(uuid.uuid4())
        self.vendedor_id_2 = str(uuid.uuid4())
        self.cliente_id_1 = str(uuid.uuid4())
        self.cliente_id_2 = str(uuid.uuid4())
        self.app = Flask(__name__)
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        db.init_app(self.app)
    
    def test_crear_consulta_sin_filtros(self):
        consulta = ObtenerInformeVentasPorVendedor()
        
        assert consulta.fecha_inicio is None
        assert consulta.fecha_fin is None
    
    def test_crear_consulta_con_filtros(self):
        fecha_inicio = "2025-01-01T00:00:00"
        fecha_fin = "2025-01-31T23:59:59"
        
        consulta = ObtenerInformeVentasPorVendedor(
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin
        )
        
        assert consulta.fecha_inicio == fecha_inicio
        assert consulta.fecha_fin == fecha_fin
    
    def test_handler_sin_resultados(self):
        consulta = ObtenerInformeVentasPorVendedor()
        
        mock_repo = Mock()
        mock_repo.obtener_pedidos_confirmados.return_value = []
        
        handler = ObtenerInformeVentasPorVendedorHandler()
        handler._repositorio = mock_repo
        
        resultado = handler.handle(consulta)
        
        assert resultado == []
        mock_repo.obtener_pedidos_confirmados.assert_called_once_with(
            fecha_inicio=None,
            fecha_fin=None
        )
    
    def test_handler_con_resultados_exitoso(self):
        consulta = ObtenerInformeVentasPorVendedor()
        
        pedido1 = Pedido(
            id=uuid.uuid4(),
            vendedor_id=self.vendedor_id,
            cliente_id=self.cliente_id_1,
            items=[
                ItemPedido(
                    id=uuid.uuid4(),
                    producto_id=str(uuid.uuid4()),
                    nombre_producto="Producto 1",
                    cantidad=Cantidad(5),
                    precio_unitario=Precio(10000.0)
                )
            ],
            estado=EstadoPedido("entregado"),
            total=Precio(50000.0)
        )
        pedido1._updated_at_model = datetime.now()
        
        pedido2 = Pedido(
            id=uuid.uuid4(),
            vendedor_id=self.vendedor_id,
            cliente_id=self.cliente_id_2,
            items=[
                ItemPedido(
                    id=uuid.uuid4(),
                    producto_id=str(uuid.uuid4()),
                    nombre_producto="Producto 2",
                    cantidad=Cantidad(3),
                    precio_unitario=Precio(20000.0)
                )
            ],
            estado=EstadoPedido("entregado"),
            total=Precio(60000.0)
        )
        pedido2._updated_at_model = datetime.now()
        
        pedido3 = Pedido(
            id=uuid.uuid4(),
            vendedor_id=self.vendedor_id,
            cliente_id=self.cliente_id_1,
            items=[
                ItemPedido(
                    id=uuid.uuid4(),
                    producto_id=str(uuid.uuid4()),
                    nombre_producto="Producto 3",
                    cantidad=Cantidad(2),
                    precio_unitario=Precio(15000.0)
                )
            ],
            estado=EstadoPedido("entregado"),
            total=Precio(30000.0)
        )
        pedido3._updated_at_model = datetime.now()
        
        vendedor_mock = {
            'id': self.vendedor_id,
            'nombre': 'Juan Pérez',
            'email': 'juan.perez@empresa.com',
            'telefono': '3001234567',
            'direccion': 'Calle 123'
        }
        
        mock_repo = Mock()
        mock_servicio = Mock()
        
        mock_repo.obtener_pedidos_confirmados.return_value = [pedido1, pedido2, pedido3]
        mock_servicio.obtener_vendedor_por_id.return_value = vendedor_mock
        
        handler = ObtenerInformeVentasPorVendedorHandler()
        handler._repositorio = mock_repo
        handler._servicio_usuarios = mock_servicio
        
        resultado = handler.handle(consulta)
        
        assert len(resultado) == 1
        assert resultado[0]["vendedor_id"] == self.vendedor_id
        assert resultado[0]["vendedor_nombre"] == "Juan Pérez"
        assert resultado[0]["numero_pedidos"] == 3
        assert resultado[0]["total_ventas"] == 140000.0
        assert resultado[0]["clientes_atendidos"] == 2
    
    def test_handler_agrupa_por_vendedor(self):
        consulta = ObtenerInformeVentasPorVendedor()
        
        pedido1 = Pedido(
            id=uuid.uuid4(),
            vendedor_id=self.vendedor_id,
            cliente_id=self.cliente_id_1,
            items=[],
            estado=EstadoPedido("entregado"),
            total=Precio(50000.0)
        )
        pedido1._updated_at_model = datetime.now()
        
        pedido2 = Pedido(
            id=uuid.uuid4(),
            vendedor_id=self.vendedor_id_2,
            cliente_id=self.cliente_id_2,
            items=[],
            estado=EstadoPedido("entregado"),
            total=Precio(30000.0)
        )
        pedido2._updated_at_model = datetime.now()
        
        vendedor1_mock = {
            'id': self.vendedor_id,
            'nombre': 'Juan Pérez'
        }
        
        vendedor2_mock = {
            'id': self.vendedor_id_2,
            'nombre': 'María García'
        }
        
        mock_repo = Mock()
        mock_servicio = Mock()
        
        mock_repo.obtener_pedidos_confirmados.return_value = [pedido1, pedido2]
        mock_servicio.obtener_vendedor_por_id.side_effect = [vendedor1_mock, vendedor2_mock]
        
        handler = ObtenerInformeVentasPorVendedorHandler()
        handler._repositorio = mock_repo
        handler._servicio_usuarios = mock_servicio
        
        resultado = handler.handle(consulta)
        
        assert len(resultado) == 2
        assert resultado[0]["vendedor_id"] == self.vendedor_id
        assert resultado[1]["vendedor_id"] == self.vendedor_id_2
    
    def test_handler_ignora_pedidos_sin_vendedor(self):
        consulta = ObtenerInformeVentasPorVendedor()
        
        pedido_con_vendedor = Pedido(
            id=uuid.uuid4(),
            vendedor_id=self.vendedor_id,
            cliente_id=self.cliente_id_1,
            items=[],
            estado=EstadoPedido("entregado"),
            total=Precio(50000.0)
        )
        pedido_con_vendedor._updated_at_model = datetime.now()
        
        pedido_sin_vendedor = Pedido(
            id=uuid.uuid4(),
            vendedor_id="",
            cliente_id=self.cliente_id_2,
            items=[],
            estado=EstadoPedido("entregado"),
            total=Precio(30000.0)
        )
        pedido_sin_vendedor._updated_at_model = datetime.now()
        
        vendedor_mock = {
            'id': self.vendedor_id,
            'nombre': 'Juan Pérez'
        }
        
        mock_repo = Mock()
        mock_servicio = Mock()
        
        mock_repo.obtener_pedidos_confirmados.return_value = [pedido_con_vendedor, pedido_sin_vendedor]
        mock_servicio.obtener_vendedor_por_id.return_value = vendedor_mock
        
        handler = ObtenerInformeVentasPorVendedorHandler()
        handler._repositorio = mock_repo
        handler._servicio_usuarios = mock_servicio
        
        resultado = handler.handle(consulta)
        
        assert len(resultado) == 1
        assert resultado[0]["vendedor_id"] == self.vendedor_id
        assert resultado[0]["numero_pedidos"] == 1
    
    def test_handler_vendedor_no_encontrado(self):
        consulta = ObtenerInformeVentasPorVendedor()
        
        pedido = Pedido(
            id=uuid.uuid4(),
            vendedor_id=self.vendedor_id,
            cliente_id=self.cliente_id_1,
            items=[],
            estado=EstadoPedido("entregado"),
            total=Precio(50000.0)
        )
        pedido._updated_at_model = datetime.now()
        
        mock_repo = Mock()
        mock_servicio = Mock()
        
        mock_repo.obtener_pedidos_confirmados.return_value = [pedido]
        mock_servicio.obtener_vendedor_por_id.return_value = None
        
        handler = ObtenerInformeVentasPorVendedorHandler()
        handler._repositorio = mock_repo
        handler._servicio_usuarios = mock_servicio
        
        resultado = handler.handle(consulta)
        
        assert len(resultado) == 1
        assert resultado[0]["vendedor_nombre"] == "Vendedor desconocido"
    
    def test_handler_con_filtro_fecha(self):
        fecha_inicio = "2025-01-01T00:00:00"
        fecha_fin = "2025-01-31T23:59:59"
        consulta = ObtenerInformeVentasPorVendedor(
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin
        )
        
        mock_repo = Mock()
        mock_repo.obtener_pedidos_confirmados.return_value = []
        
        handler = ObtenerInformeVentasPorVendedorHandler()
        handler._repositorio = mock_repo
        
        handler.handle(consulta)
        
        mock_repo.obtener_pedidos_confirmados.assert_called_once_with(
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin
        )
    
    def test_handler_manejo_errores(self):
        consulta = ObtenerInformeVentasPorVendedor()
        
        mock_repo = Mock()
        mock_repo.obtener_pedidos_confirmados.side_effect = Exception("Error en repositorio")
        
        handler = ObtenerInformeVentasPorVendedorHandler()
        handler._repositorio = mock_repo
        
        resultado = handler.handle(consulta)
        
        assert resultado == []

