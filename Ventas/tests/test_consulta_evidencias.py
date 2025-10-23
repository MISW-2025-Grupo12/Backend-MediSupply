import pytest
import uuid
from datetime import datetime
from unittest.mock import Mock, patch
from src.aplicacion.consultas.obtener_evidencias_visita import (
    ObtenerEvidenciasVisita,
    ObtenerEvidenciasVisitaHandler
)
from src.aplicacion.dto import EvidenciaVisitaDTO

class TestObtenerEvidenciasVisita:
    """Tests para la consulta ObtenerEvidenciasVisita"""
    
    def test_crear_consulta(self):
        """Test: Crear consulta para obtener evidencias de una visita"""
        consulta = ObtenerEvidenciasVisita(visita_id="visita-123")
        
        assert consulta.visita_id == "visita-123"
    
    def test_handler_obtener_evidencias_exitoso(self):
        """Test: Handler obtiene evidencias correctamente"""
        # Arrange
        visita_id = "visita-456"
        evidencias_mock = [
            EvidenciaVisitaDTO(
                id=uuid.uuid4(),
                visita_id=visita_id,
                archivo_url="https://storage.googleapis.com/bucket/foto1.jpg",
                nombre_archivo="foto1.jpg",
                formato="jpg",
                tamaño_bytes=102400,
                comentarios="Primera foto",
                vendedor_id="vendedor-1",
                created_at=datetime.utcnow()
            ),
            EvidenciaVisitaDTO(
                id=uuid.uuid4(),
                visita_id=visita_id,
                archivo_url="https://storage.googleapis.com/bucket/video1.mp4",
                nombre_archivo="video1.mp4",
                formato="mp4",
                tamaño_bytes=5242880,
                comentarios="Video de inspección",
                vendedor_id="vendedor-1",
                created_at=datetime.utcnow()
            )
        ]
        
        repositorio_mock = Mock()
        repositorio_mock.obtener_por_visita.return_value = evidencias_mock
        
        handler = ObtenerEvidenciasVisitaHandler(repositorio=repositorio_mock)
        consulta = ObtenerEvidenciasVisita(visita_id=visita_id)
        
        # Act
        resultado = handler.handle(consulta)
        
        # Assert
        assert len(resultado) == 2
        assert resultado[0].archivo_url == "https://storage.googleapis.com/bucket/foto1.jpg"
        assert resultado[1].formato == "mp4"
        repositorio_mock.obtener_por_visita.assert_called_once_with(visita_id)
    
    def test_handler_obtener_evidencias_sin_resultados(self):
        """Test: Handler cuando no hay evidencias"""
        repositorio_mock = Mock()
        repositorio_mock.obtener_por_visita.return_value = []
        
        handler = ObtenerEvidenciasVisitaHandler(repositorio=repositorio_mock)
        consulta = ObtenerEvidenciasVisita(visita_id="visita-999")
        
        resultado = handler.handle(consulta)
        
        assert isinstance(resultado, list)
        assert len(resultado) == 0
    
    def test_handler_obtener_evidencias_con_excepcion(self):
        """Test: Handler maneja excepciones correctamente"""
        repositorio_mock = Mock()
        repositorio_mock.obtener_por_visita.side_effect = Exception("Error de base de datos")
        
        handler = ObtenerEvidenciasVisitaHandler(repositorio=repositorio_mock)
        consulta = ObtenerEvidenciasVisita(visita_id="visita-error")
        
        with pytest.raises(Exception) as exc_info:
            handler.handle(consulta)
        
        assert "Error de base de datos" in str(exc_info.value)

