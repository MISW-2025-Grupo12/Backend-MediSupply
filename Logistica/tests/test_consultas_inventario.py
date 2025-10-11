import pytest
import sys
import os
from unittest.mock import Mock, patch
from datetime import datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from aplicacion.consultas.buscar_productos_con_inventario import BuscarProductosConInventario, BuscarProductosConInventarioHandler
from aplicacion.dto import InventarioDTO

class TestBuscarProductosConInventario:
    def setup_method(self):
        self.handler = BuscarProductosConInventarioHandler()
        self.mock_repositorio = Mock()
        self.mock_servicio_productos = Mock()
        self.handler._repositorio = self.mock_repositorio
        self.handler._servicio_productos = self.mock_servicio_productos

    def test_crear_consulta(self):
        consulta = BuscarProductosConInventario(termino="test", limite=10)
        assert consulta.termino == "test"
        assert consulta.limite == 10

    def test_crear_consulta_con_limite_default(self):
        consulta = BuscarProductosConInventario(termino="test")
        assert consulta.termino == "test"
        assert consulta.limite == 50

    def test_handle_termino_vacio(self):
        consulta = BuscarProductosConInventario(termino="")
        resultado = self.handler.handle(consulta)
        assert resultado == []

    def test_handle_termino_solo_espacios(self):
        consulta = BuscarProductosConInventario(termino="   ")
        resultado = self.handler.handle(consulta)
        assert resultado == []

    def test_handle_termino_muy_largo(self):
        termino_largo = "a" * 150
        consulta = BuscarProductosConInventario(termino=termino_largo)
        
        with patch('aplicacion.consultas.buscar_productos_con_inventario.logger') as mock_logger:
            resultado = self.handler.handle(consulta)
            mock_logger.warning.assert_called_once()

    def test_handle_sin_productos_encontrados(self):
        consulta = BuscarProductosConInventario(termino="test")
        self.mock_servicio_productos.buscar_productos.return_value = []
        
        resultado = self.handler.handle(consulta)
        
        assert resultado == []
        self.mock_servicio_productos.buscar_productos.assert_called_once_with(
            termino="test", limite=50
        )

    def test_handle_exitoso_con_inventario(self):
        consulta = BuscarProductosConInventario(termino="test")
        
        # Mock de productos encontrados
        productos = [
            {
                "id": "prod-1",
                "nombre": "Producto 1",
                "descripcion": "Descripción 1",
                "precio": 100.0,
                "categoria": "Categoría 1"
            }
        ]
        self.mock_servicio_productos.buscar_productos.return_value = productos
        
        # Mock de inventario
        fecha_vencimiento = datetime.now() + timedelta(days=30)
        inventario_dto = InventarioDTO(
            producto_id="prod-1",
            cantidad_disponible=10,
            cantidad_reservada=5,
            fecha_vencimiento=fecha_vencimiento
        )
        self.mock_repositorio.obtener_por_producto_id.return_value = [inventario_dto]
        
        resultado = self.handler.handle(consulta)
        
        assert len(resultado) == 1
        producto = resultado[0]
        assert producto["id"] == "prod-1"
        assert producto["nombre"] == "Producto 1"
        assert producto["cantidad_disponible"] == 10
        assert producto["cantidad_reservada"] == 5
        assert len(producto["lotes"]) == 1
        assert producto["lotes"][0]["cantidad_disponible"] == 10

    def test_handle_sin_inventario_registrado(self):
        consulta = BuscarProductosConInventario(termino="test")
        
        # Mock de productos encontrados
        productos = [
            {
                "id": "prod-1",
                "nombre": "Producto 1",
                "descripcion": "Descripción 1",
                "precio": 100.0,
                "categoria": "Categoría 1"
            }
        ]
        self.mock_servicio_productos.buscar_productos.return_value = productos
        
        # Mock de sin inventario
        self.mock_repositorio.obtener_por_producto_id.return_value = []
        
        resultado = self.handler.handle(consulta)
        
        assert resultado == []

    def test_handle_multiples_lotes(self):
        consulta = BuscarProductosConInventario(termino="test")
        
        # Mock de productos encontrados
        productos = [
            {
                "id": "prod-1",
                "nombre": "Producto 1",
                "descripcion": "Descripción 1",
                "precio": 100.0,
                "categoria": "Categoría 1"
            }
        ]
        self.mock_servicio_productos.buscar_productos.return_value = productos
        
        # Mock de múltiples lotes
        fecha1 = datetime.now() + timedelta(days=30)
        fecha2 = datetime.now() + timedelta(days=60)
        lotes = [
            InventarioDTO(
                producto_id="prod-1",
                cantidad_disponible=5,
                cantidad_reservada=2,
                fecha_vencimiento=fecha1
            ),
            InventarioDTO(
                producto_id="prod-1",
                cantidad_disponible=8,
                cantidad_reservada=3,
                fecha_vencimiento=fecha2
            )
        ]
        self.mock_repositorio.obtener_por_producto_id.return_value = lotes
        
        resultado = self.handler.handle(consulta)
        
        assert len(resultado) == 1
        producto = resultado[0]
        assert producto["cantidad_disponible"] == 13  # 5 + 8
        assert producto["cantidad_reservada"] == 5    # 2 + 3
        assert len(producto["lotes"]) == 2

    def test_handle_producto_sin_id(self):
        consulta = BuscarProductosConInventario(termino="test")
        
        # Mock de productos sin ID
        productos = [
            {
                "nombre": "Producto 1",
                "descripcion": "Descripción 1",
                "precio": 100.0,
                "categoria": "Categoría 1"
            }
        ]
        self.mock_servicio_productos.buscar_productos.return_value = productos
        
        resultado = self.handler.handle(consulta)
        
        assert resultado == []
        # No debe llamar al repositorio si no hay ID
        self.mock_repositorio.obtener_por_producto_id.assert_not_called()

    def test_handle_excepcion(self):
        consulta = BuscarProductosConInventario(termino="test")
        self.mock_servicio_productos.buscar_productos.side_effect = Exception("Error de servicio")
        
        with patch('aplicacion.consultas.buscar_productos_con_inventario.logger') as mock_logger:
            resultado = self.handler.handle(consulta)
            
            assert resultado == []
            mock_logger.error.assert_called_once()
