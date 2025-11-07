"""Tests para ProcesarCargaMasiva command handler"""
import pytest
import sys
import os
import uuid
from unittest.mock import Mock, patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from aplicacion.comandos.procesar_carga_masiva import ProcesarCargaMasiva, ProcesarCargaMasivaHandler
from aplicacion.dto import CargaMasivaJobDTO
from infraestructura.repositorios import RepositorioJobSQLite
from aplicacion.servicios.servicio_carga_masiva import ServicioCargaMasiva


class TestProcesarCargaMasivaHandler:
    """Tests para el handler de ProcesarCargaMasiva"""
    
    @pytest.fixture
    def mock_repositorio(self):
        """Mock del repositorio de jobs"""
        return Mock(spec=RepositorioJobSQLite)
    
    @pytest.fixture
    def mock_servicio_carga(self):
        """Mock del servicio de carga masiva"""
        return Mock(spec=ServicioCargaMasiva)
    
    @pytest.fixture
    def mock_servicio_storage(self):
        """Mock del servicio de storage"""
        mock_storage = Mock()
        mock_storage.descargar_csv.return_value = b"nombre,descripcion,precio,stock,fecha_vencimiento,categoria,proveedor\nProducto,Desc,1000,10,2025-12-31,Medicinas,Proveedor"
        mock_storage.guardar_csv_resultado.return_value = "https://storage.googleapis.com/result.csv"
        return mock_storage
    
    def test_handle_job_no_encontrado(self, mock_repositorio, mock_servicio_carga, mock_servicio_storage):
        """Test cuando el job no existe"""
        mock_repositorio.obtener_por_id.return_value = None
        
        handler = ProcesarCargaMasivaHandler(
            repositorio_job=mock_repositorio,
            servicio_carga=mock_servicio_carga,
            servicio_storage=mock_servicio_storage
        )
        
        comando = ProcesarCargaMasiva(job_id=str(uuid.uuid4()))
        
        with pytest.raises(ValueError, match="no encontrado"):
            handler.handle(comando)
    
    def test_handle_procesamiento_exitoso(self, mock_repositorio, mock_servicio_carga, mock_servicio_storage):
        """Test procesamiento exitoso de un job"""
        job = CargaMasivaJobDTO(
            status='pending',
            total_filas=1
        )
        mock_repositorio.obtener_por_id.return_value = job
        
        # Mock parsear CSV
        filas_normalizadas = [{'nombre': 'Producto', 'precio': '1000', 'stock': '10', 'fecha_vencimiento': '2025-12-31', 'categoria': 'Medicinas', 'proveedor': 'Proveedor', 'descripcion': 'Desc'}]
        headers_originales = ['nombre', 'descripcion', 'precio', 'stock', 'fecha_vencimiento', 'categoria', 'proveedor']
        mapeo_headers = {h.lower().strip(): h for h in headers_originales}
        
        mock_servicio_carga.parsear_csv.return_value = (filas_normalizadas, headers_originales, mapeo_headers)
        
        # Mock procesar fila
        mock_servicio_carga.procesar_fila.return_value = {
            'status': 'creado',
            'mensaje': 'Producto creado exitosamente'
        }
        
        # Mock generar CSV resultado
        mock_servicio_carga.generar_csv_resultado.return_value = b"nombre,status\nProducto,creado"
        
        handler = ProcesarCargaMasivaHandler(
            repositorio_job=mock_repositorio,
            servicio_carga=mock_servicio_carga,
            servicio_storage=mock_servicio_storage
        )
        
        comando = ProcesarCargaMasiva(job_id=str(uuid.uuid4()))
        resultado = handler.handle(comando)
        
        assert resultado.status == 'completed'
        assert resultado.filas_exitosas == 1
        assert resultado.filas_procesadas == 1
        assert resultado.result_url == "https://storage.googleapis.com/result.csv"
        mock_servicio_storage.descargar_csv.assert_called_once()
        mock_servicio_storage.guardar_csv_resultado.assert_called_once()
    
    def test_handle_actualizar_status_a_processing(self, mock_repositorio, mock_servicio_carga, mock_servicio_storage):
        """Test que actualiza status a processing si no está en processing"""
        job = CargaMasivaJobDTO(
            status='pending',
            total_filas=1
        )
        mock_repositorio.obtener_por_id.return_value = job
        
        # Mock parsear CSV
        filas_normalizadas = [{'nombre': 'Producto', 'precio': '1000'}]
        headers_originales = ['nombre', 'precio']
        mapeo_headers = {}
        
        mock_servicio_carga.parsear_csv.return_value = (filas_normalizadas, headers_originales, mapeo_headers)
        mock_servicio_carga.procesar_fila.return_value = {'status': 'creado'}
        mock_servicio_carga.generar_csv_resultado.return_value = b"content"
        
        handler = ProcesarCargaMasivaHandler(
            repositorio_job=mock_repositorio,
            servicio_carga=mock_servicio_carga,
            servicio_storage=mock_servicio_storage
        )
        
        comando = ProcesarCargaMasiva(job_id=str(uuid.uuid4()))
        handler.handle(comando)
        
        # Verificar que se actualizó el status
        assert mock_repositorio.actualizar.called
    
    def test_handle_con_filas_rechazadas(self, mock_repositorio, mock_servicio_carga, mock_servicio_storage):
        """Test procesamiento con filas rechazadas"""
        job = CargaMasivaJobDTO(
            status='processing',
            total_filas=2
        )
        mock_repositorio.obtener_por_id.return_value = job
        
        filas_normalizadas = [
            {'nombre': 'Producto1', 'precio': '1000'},
            {'nombre': 'Producto2', 'precio': '2000'}
        ]
        headers_originales = ['nombre', 'precio']
        mapeo_headers = {}
        
        mock_servicio_carga.parsear_csv.return_value = (filas_normalizadas, headers_originales, mapeo_headers)
        mock_servicio_carga.procesar_fila.side_effect = [
            {'status': 'creado'},
            {'status': 'rechazado'}
        ]
        mock_servicio_carga.generar_csv_resultado.return_value = b"content"
        
        handler = ProcesarCargaMasivaHandler(
            repositorio_job=mock_repositorio,
            servicio_carga=mock_servicio_carga,
            servicio_storage=mock_servicio_storage
        )
        
        comando = ProcesarCargaMasiva(job_id=str(uuid.uuid4()))
        resultado = handler.handle(comando)
        
        assert resultado.filas_exitosas == 1
        assert resultado.filas_rechazadas == 1
        assert resultado.filas_procesadas == 2
    
    def test_handle_con_error(self, mock_repositorio, mock_servicio_carga, mock_servicio_storage):
        """Test manejo de error durante procesamiento"""
        job = CargaMasivaJobDTO(
            status='processing',
            total_filas=1
        )
        mock_repositorio.obtener_por_id.return_value = job
        
        mock_servicio_storage.descargar_csv.side_effect = Exception("Error descargando CSV")
        
        handler = ProcesarCargaMasivaHandler(
            repositorio_job=mock_repositorio,
            servicio_carga=mock_servicio_carga,
            servicio_storage=mock_servicio_storage
        )
        
        comando = ProcesarCargaMasiva(job_id=str(uuid.uuid4()))
        
        with pytest.raises(Exception):
            handler.handle(comando)
        
        # Verificar que se actualizó el job como fallido
        assert mock_repositorio.actualizar.called
        # El job debería estar marcado como failed
        call_args = mock_repositorio.actualizar.call_args
        if call_args:
            job_actualizado = call_args[0][0] if call_args[0] else None
            if job_actualizado:
                assert job_actualizado.status == 'failed'
    
    def test_handle_actualizar_cada_10_filas(self, mock_repositorio, mock_servicio_carga, mock_servicio_storage):
        """Test que actualiza BD cada 10 filas"""
        job = CargaMasivaJobDTO(
            status='processing',
            total_filas=15
        )
        mock_repositorio.obtener_por_id.return_value = job
        
        # Crear 15 filas
        filas_normalizadas = [{'nombre': f'Producto{i}', 'precio': '1000'} for i in range(15)]
        headers_originales = ['nombre', 'precio']
        mapeo_headers = {}
        
        mock_servicio_carga.parsear_csv.return_value = (filas_normalizadas, headers_originales, mapeo_headers)
        mock_servicio_carga.procesar_fila.return_value = {'status': 'creado'}
        mock_servicio_carga.generar_csv_resultado.return_value = b"content"
        
        handler = ProcesarCargaMasivaHandler(
            repositorio_job=mock_repositorio,
            servicio_carga=mock_servicio_carga,
            servicio_storage=mock_servicio_storage
        )
        
        comando = ProcesarCargaMasiva(job_id=str(uuid.uuid4()))
        handler.handle(comando)
        
        # Debería actualizar al menos 2 veces (en fila 10 y al final)
        assert mock_repositorio.actualizar.call_count >= 2

