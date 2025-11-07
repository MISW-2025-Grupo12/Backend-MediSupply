import os
import uuid
from google.cloud import storage
import logging

logger = logging.getLogger(__name__)

class GCPStorageService:
    """Servicio de almacenamiento en Google Cloud Storage para Productos"""
    
    def __init__(self, bucket_name=None, credentials_path=None):
        try:
            bucket_name = bucket_name or os.getenv('GCP_BUCKET_NAME_PRODUCTOS', os.getenv('GCP_BUCKET_NAME', 'evidencias-g12'))
            
            if credentials_path and os.path.exists(credentials_path):
                self.client = storage.Client.from_service_account_json(credentials_path)
                logger.info(f"GCP Storage inicializado con credenciales: {credentials_path}")
            else:
                # Intentar usar Application Default Credentials (ADC)
                self.client = storage.Client()
                logger.info("GCP Storage inicializado con credenciales por defecto (ADC)")
            
            self.bucket = self.client.bucket(bucket_name)
            self.bucket_name = bucket_name
            logger.info(f"Bucket configurado: {bucket_name}")
        except Exception as e:
            logger.warning(f"Error inicializando GCP Storage: {e}")
            logger.warning("El servicio continuará pero las operaciones de GCP Storage fallarán")
            self.client = None
            self.bucket = None
            self.bucket_name = bucket_name
    
    def guardar_csv_original(self, csv_content: bytes, job_id: str) -> str:
        """Guarda el CSV original en GCP Storage y retorna la URL"""
        if not self.client or not self.bucket:
            raise RuntimeError("GCP Storage no está inicializado. Verifique las credenciales.")
        
        try:
            blob_name = f"productos-carga-masiva/{job_id}/original.csv"
            
            blob = self.bucket.blob(blob_name)
            blob.upload_from_string(csv_content, content_type='text/csv')
            
            logger.info(f"CSV original subido exitosamente: {blob_name}")
            return blob.public_url
        except Exception as e:
            logger.error(f"Error subiendo CSV original a GCP: {e}")
            raise
    
    def guardar_csv_resultado(self, csv_content: bytes, job_id: str) -> str:
        """Guarda el CSV resultado en GCP Storage y retorna la URL"""
        if not self.client or not self.bucket:
            raise RuntimeError("GCP Storage no está inicializado. Verifique las credenciales.")
        
        try:
            blob_name = f"productos-carga-masiva/{job_id}/resultado.csv"
            
            blob = self.bucket.blob(blob_name)
            blob.upload_from_string(csv_content, content_type='text/csv')
            
            logger.info(f"CSV resultado subido exitosamente: {blob_name}")
            return blob.public_url
        except Exception as e:
            logger.error(f"Error subiendo CSV resultado a GCP: {e}")
            raise
    
    def descargar_csv(self, job_id: str) -> bytes:
        """Descarga el CSV original desde GCP Storage"""
        if not self.client or not self.bucket:
            raise RuntimeError("GCP Storage no está inicializado. Verifique las credenciales.")
        
        try:
            blob_name = f"productos-carga-masiva/{job_id}/original.csv"
            blob = self.bucket.blob(blob_name)
            
            if not blob.exists():
                raise FileNotFoundError(f"CSV no encontrado: {blob_name}")
            
            csv_content = blob.download_as_bytes()
            logger.info(f"CSV descargado exitosamente: {blob_name}")
            return csv_content
        except Exception as e:
            logger.error(f"Error descargando CSV desde GCP: {e}")
            raise
    
    def eliminar_archivo(self, url: str) -> bool:
        """Elimina un archivo de GCP Storage"""
        try:
            # Extraer nombre del blob de la URL
            blob_name = url.split(f'/{self.bucket_name}/')[-1]
            blob = self.bucket.blob(blob_name)
            blob.delete()
            logger.info(f"Archivo eliminado: {blob_name}")
            return True
        except Exception as e:
            logger.error(f"Error eliminando archivo: {e}")
            return False

def get_storage_service():
    """
    Obtiene una instancia configurada del servicio de almacenamiento GCP.
    
    Busca credenciales en orden de prioridad:
    1. Variable de entorno GCP_CREDENTIALS_PATH
    2. Docker Secrets: /run/secrets/gcp_credentials
    3. Docker: /app/gcp-credentials.json
    4. Local development: Productos/gcp-credentials.json
    """
    bucket = os.getenv('GCP_BUCKET_NAME_PRODUCTOS', os.getenv('GCP_BUCKET_NAME', 'evidencias-g12'))
    
    # Determinar ruta de credenciales
    if 'GCP_CREDENTIALS_PATH' in os.environ:
        credentials_path = os.getenv('GCP_CREDENTIALS_PATH')
        logger.info("Usando credenciales desde GCP_CREDENTIALS_PATH")
    elif os.path.exists('/run/secrets/gcp_credentials'):
        credentials_path = '/run/secrets/gcp_credentials'
        logger.info("Usando Docker Secrets para credenciales")
    elif os.path.exists('/app/gcp-credentials.json'):
        credentials_path = '/app/gcp-credentials.json'
        logger.info("Usando credenciales desde /app")
    else:
        # Local development
        import os as os_module
        current_dir = os_module.path.dirname(os_module.path.abspath(__file__))
        productos_dir = os_module.path.dirname(os_module.path.dirname(current_dir))
        credentials_path = os_module.path.join(productos_dir, 'gcp-credentials.json')
        logger.info("Usando credenciales de desarrollo local")
    
    logger.info(f"Ruta de credenciales: {credentials_path}")
    logger.info(f"Archivo existe: {os.path.exists(credentials_path) if credentials_path else False}")
    
    if credentials_path and not os.path.exists(credentials_path):
        logger.warning(f"⚠️ Archivo de credenciales no encontrado: {credentials_path}")
        logger.warning(f"Directorio actual: {os.getcwd()}")
    
    return GCPStorageService(bucket, credentials_path)

