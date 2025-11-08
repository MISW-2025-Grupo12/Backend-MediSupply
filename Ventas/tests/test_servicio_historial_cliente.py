"""Tests para el servicio de historial de cliente"""
import pytest
import uuid
import sys
import os
from unittest.mock import Mock, patch
from datetime import datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from aplicacion.servicios.servicio_historial_cliente import ServicioHistorialCliente
from dominio.objetos_valor import EstadoPedido, Cantidad, Precio


class TestServicioHistorialCliente:
    """Tests para el servicio de historial de cliente"""
    
    def setup_method(self):
        """Configuración antes de cada test"""
        self.servicio = ServicioHistorialCliente()
        self.cliente_id = str(uuid.uuid4())
    
    def crear_mock_pedido(self, pedido_id, cliente_id, estado, total, items, fecha_creacion=None):
        """Helper para crear un mock de pedido"""
        mock_pedido = Mock()
        mock_pedido.id = pedido_id
        mock_pedido.cliente_id = cliente_id
        mock_pedido.estado = EstadoPedido(estado)
        mock_pedido.total = Precio(total)
        mock_pedido.items = items
        mock_pedido._created_at_model = fecha_creacion or datetime.now()
        return mock_pedido
    
    def crear_mock_item(self, producto_id, nombre, cantidad, precio_unitario):
        """Helper para crear un mock de item"""
        mock_item = Mock()
        mock_item.producto_id = producto_id
        mock_item.nombre_producto = nombre
        mock_item.cantidad = Cantidad(cantidad)
        mock_item.precio_unitario = Precio(precio_unitario)
        return mock_item
    
    def test_obtener_historial_sin_pedidos(self):
        """Test obtener historial de cliente sin pedidos"""
        mock_repositorio = Mock()
        mock_repositorio.obtener_todos.return_value = []
        servicio = ServicioHistorialCliente(repositorio_pedidos=mock_repositorio)
        
        resultado = servicio.obtener_historial_cliente(self.cliente_id)
        
        assert resultado['total_pedidos'] == 0
        assert resultado['ultimos_pedidos'] == []
        assert resultado['productos_mas_comprados'] == []
        assert resultado['frecuencia_compra'] == 'Sin compras anteriores'
    
    def test_obtener_historial_con_un_pedido(self):
        """Test obtener historial de cliente con un pedido"""
        mock_repositorio = Mock()
        
        item1 = self.crear_mock_item('prod1', 'Producto 1', 2, 10.0)
        pedido1 = self.crear_mock_pedido(
            uuid.uuid4(), self.cliente_id, 'confirmado', 20.0, [item1]
        )
        
        mock_repositorio.obtener_todos.return_value = [pedido1]
        servicio = ServicioHistorialCliente(repositorio_pedidos=mock_repositorio)
        
        resultado = servicio.obtener_historial_cliente(self.cliente_id)
        
        assert resultado['total_pedidos'] == 1
        assert len(resultado['ultimos_pedidos']) == 1
        assert resultado['frecuencia_compra'] == 'Cliente con una sola compra'
        assert len(resultado['productos_mas_comprados']) == 1
        assert resultado['productos_mas_comprados'][0]['nombre'] == 'Producto 1'
    
    def test_obtener_historial_con_multiples_pedidos(self):
        """Test obtener historial con múltiples pedidos"""
        mock_repositorio = Mock()
        
        fecha1 = datetime.now() - timedelta(days=30)
        fecha2 = datetime.now() - timedelta(days=15)
        fecha3 = datetime.now()
        
        item1 = self.crear_mock_item('prod1', 'Producto 1', 2, 10.0)
        item2 = self.crear_mock_item('prod2', 'Producto 2', 3, 15.0)
        item3 = self.crear_mock_item('prod1', 'Producto 1', 1, 10.0)
        
        pedido1 = self.crear_mock_pedido(
            uuid.uuid4(), self.cliente_id, 'confirmado', 20.0, [item1], fecha1
        )
        pedido2 = self.crear_mock_pedido(
            uuid.uuid4(), self.cliente_id, 'confirmado', 45.0, [item2], fecha2
        )
        pedido3 = self.crear_mock_pedido(
            uuid.uuid4(), self.cliente_id, 'confirmado', 10.0, [item3], fecha3
        )
        
        mock_repositorio.obtener_todos.return_value = [pedido1, pedido2, pedido3]
        servicio = ServicioHistorialCliente(repositorio_pedidos=mock_repositorio)
        
        resultado = servicio.obtener_historial_cliente(self.cliente_id)
        
        assert resultado['total_pedidos'] == 3
        assert len(resultado['ultimos_pedidos']) == 3
        # Verificar que está ordenado por fecha (más reciente primero)
        assert resultado['ultimos_pedidos'][0]['fecha'] == fecha3.isoformat()
        
        # Verificar productos más comprados
        productos = resultado['productos_mas_comprados']
        assert len(productos) == 2
        # Producto 1 debería tener más cantidad total (2 + 1 = 3)
        assert productos[0]['nombre'] == 'Producto 1'
        assert productos[0]['cantidad_total'] == 3
        assert productos[0]['veces_comprado'] == 2
    
    def test_obtener_historial_filtrado_por_cliente(self):
        """Test que solo se obtienen pedidos del cliente correcto"""
        mock_repositorio = Mock()
        
        otro_cliente_id = str(uuid.uuid4())
        item1 = self.crear_mock_item('prod1', 'Producto 1', 2, 10.0)
        pedido_cliente = self.crear_mock_pedido(
            uuid.uuid4(), self.cliente_id, 'confirmado', 20.0, [item1]
        )
        pedido_otro = self.crear_mock_pedido(
            uuid.uuid4(), otro_cliente_id, 'confirmado', 30.0, [item1]
        )
        
        mock_repositorio.obtener_todos.return_value = [pedido_cliente, pedido_otro]
        servicio = ServicioHistorialCliente(repositorio_pedidos=mock_repositorio)
        
        resultado = servicio.obtener_historial_cliente(self.cliente_id)
        
        assert resultado['total_pedidos'] == 1
        assert resultado['ultimos_pedidos'][0]['id'] == str(pedido_cliente.id)
    
    def test_obtener_historial_con_limite(self):
        """Test obtener historial con límite de pedidos"""
        mock_repositorio = Mock()
        
        pedidos = []
        for i in range(15):
            item = self.crear_mock_item(f'prod{i}', f'Producto {i}', 1, 10.0)
            fecha = datetime.now() - timedelta(days=i)
            pedido = self.crear_mock_pedido(
                uuid.uuid4(), self.cliente_id, 'confirmado', 10.0, [item], fecha
            )
            pedidos.append(pedido)
        
        mock_repositorio.obtener_todos.return_value = pedidos
        servicio = ServicioHistorialCliente(repositorio_pedidos=mock_repositorio)
        
        resultado = servicio.obtener_historial_cliente(self.cliente_id, limite=5)
        
        assert resultado['total_pedidos'] == 15
        assert len(resultado['ultimos_pedidos']) == 5
    
    def test_calcular_frecuencia_compra_frecuente(self):
        """Test calcular frecuencia de compra frecuente"""
        mock_repositorio = Mock()
        
        fecha_inicio = datetime.now() - timedelta(days=30)
        pedidos = []
        for i in range(5):  # 5 pedidos en 30 días = frecuente
            fecha = fecha_inicio + timedelta(days=i*7)
            item = self.crear_mock_item('prod1', 'Producto 1', 1, 10.0)
            pedido = self.crear_mock_pedido(
                uuid.uuid4(), self.cliente_id, 'confirmado', 10.0, [item], fecha
            )
            pedidos.append(pedido)
        
        mock_repositorio.obtener_todos.return_value = pedidos
        servicio = ServicioHistorialCliente(repositorio_pedidos=mock_repositorio)
        
        resultado = servicio.obtener_historial_cliente(self.cliente_id)
        
        assert 'frecuente' in resultado['frecuencia_compra'].lower()
    
    def test_calcular_frecuencia_compra_regular(self):
        """Test calcular frecuencia de compra regular"""
        mock_repositorio = Mock()
        
        fecha_inicio = datetime.now() - timedelta(days=60)
        pedidos = []
        for i in range(3):  # 3 pedidos en 60 días = regular
            fecha = fecha_inicio + timedelta(days=i*20)
            item = self.crear_mock_item('prod1', 'Producto 1', 1, 10.0)
            pedido = self.crear_mock_pedido(
                uuid.uuid4(), self.cliente_id, 'confirmado', 10.0, [item], fecha
            )
            pedidos.append(pedido)
        
        mock_repositorio.obtener_todos.return_value = pedidos
        servicio = ServicioHistorialCliente(repositorio_pedidos=mock_repositorio)
        
        resultado = servicio.obtener_historial_cliente(self.cliente_id)
        
        assert 'regular' in resultado['frecuencia_compra'].lower()
    
    def test_calcular_frecuencia_compra_ocasional(self):
        """Test calcular frecuencia de compra ocasional"""
        mock_repositorio = Mock()
        
        fecha_inicio = datetime.now() - timedelta(days=90)
        pedidos = []
        for i in range(2):  # 2 pedidos en 90 días = ocasional
            fecha = fecha_inicio + timedelta(days=i*45)
            item = self.crear_mock_item('prod1', 'Producto 1', 1, 10.0)
            pedido = self.crear_mock_pedido(
                uuid.uuid4(), self.cliente_id, 'confirmado', 10.0, [item], fecha
            )
            pedidos.append(pedido)
        
        mock_repositorio.obtener_todos.return_value = pedidos
        servicio = ServicioHistorialCliente(repositorio_pedidos=mock_repositorio)
        
        resultado = servicio.obtener_historial_cliente(self.cliente_id)
        
        assert 'ocasional' in resultado['frecuencia_compra'].lower()
    
    def test_productos_mas_comprados_ordenados(self):
        """Test que los productos más comprados están ordenados"""
        mock_repositorio = Mock()
        
        item1 = self.crear_mock_item('prod1', 'Producto 1', 10, 10.0)  # Más cantidad
        item2 = self.crear_mock_item('prod2', 'Producto 2', 5, 15.0)
        item3 = self.crear_mock_item('prod3', 'Producto 3', 3, 20.0)
        
        pedido1 = self.crear_mock_pedido(
            uuid.uuid4(), self.cliente_id, 'confirmado', 100.0, [item1]
        )
        pedido2 = self.crear_mock_pedido(
            uuid.uuid4(), self.cliente_id, 'confirmado', 75.0, [item2]
        )
        pedido3 = self.crear_mock_pedido(
            uuid.uuid4(), self.cliente_id, 'confirmado', 60.0, [item3]
        )
        
        mock_repositorio.obtener_todos.return_value = [pedido1, pedido2, pedido3]
        servicio = ServicioHistorialCliente(repositorio_pedidos=mock_repositorio)
        
        resultado = servicio.obtener_historial_cliente(self.cliente_id)
        
        productos = resultado['productos_mas_comprados']
        assert productos[0]['nombre'] == 'Producto 1'  # Más cantidad
        assert productos[0]['cantidad_total'] == 10
        assert productos[1]['nombre'] == 'Producto 2'
        assert productos[2]['nombre'] == 'Producto 3'
    
    def test_historial_con_pedidos_sin_fecha(self):
        """Test historial con pedidos sin fecha de creación"""
        mock_repositorio = Mock()
        
        item1 = self.crear_mock_item('prod1', 'Producto 1', 2, 10.0)
        pedido = self.crear_mock_pedido(
            uuid.uuid4(), self.cliente_id, 'confirmado', 20.0, [item1]
        )
        pedido._created_at_model = None  # Sin fecha
        
        mock_repositorio.obtener_todos.return_value = [pedido]
        servicio = ServicioHistorialCliente(repositorio_pedidos=mock_repositorio)
        
        resultado = servicio.obtener_historial_cliente(self.cliente_id)
        
        assert resultado['total_pedidos'] == 1
        assert resultado['ultimos_pedidos'][0]['fecha'] == 'Fecha no disponible'
        # Cuando hay un solo pedido, devuelve "Cliente con una sola compra"
        assert resultado['frecuencia_compra'] == 'Cliente con una sola compra'
    
    def test_historial_error_exception(self):
        """Test que maneja errores correctamente"""
        mock_repositorio = Mock()
        mock_repositorio.obtener_todos.side_effect = Exception("Error de BD")
        
        servicio = ServicioHistorialCliente(repositorio_pedidos=mock_repositorio)
        
        resultado = servicio.obtener_historial_cliente(self.cliente_id)
        
        assert resultado['total_pedidos'] == 0
        assert resultado['frecuencia_compra'] == 'Error al obtener historial'

