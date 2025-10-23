import pytest
import uuid
from datetime import datetime
from src.aplicacion.dto import EvidenciaVisitaDTO

class TestEvidenciaVisitaDTO:
    """Tests para el DTO de Evidencia de Visita"""
    
    def test_crear_evidencia_dto_completo(self):
        """Test: Crear DTO de evidencia con todos los campos"""
        evidencia_id = uuid.uuid4()
        created_at = datetime.utcnow()
        
        dto = EvidenciaVisitaDTO(
            id=evidencia_id,
            visita_id="visita-123",
            archivo_url="https://storage.googleapis.com/evidencias-g12/evidencias/foto.jpg",
            nombre_archivo="equipo_medico.jpg",
            formato="jpg",
            tamaño_bytes=204800,
            comentarios="Equipo en perfecto estado, sin daños visibles",
            vendedor_id="vendedor-456",
            created_at=created_at
        )
        
        assert dto.id == evidencia_id
        assert dto.visita_id == "visita-123"
        assert dto.archivo_url == "https://storage.googleapis.com/evidencias-g12/evidencias/foto.jpg"
        assert dto.nombre_archivo == "equipo_medico.jpg"
        assert dto.formato == "jpg"
        assert dto.tamaño_bytes == 204800
        assert dto.comentarios == "Equipo en perfecto estado, sin daños visibles"
        assert dto.vendedor_id == "vendedor-456"
        assert dto.created_at == created_at
    
    def test_evidencia_dto_frozen(self):
        """Test: DTO es inmutable (frozen)"""
        dto = EvidenciaVisitaDTO(
            visita_id="visita-789",
            archivo_url="https://example.com/video.mp4",
            nombre_archivo="video.mp4",
            formato="mp4",
            tamaño_bytes=5242880,
            comentarios="Video de inspección",
            vendedor_id="vendedor-1",
            created_at=datetime.utcnow()
        )
        
        # Intentar modificar debería fallar
        with pytest.raises(Exception):  # FrozenInstanceError en dataclass frozen
            dto.comentarios = "Nuevo comentario"
    
    def test_evidencia_dto_con_id_autogenerado(self):
        """Test: DTO genera ID automáticamente si no se proporciona"""
        dto = EvidenciaVisitaDTO(
            visita_id="visita-abc",
            archivo_url="https://example.com/imagen.png",
            nombre_archivo="imagen.png",
            formato="png",
            tamaño_bytes=51200,
            comentarios="",
            vendedor_id="vendedor-xyz",
            created_at=datetime.utcnow()
        )
        
        assert dto.id is not None
        assert isinstance(dto.id, uuid.UUID)
    
    def test_evidencia_dto_con_video(self):
        """Test: DTO con video en lugar de imagen"""
        dto = EvidenciaVisitaDTO(
            visita_id="visita-video-1",
            archivo_url="https://storage.googleapis.com/evidencias-g12/evidencias/video123.mov",
            nombre_archivo="inspeccion_completa.mov",
            formato="mov",
            tamaño_bytes=52428800,  # 50 MB
            comentarios="Video completo de la inspección del equipo",
            vendedor_id="vendedor-999",
            created_at=datetime.utcnow()
        )
        
        assert dto.formato == "mov"
        assert dto.tamaño_bytes == 52428800
        assert "Video completo" in dto.comentarios
    
    def test_evidencia_dto_sin_comentarios(self):
        """Test: DTO válido sin comentarios"""
        dto = EvidenciaVisitaDTO(
            visita_id="visita-sin-comentarios",
            archivo_url="https://example.com/foto_rapida.jpg",
            nombre_archivo="foto_rapida.jpg",
            formato="jpg",
            tamaño_bytes=81920,
            comentarios="",
            vendedor_id="vendedor-123",
            created_at=datetime.utcnow()
        )
        
        assert dto.comentarios == ""
        assert dto.nombre_archivo == "foto_rapida.jpg"

