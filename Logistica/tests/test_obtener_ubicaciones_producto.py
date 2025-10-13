"""
Tests para la consulta de ubicaciones de productos
"""

import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime
from src.aplicacion.consultas.obtener_ubicaciones_producto import ObtenerUbicacionesProducto, ObtenerUbicacionesProductoHandler
from src.aplicacion.dto import InventarioDTO, BodegaDTO


class TestObtenerUbicacionesProducto:
    """Tests para la consulta ObtenerUbicacionesProducto"""

    def test_obtener_ubicaciones_producto_handler_sin_inventario(self):
        """Test para producto sin inventario"""
        # Mock del repositorio de inventario
        mock_repo_inventario = MagicMock()
        mock_repo_inventario.obtener_por_producto_id.return_value = []
        
        handler = ObtenerUbicacionesProductoHandler(
            repositorio_inventario=mock_repo_inventario
        )
        consulta = ObtenerUbicacionesProducto(producto_id="prod-inexistente")
        
        resultado = handler.handle(consulta)
        
        assert resultado['producto_id'] == "prod-inexistente"
        assert resultado['ubicaciones'] == []
        assert resultado['total_bodegas'] == 0
        assert resultado['total_cantidad_disponible'] == 0
        assert resultado['total_cantidad_reservada'] == 0
        assert 'no encontrado' in resultado['mensaje']

    def test_obtener_ubicaciones_producto_handler_con_inventario(self):
        """Test para producto con inventario en una bodega"""
        # Mock de inventario
        inventario_dto = InventarioDTO(
            producto_id="prod-1",
            cantidad_disponible=50,
            cantidad_reservada=10,
            fecha_vencimiento=datetime(2025, 12, 31),
            bodega_id="bodega-1",
            pasillo="A",
            estante="5",
            id="inventario-1"
        )
        
        # Mock de bodega
        bodega_model = MagicMock()
        bodega_model.id = "bodega-1"
        bodega_model.nombre = "Bodega Central"
        bodega_model.direccion = "Av. Principal #123"
        
        # Mock de repositorios
        mock_repo_inventario = MagicMock()
        mock_repo_inventario.obtener_por_producto_id.return_value = [inventario_dto]
        
        mock_repo_bodega = MagicMock()
        mock_repo_bodega.obtener_por_id.return_value = bodega_model
        
        handler = ObtenerUbicacionesProductoHandler(
            repositorio_inventario=mock_repo_inventario,
            repositorio_bodega=mock_repo_bodega
        )
        consulta = ObtenerUbicacionesProducto(producto_id="prod-1")
        
        resultado = handler.handle(consulta)
        
        assert resultado['producto_id'] == "prod-1"
        assert resultado['total_bodegas'] == 1
        assert resultado['total_cantidad_disponible'] == 50
        assert resultado['total_cantidad_reservada'] == 10
        assert len(resultado['ubicaciones']) == 1
        
        ubicacion = resultado['ubicaciones'][0]
        assert ubicacion['bodega_id'] == "bodega-1"
        assert ubicacion['bodega_nombre'] == "Bodega Central"
        assert ubicacion['bodega_direccion'] == "Av. Principal #123"
        assert ubicacion['total_cantidad_disponible'] == 50
        assert ubicacion['total_cantidad_reservada'] == 10
        
        ubicacion_fisica = ubicacion['ubicaciones_fisicas'][0]
        assert ubicacion_fisica['pasillo'] == "A"
        assert ubicacion_fisica['estante'] == "5"
        assert ubicacion_fisica['cantidad_disponible'] == 50
        assert ubicacion_fisica['cantidad_reservada'] == 10
        assert "Bodega Central - Pasillo A - Estante 5" in ubicacion_fisica['ubicacion_descripcion']

    def test_obtener_ubicaciones_producto_handler_sin_bodega_asignada(self):
        """Test para producto con inventario sin bodega asignada"""
        # Mock de inventario sin bodega
        inventario_dto = InventarioDTO(
            producto_id="prod-1",
            cantidad_disponible=30,
            cantidad_reservada=5,
            fecha_vencimiento=datetime(2025, 12, 31),
            bodega_id=None,
            pasillo=None,
            estante=None,
            id="inventario-1"
        )
        
        # Mock de repositorios
        mock_repo_inventario = MagicMock()
        mock_repo_inventario.obtener_por_producto_id.return_value = [inventario_dto]
        
        handler = ObtenerUbicacionesProductoHandler(
            repositorio_inventario=mock_repo_inventario
        )
        consulta = ObtenerUbicacionesProducto(producto_id="prod-1")
        
        resultado = handler.handle(consulta)
        
        assert resultado['producto_id'] == "prod-1"
        assert resultado['total_bodegas'] == 1
        assert resultado['total_cantidad_disponible'] == 30
        assert resultado['total_cantidad_reservada'] == 5
        
        ubicacion = resultado['ubicaciones'][0]
        assert ubicacion['bodega_id'] is None
        assert ubicacion['bodega_nombre'] == "Sin asignar"
        assert ubicacion['bodega_direccion'] is None
        
        ubicacion_fisica = ubicacion['ubicaciones_fisicas'][0]
        assert ubicacion_fisica['pasillo'] is None
        assert ubicacion_fisica['estante'] is None
        assert ubicacion_fisica['ubicacion_descripcion'] == "Sin ubicación asignada"

    def test_obtener_ubicaciones_producto_handler_multiple_bodegas(self):
        """Test para producto con inventario en múltiples bodegas"""
        # Mock de inventarios en diferentes bodegas
        inventario1 = InventarioDTO(
            producto_id="prod-1",
            cantidad_disponible=30,
            cantidad_reservada=5,
            fecha_vencimiento=datetime(2025, 12, 31),
            bodega_id="bodega-1",
            pasillo="A",
            estante="5",
            id="inventario-1"
        )
        
        inventario2 = InventarioDTO(
            producto_id="prod-1",
            cantidad_disponible=20,
            cantidad_reservada=3,
            fecha_vencimiento=datetime(2025, 12, 31),
            bodega_id="bodega-2",
            pasillo="B",
            estante="10",
            id="inventario-2"
        )
        
        # Mock de bodegas
        bodega1 = MagicMock()
        bodega1.id = "bodega-1"
        bodega1.nombre = "Bodega Central"
        bodega1.direccion = "Av. Principal #123"
        
        bodega2 = MagicMock()
        bodega2.id = "bodega-2"
        bodega2.nombre = "Bodega Norte"
        bodega2.direccion = "Av. Norte #456"
        
        # Mock de repositorios
        mock_repo_inventario = MagicMock()
        mock_repo_inventario.obtener_por_producto_id.return_value = [inventario1, inventario2]
        
        mock_repo_bodega = MagicMock()
        mock_repo_bodega.obtener_por_id.side_effect = lambda bodega_id: {
            "bodega-1": bodega1,
            "bodega-2": bodega2
        }[bodega_id]
        
        handler = ObtenerUbicacionesProductoHandler(
            repositorio_inventario=mock_repo_inventario,
            repositorio_bodega=mock_repo_bodega
        )
        consulta = ObtenerUbicacionesProducto(producto_id="prod-1")
        
        resultado = handler.handle(consulta)
        
        assert resultado['producto_id'] == "prod-1"
        assert resultado['total_bodegas'] == 2
        assert resultado['total_cantidad_disponible'] == 50  # 30 + 20
        assert resultado['total_cantidad_reservada'] == 8   # 5 + 3
        assert len(resultado['ubicaciones']) == 2
        
        # Verificar que ambas bodegas están presentes
        bodega_ids = [ubicacion['bodega_id'] for ubicacion in resultado['ubicaciones']]
        assert "bodega-1" in bodega_ids
        assert "bodega-2" in bodega_ids

    def test_obtener_ubicaciones_producto_handler_con_repositorios_por_defecto(self):
        """Test para verificar que se pueden crear repositorios por defecto"""
        handler = ObtenerUbicacionesProductoHandler()
        assert handler.repositorio_inventario is not None
        assert handler.repositorio_bodega is not None

    def test_obtener_ubicaciones_producto_consulta_estructura(self):
        """Test para verificar la estructura de la consulta"""
        consulta = ObtenerUbicacionesProducto(producto_id="prod-1")
        assert consulta.producto_id == "prod-1"
        assert hasattr(consulta, '__dataclass_fields__')

    @patch('src.aplicacion.consultas.obtener_ubicaciones_producto.ejecutar_consulta')
    def test_ejecutar_consulta_registrado(self, mock_ejecutar):
        """Test para verificar que la consulta está registrada correctamente"""
        from src.aplicacion.consultas.obtener_ubicaciones_producto import ejecutar_consulta
        
        # Verificar que ejecutar_consulta está disponible
        assert ejecutar_consulta is not None
        assert callable(ejecutar_consulta)
