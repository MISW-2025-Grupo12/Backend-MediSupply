import os
import uuid
from abc import ABC, abstractmethod
from google.cloud import storage
import logging

logger = logging.getLogger(__name__)

class StorageService(ABC):
    @abstractmethod
    def guardar_archivo(self, file_data: bytes, filename: str, content_type: str) -> str:
        pass
    
    @abstractmethod
    def eliminar_archivo(self, url: str) -> bool:
        pass

class GCPStorageService(StorageService):
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

class LocalStorageService(StorageService):
    def __init__(self, upload_dir='uploads/evidencias'):
        self.upload_dir = upload_dir
        os.makedirs(upload_dir, exist_ok=True)
        logger.info(f"Storage local configurado: {upload_dir}")
    
    def guardar_archivo(self, file_data: bytes, filename: str, content_type: str) -> str:
        try:
            unique_filename = f"{uuid.uuid4()}_{filename}"
            filepath = os.path.join(self.upload_dir, unique_filename)
            
            with open(filepath, 'wb') as f:
                f.write(file_data)
            
            logger.info(f"Archivo guardado localmente: {filepath}")
            return f"/uploads/evidencias/{unique_filename}"
        except Exception as e:
            logger.error(f"Error guardando archivo localmente: {e}")
            raise
    
    def eliminar_archivo(self, url: str) -> bool:
        try:
            filename = url.split('/')[-1]
            filepath = os.path.join(self.upload_dir, filename)
            if os.path.exists(filepath):
                os.remove(filepath)
                return True
            return False
        except Exception as e:
            logger.error(f"Error eliminando archivo: {e}")
            return False

def get_storage_service():
    mode = os.getenv('STORAGE_MODE', 'gcp')
    
    if mode == 'local':
        logger.info("Usando almacenamiento LOCAL")
        return LocalStorageService()
    else:
        logger.info("Usando almacenamiento GCP")
        bucket = os.getenv('GCP_BUCKET_NAME', 'evidencias-g12')
        
        # Determinar ruta de credenciales
        # Prioridad:
        # 1. Variable de entorno GCP_CREDENTIALS_PATH (puede ser Docker Secret)
        # 2. Docker Secret: /run/secrets/gcp_credentials
        # 3. Docker (legacy): /app/gcp-credentials.json
        # 4. Local: Ventas/gcp-credentials.json (calculado desde este archivo)
        
        if 'GCP_CREDENTIALS_PATH' in os.environ:
            credentials_path = os.getenv('GCP_CREDENTIALS_PATH')
        elif os.path.exists('/run/secrets/gcp_credentials'):
            # Docker Secrets (recomendado)
            credentials_path = '/run/secrets/gcp_credentials'
            logger.info("Usando Docker Secrets para credenciales")
        elif os.path.exists('/app/gcp-credentials.json'):
            # Docker legacy
            credentials_path = '/app/gcp-credentials.json'
            logger.warning("Usando credenciales desde /app (legacy). Considera usar Docker Secrets")
        else:
            # Local development
            current_dir = os.path.dirname(os.path.abspath(__file__))
            ventas_dir = os.path.dirname(os.path.dirname(current_dir))  # Subir dos niveles
            credentials_path = os.path.join(ventas_dir, 'gcp-credentials.json')
        
        logger.info(f"Buscando credenciales en: {credentials_path}")
        logger.info(f"¿Archivo existe? {os.path.exists(credentials_path)}")
        
        if not os.path.exists(credentials_path):
            logger.error(f"Archivo de credenciales no encontrado en: {credentials_path}")
            logger.error(f"Directorio actual: {os.getcwd()}")
            if os.path.exists('/run/secrets'):
                logger.error(f"Contenido de /run/secrets: {os.listdir('/run/secrets')}")
            if os.path.exists('/app'):
                logger.error(f"Contenido de /app: {os.listdir('/app')}")
        
        return GCPStorageService(bucket, credentials_path)

