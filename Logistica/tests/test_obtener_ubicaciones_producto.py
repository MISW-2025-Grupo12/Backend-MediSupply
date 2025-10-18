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
        
        assert resultado['id'] == "prod-1"
        assert len(resultado['ubicaciones']) == 1

        # Suma de cantidades desde ubicaciones
        assert sum(u['stock_disponible'] for u in resultado['ubicaciones']) == 50
        assert sum(u['stock_reservado'] for u in resultado['ubicaciones']) == 10

        # Validar estructura de la primera ubicación
        ubicacion = resultado['ubicaciones'][0]
        assert ubicacion['nombre'] == "Bodega Central"
        assert ubicacion['pasillo'] == "A"
        assert ubicacion['estante'] == "5"
        assert ubicacion['stock_disponible'] == 50
        assert ubicacion['stock_reservado'] == 10

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
        
        assert resultado['id'] == "prod-1"
        assert len(resultado['ubicaciones']) == 1

        # Validar sumatorias desde las ubicaciones
        assert sum(u['stock_disponible'] for u in resultado['ubicaciones']) == 30
        assert sum(u['stock_reservado'] for u in resultado['ubicaciones']) == 5

        # Validar la primera ubicación sin bodega asignada
        ubicacion = resultado['ubicaciones'][0]
        assert ubicacion['nombre'] == "Sin asignar"
        assert ubicacion['pasillo'] is None
        assert ubicacion['estante'] is None
        assert ubicacion['stock_disponible'] == 30
        assert ubicacion['stock_reservado'] == 5

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
        
        assert resultado['id'] == "prod-1"

        # Verificar que hay dos ubicaciones
        assert len(resultado['ubicaciones']) == 2

        # Sumar cantidades desde ubicaciones
        assert sum(u['stock_disponible'] for u in resultado['ubicaciones']) == 50  # 30 + 20
        assert sum(u['stock_reservado'] for u in resultado['ubicaciones']) == 8    # 5 + 3

        # Validar que ambas bodegas están presentes
        nombres_bodegas = [u['nombre'] for u in resultado['ubicaciones']]
        assert "Bodega Central" in nombres_bodegas
        assert "Bodega Norte" in nombres_bodegas

        # Validar que las ubicaciones tengan los datos correctos
        ubicacion_central = next(u for u in resultado['ubicaciones'] if u['nombre'] == "Bodega Central")
        assert ubicacion_central['pasillo'] == "A"
        assert ubicacion_central['estante'] == "5"
        assert ubicacion_central['stock_disponible'] == 30
        assert ubicacion_central['stock_reservado'] == 5

        ubicacion_norte = next(u for u in resultado['ubicaciones'] if u['nombre'] == "Bodega Norte")
        assert ubicacion_norte['pasillo'] == "B"
        assert ubicacion_norte['estante'] == "10"
        assert ubicacion_norte['stock_disponible'] == 20
        assert ubicacion_norte['stock_reservado'] == 3

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
