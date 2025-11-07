"""Tests para GCPStorageService"""
import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from infraestructura.servicio_gcp_storage import GCPStorageService, get_storage_service


class TestGCPStorageService:
    """Tests para el servicio de GCP Storage"""
    
    @patch('infraestructura.servicio_gcp_storage.os.path.exists')
    @patch('infraestructura.servicio_gcp_storage.storage.Client')
    def test_init_con_credenciales_existentes(self, mock_client_class, mock_exists):
        """Test inicialización con credenciales existentes"""
        mock_exists.return_value = True
        mock_client = Mock()
        mock_bucket = Mock()
        mock_client.bucket.return_value = mock_bucket
        mock_client_class.from_service_account_json.return_value = mock_client
        
        servicio = GCPStorageService(
            bucket_name='test-bucket',
            credentials_path='/path/to/credentials.json'
        )
        
        assert servicio.bucket_name == 'test-bucket'
        assert servicio.client == mock_client
        assert servicio.bucket == mock_bucket
        mock_client_class.from_service_account_json.assert_called_once_with('/path/to/credentials.json')
    
    @patch('infraestructura.servicio_gcp_storage.storage.Client')
    def test_init_sin_credenciales(self, mock_client_class):
        """Test inicialización sin credenciales (usando ADC)"""
        mock_client = Mock()
        mock_bucket = Mock()
        mock_client.bucket.return_value = mock_bucket
        mock_client_class.return_value = mock_client
        
        servicio = GCPStorageService(bucket_name='test-bucket')
        
        assert servicio.bucket_name == 'test-bucket'
        assert servicio.client == mock_client
        mock_client_class.assert_called_once()
    
    @patch('infraestructura.servicio_gcp_storage.storage.Client')
    def test_init_error(self, mock_client_class):
        """Test inicialización con error"""
        mock_client_class.side_effect = Exception("Error de conexión")
        
        servicio = GCPStorageService(bucket_name='test-bucket')
        
        assert servicio.client is None
        assert servicio.bucket is None
        assert servicio.bucket_name == 'test-bucket'
    
    @patch('infraestructura.servicio_gcp_storage.storage.Client')
    def test_guardar_csv_original_exitoso(self, mock_client_class):
        """Test guardar CSV original exitosamente"""
        mock_client = Mock()
        mock_bucket = Mock()
        mock_blob = Mock()
        mock_blob.public_url = 'https://storage.googleapis.com/test-url'
        
        mock_bucket.blob.return_value = mock_blob
        mock_client.bucket.return_value = mock_bucket
        mock_client_class.return_value = mock_client
        
        servicio = GCPStorageService(bucket_name='test-bucket')
        csv_content = b"nombre,precio\nProducto,1000"
        job_id = "test-job-id"
        
        url = servicio.guardar_csv_original(csv_content, job_id)
        
        assert url == 'https://storage.googleapis.com/test-url'
        mock_blob.upload_from_string.assert_called_once_with(csv_content, content_type='text/csv')
    
    @patch('infraestructura.servicio_gcp_storage.storage.Client')
    def test_guardar_csv_original_sin_inicializar(self, mock_client_class):
        """Test guardar CSV cuando no está inicializado"""
        mock_client_class.side_effect = Exception("Error")
        servicio = GCPStorageService(bucket_name='test-bucket')
        
        with pytest.raises(RuntimeError, match="no está inicializado"):
            servicio.guardar_csv_original(b"content", "job-id")
    
    @patch('infraestructura.servicio_gcp_storage.storage.Client')
    def test_guardar_csv_resultado_exitoso(self, mock_client_class):
        """Test guardar CSV resultado exitosamente"""
        mock_client = Mock()
        mock_bucket = Mock()
        mock_blob = Mock()
        mock_blob.public_url = 'https://storage.googleapis.com/result-url'
        
        mock_bucket.blob.return_value = mock_blob
        mock_client.bucket.return_value = mock_bucket
        mock_client_class.return_value = mock_client
        
        servicio = GCPStorageService(bucket_name='test-bucket')
        csv_content = b"nombre,status\nProducto,creado"
        job_id = "test-job-id"
        
        url = servicio.guardar_csv_resultado(csv_content, job_id)
        
        assert url == 'https://storage.googleapis.com/result-url'
        mock_blob.upload_from_string.assert_called_once_with(csv_content, content_type='text/csv')
    
    @patch('infraestructura.servicio_gcp_storage.storage.Client')
    def test_descargar_csv_exitoso(self, mock_client_class):
        """Test descargar CSV exitosamente"""
        mock_client = Mock()
        mock_bucket = Mock()
        mock_blob = Mock()
        mock_blob.exists.return_value = True
        mock_blob.download_as_bytes.return_value = b"nombre,precio\nProducto,1000"
        
        mock_bucket.blob.return_value = mock_blob
        mock_client.bucket.return_value = mock_bucket
        mock_client_class.return_value = mock_client
        
        servicio = GCPStorageService(bucket_name='test-bucket')
        job_id = "test-job-id"
        
        content = servicio.descargar_csv(job_id)
        
        assert content == b"nombre,precio\nProducto,1000"
        mock_blob.exists.assert_called_once()
    
    @patch('infraestructura.servicio_gcp_storage.storage.Client')
    def test_descargar_csv_no_encontrado(self, mock_client_class):
        """Test descargar CSV que no existe"""
        mock_client = Mock()
        mock_bucket = Mock()
        mock_blob = Mock()
        mock_blob.exists.return_value = False
        
        mock_bucket.blob.return_value = mock_blob
        mock_client.bucket.return_value = mock_bucket
        mock_client_class.return_value = mock_client
        
        servicio = GCPStorageService(bucket_name='test-bucket')
        job_id = "test-job-id"
        
        with pytest.raises(FileNotFoundError):
            servicio.descargar_csv(job_id)
    
    @patch('infraestructura.servicio_gcp_storage.storage.Client')
    def test_eliminar_archivo_exitoso(self, mock_client_class):
        """Test eliminar archivo exitosamente"""
        mock_client = Mock()
        mock_bucket = Mock()
        mock_blob = Mock()
        
        mock_bucket.blob.return_value = mock_blob
        mock_client.bucket.return_value = mock_bucket
        mock_client_class.return_value = mock_client
        
        servicio = GCPStorageService(bucket_name='test-bucket')
        url = 'https://storage.googleapis.com/test-bucket/path/to/file.csv'
        
        resultado = servicio.eliminar_archivo(url)
        
        assert resultado is True
        mock_blob.delete.assert_called_once()
    
    @patch('infraestructura.servicio_gcp_storage.storage.Client')
    def test_eliminar_archivo_error(self, mock_client_class):
        """Test eliminar archivo con error"""
        mock_client = Mock()
        mock_bucket = Mock()
        mock_blob = Mock()
        mock_blob.delete.side_effect = Exception("Error al eliminar")
        
        mock_bucket.blob.return_value = mock_blob
        mock_client.bucket.return_value = mock_bucket
        mock_client_class.return_value = mock_client
        
        servicio = GCPStorageService(bucket_name='test-bucket')
        url = 'https://storage.googleapis.com/test-bucket/path/to/file.csv'
        
        resultado = servicio.eliminar_archivo(url)
        
        assert resultado is False


class TestGetStorageService:
    """Tests para get_storage_service"""
    
    @patch.dict(os.environ, {'GCP_CREDENTIALS_PATH': '/path/to/creds.json'}, clear=False)
    @patch('infraestructura.servicio_gcp_storage.GCPStorageService')
    def test_get_storage_service_con_env(self, mock_service_class):
        """Test get_storage_service con variable de entorno"""
        mock_service = Mock()
        mock_service_class.return_value = mock_service
        
        resultado = get_storage_service()
        
        assert resultado == mock_service
        mock_service_class.assert_called_once()
    
    @patch.dict(os.environ, {}, clear=False)
    @patch('os.path.exists')
    @patch('infraestructura.servicio_gcp_storage.GCPStorageService')
    def test_get_storage_service_sin_credenciales(self, mock_service_class, mock_exists):
        """Test get_storage_service sin credenciales"""
        mock_exists.return_value = False
        mock_service = Mock()
        mock_service_class.return_value = mock_service
        
        resultado = get_storage_service()
        
        assert resultado == mock_service
        mock_service_class.assert_called_once()

