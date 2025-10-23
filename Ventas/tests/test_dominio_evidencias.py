import pytest
import uuid
from datetime import datetime
from src.dominio.entidades import EvidenciaVisita
from src.dominio.eventos import EvidenciaSubida

class TestEvidenciaVisita:
    """Tests para la entidad EvidenciaVisita"""
    
    def test_crear_evidencia_visita_basica(self):
        """Test: Crear evidencia con valores básicos"""
        evidencia = EvidenciaVisita(
            visita_id="visita-123",
            archivo_url="https://storage.googleapis.com/bucket/file.jpg",
            nombre_archivo="foto_equipo.jpg",
            formato="jpg",
            tamaño_bytes=102400,
            comentarios="Equipo en buen estado",
            vendedor_id="vendedor-456"
        )
        
        assert evidencia.visita_id == "visita-123"
        assert evidencia.archivo_url == "https://storage.googleapis.com/bucket/file.jpg"
        assert evidencia.nombre_archivo == "foto_equipo.jpg"
        assert evidencia.formato == "jpg"
        assert evidencia.tamaño_bytes == 102400
        assert evidencia.comentarios == "Equipo en buen estado"
        assert evidencia.vendedor_id == "vendedor-456"
        assert evidencia.id is not None
    
    def test_evidencia_valores_por_defecto(self):
        """Test: Valores por defecto al crear evidencia"""
        evidencia = EvidenciaVisita()
        
        assert evidencia.visita_id == ""
        assert evidencia.archivo_url == ""
        assert evidencia.nombre_archivo == ""
        assert evidencia.formato == ""
        assert evidencia.tamaño_bytes == 0
        assert evidencia.comentarios == ""
        assert evidencia.vendedor_id == ""
        assert evidencia.id is not None
    
    def test_disparar_evento_creacion_evidencia(self):
        """Test: Disparar evento al crear evidencia"""
        evidencia = EvidenciaVisita(
            visita_id="visita-123",
            archivo_url="https://storage.googleapis.com/bucket/video.mp4",
            nombre_archivo="video_inspeccion.mp4",
            formato="mp4",
            tamaño_bytes=5242880,
            vendedor_id="vendedor-789"
        )
        
        evento = evidencia.disparar_evento_creacion()
        
        assert isinstance(evento, EvidenciaSubida)
        assert evento.evidencia_id == evidencia.id
        assert evento.visita_id == "visita-123"
        assert evento.vendedor_id == "vendedor-789"
        assert evento.archivo_url == "https://storage.googleapis.com/bucket/video.mp4"
    
    def test_evidencia_con_id_personalizado(self):
        """Test: Crear evidencia con ID personalizado"""
        custom_id = uuid.uuid4()
        evidencia = EvidenciaVisita(
            id=custom_id,
            visita_id="visita-999",
            archivo_url="https://example.com/file.png"
        )
        
        assert evidencia.id == custom_id
        assert evidencia.visita_id == "visita-999"


class TestEventoEvidenciaSubida:
    """Tests para el evento EvidenciaSubida"""
    
    def test_crear_evento_evidencia_subida(self):
        """Test: Crear evento de evidencia subida"""
        evidencia_id = uuid.uuid4()
        evento = EvidenciaSubida(
            evidencia_id=evidencia_id,
            visita_id="visita-abc",
            vendedor_id="vendedor-xyz",
            archivo_url="https://storage.googleapis.com/bucket/evidence.jpg"
        )
        
        assert evento.evidencia_id == evidencia_id
        assert evento.visita_id == "visita-abc"
        assert evento.vendedor_id == "vendedor-xyz"
        assert evento.archivo_url == "https://storage.googleapis.com/bucket/evidence.jpg"
    
    def test_evento_evidencia_get_datos_evento(self):
        """Test: Obtener datos del evento de evidencia"""
        evidencia_id = uuid.uuid4()
        evento = EvidenciaSubida(
            evidencia_id=evidencia_id,
            visita_id="visita-123",
            vendedor_id="vendedor-456",
            archivo_url="https://example.com/file.mp4"
        )
        
        datos = evento._get_datos_evento()
        
        assert isinstance(datos, dict)
        assert datos['evidencia_id'] == str(evidencia_id)
        assert datos['visita_id'] == "visita-123"
        assert datos['vendedor_id'] == "vendedor-456"
        assert datos['archivo_url'] == "https://example.com/file.mp4"
    
    def test_evento_evidencia_valores_por_defecto(self):
        """Test: Evento con valores por defecto"""
        evento = EvidenciaSubida()
        
        assert evento.evidencia_id is None
        assert evento.visita_id == ""
        assert evento.vendedor_id == ""
        assert evento.archivo_url == ""

