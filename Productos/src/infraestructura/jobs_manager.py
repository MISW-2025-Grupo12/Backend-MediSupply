import threading
import time
import logging
from aplicacion.comandos.procesar_carga_masiva import ProcesarCargaMasiva
from seedwork.aplicacion.comandos import ejecutar_comando
from infraestructura.repositorios import RepositorioJobSQLite

logger = logging.getLogger(__name__)

class JobsManager:
    """Gestor de trabajos asíncronos para carga masiva"""
    
    def __init__(self, repositorio_job=None, poll_interval=5):
        self.repositorio_job = repositorio_job or RepositorioJobSQLite()
        self.poll_interval = poll_interval  # Segundos entre consultas
        self.worker_thread = None
        self.running = False
        self.app = None
    
    def iniciar(self, app=None):
        """Inicia el worker thread para procesar jobs"""
        if self.running:
            logger.warning("JobsManager ya está corriendo")
            return
        
        self.app = app
        self.running = True
        self.worker_thread = threading.Thread(target=self._worker_loop, daemon=True)
        self.worker_thread.start()
        logger.info("JobsManager iniciado")
    
    def detener(self):
        """Detiene el worker thread"""
        self.running = False
        if self.worker_thread:
            self.worker_thread.join(timeout=10)
        logger.info("JobsManager detenido")
    
    def _worker_loop(self):
        """Loop principal del worker que procesa jobs pendientes"""
        logger.info("Worker thread iniciado")
        
        while self.running:
            try:
                jobs_pendientes = None
                
                # Obtener jobs pendientes dentro del contexto de aplicación
                if self.app:
                    with self.app.app_context():
                        jobs_pendientes = self.repositorio_job.obtener_pendientes(limit=1)
                else:
                    # Sin app, intentar obtener jobs (puede fallar sin contexto)
                    jobs_pendientes = self.repositorio_job.obtener_pendientes(limit=1)
                
                if jobs_pendientes:
                    job = jobs_pendientes[0]
                    logger.info(f"Procesando job {job.id}")
                    
                    # Procesar job dentro del contexto de aplicación
                    if self.app:
                        with self.app.app_context():
                            self._procesar_job(job)
                    else:
                        self._procesar_job(job)
                else:
                    # No hay jobs pendientes, esperar antes de consultar de nuevo
                    time.sleep(self.poll_interval)
                    
            except Exception as e:
                logger.error(f"Error en worker loop: {e}", exc_info=True)
                time.sleep(self.poll_interval)
    
    def _procesar_job(self, job):
        """Procesa un job individual"""
        try:
            # El job ya está marcado como processing en obtener_pendientes
            # Ejecutar comando de procesamiento
            comando = ProcesarCargaMasiva(job_id=str(job.id))
            ejecutar_comando(comando)
            
            logger.info(f"Job {job.id} procesado exitosamente")
            
        except Exception as e:
            logger.error(f"Error procesando job {job.id}: {e}")
            # El comando ya actualiza el job como failed si hay error
            try:
                job = self.repositorio_job.obtener_por_id(str(job.id))
                if job and job.status != 'failed':
                    job.status = 'failed'
                    job.error = str(e)
                    self.repositorio_job.actualizar(job)
            except Exception as update_error:
                logger.error(f"Error actualizando job como failed: {update_error}")

# Instancia global del JobsManager
_jobs_manager_instance = None

def get_jobs_manager(app=None) -> JobsManager:
    """Obtiene la instancia singleton del JobsManager"""
    global _jobs_manager_instance
    if _jobs_manager_instance is None:
        _jobs_manager_instance = JobsManager()
        if app:
            _jobs_manager_instance.iniciar(app)
    return _jobs_manager_instance

