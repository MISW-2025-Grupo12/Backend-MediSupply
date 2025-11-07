from dataclasses import dataclass
from seedwork.aplicacion.comandos import Comando, ejecutar_comando
import logging
from aplicacion.servicios.servicio_carga_masiva import ServicioCargaMasiva
from infraestructura.servicio_gcp_storage import get_storage_service
from infraestructura.repositorios import RepositorioJobSQLite
from aplicacion.dto import CargaMasivaJobDTO

logger = logging.getLogger(__name__)

@dataclass
class ProcesarCargaMasiva(Comando):
    job_id: str

class ProcesarCargaMasivaHandler:
    def __init__(self, repositorio_job=None, servicio_carga=None, servicio_storage=None):
        self.repositorio_job = repositorio_job or RepositorioJobSQLite()
        self.servicio_carga = servicio_carga or ServicioCargaMasiva()
        self.servicio_storage = servicio_storage or get_storage_service()
    
    def handle(self, comando: ProcesarCargaMasiva) -> CargaMasivaJobDTO:
        """Procesa un job de carga masiva"""
        try:
            # 1. Obtener job
            job = self.repositorio_job.obtener_por_id(comando.job_id)
            if not job:
                raise ValueError(f"Job {comando.job_id} no encontrado")
            
            # 2. El job ya debería estar en processing (marcado por JobsManager)
            # Solo actualizar si no está en processing
            if job.status != 'processing':
                job.status = 'processing'
                self.repositorio_job.actualizar(job)
            
            # 3. Descargar CSV original desde GCP
            logger.info(f"Descargando CSV original para job {comando.job_id}")
            csv_content = self.servicio_storage.descargar_csv(comando.job_id)
            
            # 4. Parsear CSV para obtener filas normalizadas, headers originales y mapeo
            filas_normalizadas, headers_originales, mapeo_headers = self.servicio_carga.parsear_csv(csv_content)
            
            # 5. Procesar cada fila con callback de progreso
            def callback_progreso(filas_procesadas: int, total_filas: int):
                """Callback para actualizar progreso en BD"""
                try:
                    job.filas_procesadas = filas_procesadas
                    job.updated_at = self._get_current_datetime()
                    self.repositorio_job.actualizar(job)
                except Exception as e:
                    logger.error(f"Error actualizando progreso: {e}")
            
            logger.info(f"Procesando {len(filas_normalizadas)} filas para job {comando.job_id}")
            resultados = []
            
            for i, fila in enumerate(filas_normalizadas):
                # Procesar fila
                resultado = self.servicio_carga.procesar_fila(fila)
                resultados.append(resultado)
                
                # Actualizar contadores
                if resultado['status'] == 'creado' or resultado['status'] == 'actualizado':
                    job.filas_exitosas += 1
                elif resultado['status'] == 'rechazado':
                    job.filas_rechazadas += 1
                elif resultado['status'] == 'error':
                    job.filas_error += 1
                
                job.filas_procesadas = i + 1
                
                # Actualizar BD cada 10 filas o al final
                if (i + 1) % 10 == 0 or i == len(filas_normalizadas) - 1:
                    job.updated_at = self._get_current_datetime()
                    self.repositorio_job.actualizar(job)
            
            # 6. Generar CSV resultado
            logger.info(f"Generando CSV resultado para job {comando.job_id}")
            csv_resultado = self.servicio_carga.generar_csv_resultado(
                filas_normalizadas, resultados, headers_originales, mapeo_headers
            )
            
            # 7. Subir CSV resultado a GCP
            logger.info(f"Subiendo CSV resultado a GCP para job {comando.job_id}")
            result_url = self.servicio_storage.guardar_csv_resultado(csv_resultado, comando.job_id)
            
            # 8. Actualizar job como completado
            job.status = 'completed'
            job.result_url = result_url
            job.updated_at = self._get_current_datetime()
            self.repositorio_job.actualizar(job)
            
            logger.info(f"Job {comando.job_id} completado exitosamente")
            return job
            
        except Exception as e:
            logger.error(f"Error procesando carga masiva job {comando.job_id}: {e}")
            # Actualizar job como fallido
            try:
                job = self.repositorio_job.obtener_por_id(comando.job_id)
                if job:
                    job.status = 'failed'
                    job.error = str(e)
                    job.updated_at = self._get_current_datetime()
                    self.repositorio_job.actualizar(job)
            except Exception as update_error:
                logger.error(f"Error actualizando job como fallido: {update_error}")
            
            raise
    
    def _get_current_datetime(self):
        """Obtiene la fecha actual"""
        from datetime import datetime
        return datetime.utcnow()

@ejecutar_comando.register
def _(comando: ProcesarCargaMasiva):
    handler = ProcesarCargaMasivaHandler()
    return handler.handle(comando)

