"""Tests para la API de sugerencias"""
import pytest
import uuid
import sys
import os
import json
from unittest.mock import patch, Mock
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from api import create_app
from config.db import db
from aplicacion.dto import SugerenciaClienteDTO


class TestAPISugerencias:
    """Tests para los endpoints de sugerencias"""
    
    def setup_method(self):
        """Configuración antes de cada test"""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.client = self.app.test_client()
        
        with self.app.app_context():
            db.create_all()
    
    def teardown_method(self):
        """Limpieza después de cada test"""
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
    
    @patch.dict(os.environ, {'GOOGLE_CLOUD_API_KEY': 'test-api-key'})
    def test_generar_sugerencias_exitoso(self):
        """Test generar sugerencias exitosamente"""
        import api.sugerencias as sugerencias_module
        visita_id = str(uuid.uuid4())
        cliente_id = str(uuid.uuid4())
        
        # Mock de sugerencia generada
        sugerencia_dto = SugerenciaClienteDTO(
            cliente_id=cliente_id,
            evidencia_id=None,
            sugerencias_texto='Sugerencias de prueba',
            modelo_usado='gemini-2.5-flash-lite'
        )
        
        # Mockear ejecutar_comando en el módulo donde se usa
        with patch.object(sugerencias_module, 'ejecutar_comando', return_value=sugerencia_dto):
            response = self.client.post(f'/ventas/api/visitas/{visita_id}/sugerencias')
            
            assert response.status_code == 201
            data = json.loads(response.data)
            assert data['mensaje'] == 'Sugerencias generadas exitosamente'
            assert data['visita_id'] == visita_id
            assert data['sugerencia']['cliente_id'] == cliente_id
            assert data['sugerencia']['sugerencias_texto'] == 'Sugerencias de prueba'
    
    @patch.dict(os.environ, {'GOOGLE_CLOUD_API_KEY': 'test-api-key'})
    def test_generar_sugerencias_visita_no_encontrada(self):
        """Test generar sugerencias cuando la visita no existe"""
        import api.sugerencias as sugerencias_module
        visita_id = str(uuid.uuid4())
        
        # Mock de la función ejecutar_comando para que lance ValueError
        with patch.object(sugerencias_module, 'ejecutar_comando', side_effect=ValueError(f"Visita {visita_id} no encontrada")):
            response = self.client.post(f'/ventas/api/visitas/{visita_id}/sugerencias')
            
            assert response.status_code == 404
            data = json.loads(response.data)
            assert 'error' in data
            assert 'no encontrada' in data['error'].lower()
    
    @patch.dict(os.environ, {'GOOGLE_CLOUD_API_KEY': 'test-api-key'})
    def test_generar_sugerencias_error_interno(self):
        """Test generar sugerencias con error interno"""
        import api.sugerencias as sugerencias_module
        visita_id = str(uuid.uuid4())
        
        # Mock de la función ejecutar_comando para que lance Exception
        with patch.object(sugerencias_module, 'ejecutar_comando', side_effect=Exception("Error interno")):
            response = self.client.post(f'/ventas/api/visitas/{visita_id}/sugerencias')
            
            assert response.status_code == 500
            data = json.loads(response.data)
            assert 'error' in data
            assert 'Error interno del servidor' in data['error']
    
    @patch('api.sugerencias.RepositorioSugerenciaCliente')
    def test_obtener_sugerencias_cliente(self, mock_repositorio_class):
        """Test obtener sugerencias de un cliente"""
        cliente_id = str(uuid.uuid4())
        
        # Mock del repositorio
        mock_repositorio = Mock()
        mock_repositorio_class.return_value = mock_repositorio
        
        # Mock de sugerencias
        sugerencias = [
            SugerenciaClienteDTO(
                cliente_id=cliente_id,
                evidencia_id=None,
                sugerencias_texto='Sugerencia 1',
                modelo_usado='gemini-2.5-flash-lite',
                created_at=datetime.now()
            ),
            SugerenciaClienteDTO(
                cliente_id=cliente_id,
                evidencia_id=str(uuid.uuid4()),
                sugerencias_texto='Sugerencia 2',
                modelo_usado='gemini-2.5-flash-lite',
                created_at=datetime.now()
            )
        ]
        mock_repositorio.obtener_por_cliente_id.return_value = sugerencias
        
        response = self.client.get(f'/ventas/api/clientes/{cliente_id}/sugerencias')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['cliente_id'] == cliente_id
        assert data['total'] == 2
        assert len(data['sugerencias']) == 2
        assert data['sugerencias'][0]['sugerencias_texto'] == 'Sugerencia 1'
        assert data['sugerencias'][1]['sugerencias_texto'] == 'Sugerencia 2'
    
    @patch('api.sugerencias.RepositorioSugerenciaCliente')
    def test_obtener_sugerencias_cliente_vacio(self, mock_repositorio_class):
        """Test obtener sugerencias de un cliente sin sugerencias"""
        cliente_id = str(uuid.uuid4())
        
        # Mock del repositorio
        mock_repositorio = Mock()
        mock_repositorio_class.return_value = mock_repositorio
        mock_repositorio.obtener_por_cliente_id.return_value = []
        
        response = self.client.get(f'/ventas/api/clientes/{cliente_id}/sugerencias')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['cliente_id'] == cliente_id
        assert data['total'] == 0
        assert len(data['sugerencias']) == 0
    
    @patch('api.sugerencias.RepositorioSugerenciaCliente')
    def test_obtener_sugerencias_error(self, mock_repositorio_class):
        """Test obtener sugerencias con error"""
        cliente_id = str(uuid.uuid4())
        
        # Mock del repositorio que lanza excepción
        mock_repositorio = Mock()
        mock_repositorio_class.return_value = mock_repositorio
        mock_repositorio.obtener_por_cliente_id.side_effect = Exception("Error de BD")
        
        response = self.client.get(f'/ventas/api/clientes/{cliente_id}/sugerencias')
        
        assert response.status_code == 500
        data = json.loads(response.data)
        assert 'error' in data
        assert 'Error interno del servidor' in data['error']

