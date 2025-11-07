"""Tests para endpoints de carga masiva"""
import pytest
import json
import uuid
import io
import sys
import os
from unittest.mock import Mock, patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from aplicacion.dto import CargaMasivaJobDTO
from infraestructura.repositorios import RepositorioJobSQLite


class TestAPICargaMasiva:
    """Tests para los endpoints de carga masiva"""
    
    @pytest.fixture
    def csv_content(self):
        """Contenido CSV de prueba"""
        return b"""nombre,descripcion,precio,stock,fecha_vencimiento,categoria,proveedor
Paracetamol 500mg,Analgesico,5000,100,2025-12-31,Medicinas,Distribuidora MediPro S.A.S."""
    
    @pytest.fixture
    def csv_content_invalido(self):
        """CSV con columnas faltantes"""
        return b"""nombre,precio
Paracetamol,5000"""
    
    def test_crear_carga_masiva_exitoso(self, client, csv_content):
        """Test creación exitosa de carga masiva"""
        with patch('src.api.producto.get_storage_service') as mock_storage:
            mock_storage_instance = Mock()
            mock_storage_instance.guardar_csv_original.return_value = "https://storage.googleapis.com/test.csv"
            mock_storage.return_value = mock_storage_instance
            
            response = client.post(
                '/productos/api/productos/carga-masiva',
                data={'file': (io.BytesIO(csv_content), 'test.csv')},
                content_type='multipart/form-data'
            )
            
            assert response.status_code == 202
            data = json.loads(response.data)
            assert 'job_id' in data
            assert data['status'] == 'pending'
            assert data['total_filas'] == 1
    
    def test_crear_carga_masiva_sin_archivo(self, client):
        """Test creación sin archivo"""
        response = client.post('/productos/api/productos/carga-masiva')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_crear_carga_masiva_archivo_invalido(self, client, csv_content_invalido):
        """Test creación con archivo inválido"""
        with patch('src.api.producto.ServicioCargaMasiva') as mock_servicio:
            mock_instance = Mock()
            mock_instance.validar_archivo_csv.return_value = (False, "Falta columna requerida")
            mock_servicio.return_value = mock_instance
            
            response = client.post(
                '/productos/api/productos/carga-masiva',
                data={'file': (io.BytesIO(csv_content_invalido), 'test.csv')},
                content_type='multipart/form-data'
            )
            
            assert response.status_code == 400
    
    def test_obtener_estado_carga_masiva_exitoso(self, client, app):
        """Test obtener estado de carga masiva"""
        with app.app_context():
            repositorio = RepositorioJobSQLite()
            job = CargaMasivaJobDTO(
                status='completed',
                total_filas=10,
                filas_procesadas=10,
                filas_exitosas=8,
                filas_error=1,
                filas_rechazadas=1,
                result_url='https://storage.googleapis.com/result.csv'
            )
            
            creado = repositorio.crear(job)
            job_id = str(creado.id)
        
        response = client.get(f'/productos/api/productos/carga-masiva/{job_id}')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['job_id'] == job_id
        assert data['status'] == 'completed'
        assert data['progreso']['total_filas'] == 10
        assert data['progreso']['filas_procesadas'] == 10
        assert 'result_url' in data
    
    def test_obtener_estado_carga_masiva_no_encontrado(self, client):
        """Test obtener estado de job inexistente"""
        job_id = str(uuid.uuid4())
        response = client.get(f'/productos/api/productos/carga-masiva/{job_id}')
        
        assert response.status_code == 404
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_listar_cargas_masivas(self, client, app):
        """Test listar todos los jobs"""
        with app.app_context():
            repositorio = RepositorioJobSQLite()
            
            # Crear varios jobs
            job1 = CargaMasivaJobDTO(status='pending', total_filas=10)
            repositorio.crear(job1)
            
            job2 = CargaMasivaJobDTO(status='completed', total_filas=5)
            repositorio.crear(job2)
        
        response = client.get('/productos/api/productos/carga-masiva?page=1&page_size=10')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'items' in data
        assert 'pagination' in data
        assert len(data['items']) > 0
    
    def test_listar_cargas_masivas_filtrado_por_status(self, client, app):
        """Test listar jobs filtrados por status"""
        with app.app_context():
            repositorio = RepositorioJobSQLite()
            
            # Crear job completado
            job = CargaMasivaJobDTO(status='completed', total_filas=5)
            repositorio.crear(job)
        
        response = client.get('/productos/api/productos/carga-masiva?status=completed')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'items' in data
        assert all(item['status'] == 'completed' for item in data['items'])
    
    def test_listar_cargas_masivas_status_invalido(self, client):
        """Test listar con status inválido"""
        response = client.get('/productos/api/productos/carga-masiva?status=invalid')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert 'status' in data['error'].lower()

