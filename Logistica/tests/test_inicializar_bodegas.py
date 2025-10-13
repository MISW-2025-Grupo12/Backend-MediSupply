"""
Tests para el comando de inicializar bodegas
"""

import pytest
from unittest.mock import patch, MagicMock
from src.aplicacion.comandos.inicializar_bodegas import InicializarBodegas, InicializarBodegasHandler
from src.aplicacion.dto import BodegaDTO


class TestInicializarBodegas:
    """Tests para el comando InicializarBodegas"""

    def test_inicializar_bodegas_handler_crear_bodegas(self):
        """Test para crear bodegas por defecto"""
        # Mock del repositorio
        mock_repo = MagicMock()
        mock_repo.obtener_todas.return_value = []
        mock_repo.crear.return_value = BodegaDTO(
            id="bodega-1",
            nombre="Bodega Central",
            direccion="Calle 10 # 20-30, Bogotá"
        )
        
        handler = InicializarBodegasHandler(repositorio=mock_repo)
        comando = InicializarBodegas()
        
        resultado = handler.handle(comando)
        
        # Verificar que se crearon 3 bodegas
        assert mock_repo.crear.call_count == 3
        assert resultado['count'] == 3
        assert 'Bodegas inicializadas exitosamente' in resultado['message']

    def test_inicializar_bodegas_handler_con_repositorio_por_defecto(self):
        """Test para verificar que se puede crear el handler sin repositorio"""
        handler = InicializarBodegasHandler()
        assert handler.repositorio is not None

    def test_inicializar_bodegas_handler_con_repositorio_personalizado(self):
        """Test para verificar que se puede pasar un repositorio personalizado"""
        mock_repo = MagicMock()
        handler = InicializarBodegasHandler(repositorio=mock_repo)
        assert handler.repositorio == mock_repo

    def test_inicializar_bodegas_handler_error_creacion(self):
        """Test para manejo de errores al crear bodegas"""
        mock_repo = MagicMock()
        mock_repo.obtener_todas.return_value = []
        mock_repo.crear.side_effect = Exception("Error de base de datos")
        
        handler = InicializarBodegasHandler(repositorio=mock_repo)
        comando = InicializarBodegas()
        
        with pytest.raises(Exception) as exc_info:
            handler.handle(comando)
        
        assert "Error de base de datos" in str(exc_info.value)

    def test_inicializar_bodegas_comando_estructura(self):
        """Test para verificar la estructura del comando"""
        comando = InicializarBodegas()
        assert hasattr(comando, '__dataclass_fields__')
        assert len(comando.__dataclass_fields__) == 0

    @patch('src.aplicacion.comandos.inicializar_bodegas.ejecutar_comando')
    def test_ejecutar_comando_registrado(self, mock_ejecutar):
        """Test para verificar que el comando está registrado correctamente"""
        from src.aplicacion.comandos.inicializar_bodegas import ejecutar_comando
        
        assert ejecutar_comando is not None
        assert callable(ejecutar_comando)
