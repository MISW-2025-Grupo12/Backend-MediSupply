import os
import uuid
from google.cloud import storage
import logging

logger = logging.getLogger(__name__)

class GCPStorageService:
    """Servicio de almacenamiento en Google Cloud Storage"""
    
    def __init__(self, bucket_name='evidencias-g12', credentials_path=None):
        try:
            if credentials_path and os.path.exists(credentials_path):
                self.client = storage.Client.from_service_account_json(credentials_path)
                logger.info(f"GCP Storage inicializado con credenciales: {credentials_path}")
            else:
                self.client = storage.Client()
                logger.info("GCP Storage inicializado con credenciales por defecto")
            
            self.bucket = self.client.bucket(bucket_name)
            self.bucket_name = bucket_name
            logger.info(f"Bucket configurado: {bucket_name}")
        except Exception as e:
            logger.error(f"Error inicializando GCP Storage: {e}")
            raise
    
    def guardar_archivo(self, file_data: bytes, filename: str, content_type: str) -> str:
        """Guarda un archivo en GCP Storage y retorna la URL pública"""
        try:
            # Generar nombre único
            extension = filename.rsplit('.', 1)[-1] if '.' in filename else ''
            blob_name = f"evidencias/{uuid.uuid4()}.{extension}"
            
            # Crear blob y subir
            blob = self.bucket.blob(blob_name)
            blob.upload_from_string(file_data, content_type=content_type)
            
            logger.info(f"Archivo subido exitosamente: {blob_name}")
            return blob.public_url
        
        except Exception as e:
            logger.error(f"Error subiendo archivo a GCP: {e}")
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
    4. Local development: Ventas/gcp-credentials.json
    """
    bucket = os.getenv('GCP_BUCKET_NAME', 'evidencias-g12')
    
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
        current_dir = os.path.dirname(os.path.abspath(__file__))
        ventas_dir = os.path.dirname(os.path.dirname(current_dir))
        credentials_path = os.path.join(ventas_dir, 'gcp-credentials.json')
        logger.info("Usando credenciales de desarrollo local")
    
    logger.info(f"Ruta de credenciales: {credentials_path}")
    logger.info(f"Archivo existe: {os.path.exists(credentials_path)}")
    
    if not os.path.exists(credentials_path):
        logger.error(f"⚠️ Archivo de credenciales no encontrado: {credentials_path}")
        logger.error(f"Directorio actual: {os.getcwd()}")
    
    return GCPStorageService(bucket, credentials_path)

