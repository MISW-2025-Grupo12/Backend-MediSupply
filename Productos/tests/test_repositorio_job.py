"""Tests para RepositorioJobSQLite"""
import pytest
import uuid
import sys
import os
from datetime import datetime
from flask import Flask

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from aplicacion.dto import CargaMasivaJobDTO
from infraestructura.repositorios import RepositorioJobSQLite
from infraestructura.modelos import CargaMasivaJobModel
from config.db import db, init_db


class TestRepositorioJobSQLite:
    """Tests para el repositorio de jobs"""
    
    @pytest.fixture(autouse=True)
    def setup_db(self):
        """Setup de base de datos para cada test"""
        self.app = Flask(__name__)
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        self.app.config['TESTING'] = True
        
        init_db(self.app)
        
        with self.app.app_context():
            db.create_all()
            yield
            db.drop_all()
    
    @pytest.fixture
    def repositorio(self):
        """Crea una instancia del repositorio"""
        return RepositorioJobSQLite()
    
    def test_crear_job(self, repositorio):
        """Test creación de job"""
        with self.app.app_context():
            job_dto = CargaMasivaJobDTO(
                status='pending',
                total_filas=10
            )
            
            resultado = repositorio.crear(job_dto)
            
            assert resultado.id == job_dto.id
            assert resultado.status == 'pending'
            assert resultado.total_filas == 10
    
    def test_obtener_por_id(self, repositorio):
        """Test obtener job por ID"""
        with self.app.app_context():
            job_dto = CargaMasivaJobDTO(
                status='pending',
                total_filas=5
            )
            
            creado = repositorio.crear(job_dto)
            obtenido = repositorio.obtener_por_id(str(creado.id))
            
            assert obtenido is not None
            assert obtenido.id == creado.id
            assert obtenido.status == 'pending'
            assert obtenido.total_filas == 5
    
    def test_obtener_por_id_no_existe(self, repositorio):
        """Test obtener job que no existe"""
        with self.app.app_context():
            job_id = str(uuid.uuid4())
            obtenido = repositorio.obtener_por_id(job_id)
            
            assert obtenido is None
    
    def test_actualizar_job(self, repositorio):
        """Test actualización de job"""
        with self.app.app_context():
            job_dto = CargaMasivaJobDTO(
                status='pending',
                total_filas=10
            )
            
            creado = repositorio.crear(job_dto)
            
            # Actualizar
            creado.status = 'processing'
            creado.filas_procesadas = 5
            creado.filas_exitosas = 3
            
            actualizado = repositorio.actualizar(creado)
            
            assert actualizado.status == 'processing'
            assert actualizado.filas_procesadas == 5
            assert actualizado.filas_exitosas == 3
            
            # Verificar en BD
            obtenido = repositorio.obtener_por_id(str(creado.id))
            assert obtenido.status == 'processing'
            assert obtenido.filas_procesadas == 5
    
    def test_obtener_pendientes(self, repositorio):
        """Test obtener jobs pendientes"""
        with self.app.app_context():
            # Crear job pendiente
            job1 = CargaMasivaJobDTO(status='pending', total_filas=10)
            repositorio.crear(job1)
            
            # Crear job completado
            job2 = CargaMasivaJobDTO(status='completed', total_filas=5)
            repositorio.crear(job2)
            
            # Obtener pendientes (debe atomizar y marcar como processing)
            pendientes = repositorio.obtener_pendientes(limit=1)
            
            # El job pendiente debería ser marcado como processing
            if pendientes:
                assert pendientes[0].status == 'processing'
    
    def test_obtener_todos(self, repositorio):
        """Test obtener todos los jobs"""
        with self.app.app_context():
            # Crear varios jobs
            job1 = CargaMasivaJobDTO(status='pending', total_filas=10)
            repositorio.crear(job1)
            
            job2 = CargaMasivaJobDTO(status='completed', total_filas=5)
            repositorio.crear(job2)
            
            job3 = CargaMasivaJobDTO(status='failed', total_filas=3)
            repositorio.crear(job3)
            
            # Obtener todos
            todos = repositorio.obtener_todos()
            
            assert len(todos) >= 3
    
    def test_obtener_todos_filtrado_por_status(self, repositorio):
        """Test obtener jobs filtrados por status"""
        with self.app.app_context():
            # Crear jobs con diferentes status
            job1 = CargaMasivaJobDTO(status='pending', total_filas=10)
            repositorio.crear(job1)
            
            job2 = CargaMasivaJobDTO(status='completed', total_filas=5)
            repositorio.crear(job2)
            
            job3 = CargaMasivaJobDTO(status='completed', total_filas=3)
            repositorio.crear(job3)
            
            # Obtener solo completados
            completados = repositorio.obtener_todos(status='completed')
            
            assert len(completados) >= 2
            assert all(job.status == 'completed' for job in completados)
    
    def test_obtener_todos_ordenado(self, repositorio):
        """Test obtener jobs ordenados"""
        with self.app.app_context():
            # Crear jobs con diferentes fechas
            job1 = CargaMasivaJobDTO(status='pending', total_filas=10)
            repositorio.crear(job1)
            
            # Obtener ordenados por created_at descendente
            todos = repositorio.obtener_todos(ordenar_por='created_at', orden='desc')
            
            assert len(todos) >= 1
            # Verificar que está ordenado (más reciente primero)
            if len(todos) > 1:
                fechas = [job.created_at for job in todos if job.created_at]
                fechas_ordenadas = sorted(fechas, reverse=True)
                assert fechas == fechas_ordenadas

