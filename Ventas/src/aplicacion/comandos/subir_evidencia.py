from dataclasses import dataclass
from seedwork.aplicacion.comandos import Comando, ejecutar_comando
import uuid
import logging
from datetime import datetime
from aplicacion.dto import EvidenciaVisitaDTO
from dominio.entidades import EvidenciaVisita
from infraestructura.repositorios import RepositorioEvidenciaVisita, RepositorioVisita
from infraestructura.servicio_storage import get_storage_service

logger = logging.getLogger(__name__)

FORMATOS_PERMITIDOS = ['jpg', 'jpeg', 'png', 'mp4', 'mov']
TAMAÑO_MAXIMO = 100 * 1024 * 1024  # 100MB

@dataclass
class SubirEvidencia(Comando):
    visita_id: str
    archivo_data: bytes
    nombre_archivo: str
    content_type: str
    comentarios: str
    vendedor_id: str

class SubirEvidenciaHandler:
    def __init__(self, repositorio_evidencia=None, repositorio_visita=None, storage_service=None):
        self.repositorio_evidencia = repositorio_evidencia or RepositorioEvidenciaVisita()
        self.repositorio_visita = repositorio_visita or RepositorioVisita()
        self.storage_service = storage_service or get_storage_service()
    
    def handle(self, comando: SubirEvidencia) -> EvidenciaVisitaDTO:
        try:
            # 1. Validar que la visita existe
            visita = self.repositorio_visita.obtener_por_id(comando.visita_id)
            if not visita:
                raise ValueError(f"Visita no encontrada: {comando.visita_id}")
            
            # 2. Validar formato
            extension = comando.nombre_archivo.rsplit('.', 1)[-1].lower() if '.' in comando.nombre_archivo else ''
            if extension not in FORMATOS_PERMITIDOS:
                raise ValueError(f"Formato no permitido: {extension}. Use: {', '.join(FORMATOS_PERMITIDOS)}")
            
            # 3. Validar tamaño
            tamaño = len(comando.archivo_data)
            if tamaño > TAMAÑO_MAXIMO:
                raise ValueError(f"Archivo excede el tamaño máximo de 100MB")
            
            # 4. Guardar archivo en storage
            logger.info(f"Subiendo archivo {comando.nombre_archivo} ({tamaño} bytes)")
            archivo_url = self.storage_service.guardar_archivo(
                comando.archivo_data,
                comando.nombre_archivo,
                comando.content_type
            )
            
            # 5. Crear entidad de dominio
            evidencia = EvidenciaVisita(
                visita_id=comando.visita_id,
                archivo_url=archivo_url,
                nombre_archivo=comando.nombre_archivo,
                formato=extension,
                tamaño_bytes=tamaño,
                comentarios=comando.comentarios,
                vendedor_id=comando.vendedor_id
            )
            
            # 6. Disparar evento
            evidencia.disparar_evento_creacion()
            
            # 7. Crear DTO
            evidencia_dto = EvidenciaVisitaDTO(
                id=evidencia.id,
                visita_id=comando.visita_id,
                archivo_url=archivo_url,
                nombre_archivo=comando.nombre_archivo,
                formato=extension,
                tamaño_bytes=tamaño,
                comentarios=comando.comentarios,
                vendedor_id=comando.vendedor_id,
                created_at=datetime.now()
            )
            
            # 8. Guardar en BD
            evidencia_guardada = self.repositorio_evidencia.crear(evidencia_dto)
            
            logger.info(f"Evidencia guardada exitosamente: {evidencia_guardada.id}")
            return evidencia_guardada
            
        except ValueError as e:
            logger.warning(f"Error de validación: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error subiendo evidencia: {e}")
            raise

@ejecutar_comando.register
def _(comando: SubirEvidencia):
    handler = SubirEvidenciaHandler()
    return handler.handle(comando)

