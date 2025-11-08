"""Tests para el servicio de Vertex AI"""
import pytest
import os
import sys
from unittest.mock import patch, Mock
import requests

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from infraestructura.servicio_vertex_ai import ServicioVertexAI


class TestServicioVertexAI:
    """Tests para el servicio de Vertex AI"""
    
    def setup_method(self):
        """Configuración antes de cada test"""
        # Establecer variable de entorno para API key
        os.environ['GOOGLE_CLOUD_API_KEY'] = 'test-api-key-123'
        os.environ.pop('VERTEX_MODEL_NAME', None)  # Usar default
    
    def teardown_method(self):
        """Limpieza después de cada test"""
        os.environ.pop('GOOGLE_CLOUD_API_KEY', None)
        os.environ.pop('VERTEX_MODEL_NAME', None)
    
    def test_init_sin_api_key(self):
        """Test que falla si no hay API key"""
        os.environ.pop('GOOGLE_CLOUD_API_KEY', None)
        with pytest.raises(RuntimeError, match="GOOGLE_CLOUD_API_KEY no está configurada"):
            ServicioVertexAI()
    
    def test_init_con_api_key(self):
        """Test inicialización exitosa con API key"""
        servicio = ServicioVertexAI()
        assert servicio.api_key == 'test-api-key-123'
        assert servicio.base_model == 'gemini-2.5-flash-lite'
        assert 'aiplatform.googleapis.com' in servicio.endpoint
    
    def test_init_con_modelo_personalizado(self):
        """Test inicialización con modelo personalizado"""
        os.environ['VERTEX_MODEL_NAME'] = 'gemini-pro'
        servicio = ServicioVertexAI()
        assert servicio.base_model == 'gemini-pro'
        assert 'gemini-pro' in servicio.endpoint
    
    def test_obtener_mime_type_jpg(self):
        """Test obtener MIME type para JPG"""
        servicio = ServicioVertexAI()
        assert servicio.obtener_mime_type('jpg') == 'image/jpeg'
        assert servicio.obtener_mime_type('JPG') == 'image/jpeg'
        assert servicio.obtener_mime_type('jpeg') == 'image/jpeg'
    
    def test_obtener_mime_type_png(self):
        """Test obtener MIME type para PNG"""
        servicio = ServicioVertexAI()
        assert servicio.obtener_mime_type('png') == 'image/png'
    
    def test_obtener_mime_type_mp4(self):
        """Test obtener MIME type para MP4"""
        servicio = ServicioVertexAI()
        assert servicio.obtener_mime_type('mp4') == 'video/mp4'
    
    def test_obtener_mime_type_desconocido(self):
        """Test obtener MIME type para formato desconocido"""
        servicio = ServicioVertexAI()
        assert servicio.obtener_mime_type('unknown') == 'application/octet-stream'
    
    def test_construir_parte_archivo_sin_url(self):
        """Test construir parte de archivo sin URL"""
        servicio = ServicioVertexAI()
        resultado = servicio._construir_parte_archivo(None, 'image/jpeg')
        assert resultado is None
        
        resultado = servicio._construir_parte_archivo('https://example.com/image.jpg', None)
        assert resultado is None
    
    def test_construir_parte_archivo_gcs_https(self):
        """Test construir parte de archivo con URL de GCS HTTPS"""
        servicio = ServicioVertexAI()
        url = 'https://storage.googleapis.com/bucket/file.jpg'
        resultado = servicio._construir_parte_archivo(url, 'image/jpeg')
        
        assert resultado is not None
        assert resultado['file_data']['mime_type'] == 'image/jpeg'
        assert resultado['file_data']['file_uri'] == url
    
    def test_construir_parte_archivo_gcs_gs(self):
        """Test construir parte de archivo con URI de GCS gs://"""
        servicio = ServicioVertexAI()
        url = 'gs://bucket/file.jpg'
        resultado = servicio._construir_parte_archivo(url, 'image/jpeg')
        
        assert resultado is not None
        assert resultado['file_data']['mime_type'] == 'image/jpeg'
        assert resultado['file_data']['file_uri'] == url
    
    def test_construir_parte_archivo_url_invalida(self):
        """Test construir parte de archivo con URL no válida"""
        servicio = ServicioVertexAI()
        url = 'https://example.com/file.jpg'  # No es GCS
        resultado = servicio._construir_parte_archivo(url, 'image/jpeg')
        
        assert resultado is None
    
    @patch('requests.post')
    def test_generar_sugerencias_exitoso(self, mock_post):
        """Test generar sugerencias exitosamente"""
        servicio = ServicioVertexAI()
        
        # Mock de respuesta de Vertex AI
        mock_response = Mock()
        mock_response.ok = True
        mock_response.json.return_value = {
            'candidates': [{
                'content': {
                    'parts': [{
                        'text': 'Sugerencia de prueba: Paracetamol, Ibuprofeno, Aspirina'
                    }]
                }
            }]
        }
        mock_post.return_value = mock_response
        
        datos_cliente = {
            'nombre': 'Cliente Test',
            'direccion': 'Calle Test 123',
            'telefono': '3001234567'
        }
        historial_pedidos = {
            'total_pedidos': 5,
            'frecuencia_compra': '3 pedidos por mes',
            'ultimos_pedidos': [],
            'productos_mas_comprados': []
        }
        
        resultado = servicio.generar_sugerencias(
            datos_cliente=datos_cliente,
            historial_pedidos=historial_pedidos
        )
        
        assert 'Paracetamol' in resultado
        mock_post.assert_called_once()
    
    @patch('requests.post')
    def test_generar_sugerencias_con_archivo(self, mock_post):
        """Test generar sugerencias con archivo"""
        servicio = ServicioVertexAI()
        
        mock_response = Mock()
        mock_response.ok = True
        mock_response.json.return_value = {
            'candidates': [{
                'content': {
                    'parts': [{
                        'text': 'Sugerencia con imagen'
                    }]
                }
            }]
        }
        mock_post.return_value = mock_response
        
        datos_cliente = {'nombre': 'Cliente Test'}
        historial_pedidos = {'total_pedidos': 0}
        
        resultado = servicio.generar_sugerencias(
            datos_cliente=datos_cliente,
            historial_pedidos=historial_pedidos,
            archivo_url='https://storage.googleapis.com/bucket/image.jpg',
            mime_type='image/jpeg'
        )
        
        assert resultado is not None
        # Verificar que se incluyó el archivo en el payload
        call_args = mock_post.call_args
        payload = call_args[1]['json']
        assert 'contents' in payload
        assert len(payload['contents'][0]['parts']) == 2  # texto + archivo
    
    @patch('requests.post')
    def test_generar_sugerencias_con_comentarios(self, mock_post):
        """Test generar sugerencias con comentarios de evidencia"""
        servicio = ServicioVertexAI()
        
        mock_response = Mock()
        mock_response.ok = True
        mock_response.json.return_value = {
            'candidates': [{
                'content': {
                    'parts': [{
                        'text': 'Sugerencia con comentarios'
                    }]
                }
            }]
        }
        mock_post.return_value = mock_response
        
        datos_cliente = {'nombre': 'Cliente Test'}
        historial_pedidos = {'total_pedidos': 0}
        
        resultado = servicio.generar_sugerencias(
            datos_cliente=datos_cliente,
            historial_pedidos=historial_pedidos,
            comentarios_evidencia='Comentario de prueba'
        )
        
        assert resultado is not None
    
    @patch('requests.post')
    def test_generar_sugerencias_con_historial_completo(self, mock_post):
        """Test generar sugerencias con historial completo"""
        servicio = ServicioVertexAI()
        
        mock_response = Mock()
        mock_response.ok = True
        mock_response.json.return_value = {
            'candidates': [{
                'content': {
                    'parts': [{
                        'text': 'Sugerencia con historial'
                    }]
                }
            }]
        }
        mock_post.return_value = mock_response
        
        datos_cliente = {
            'nombre': 'Cliente Test',
            'email': 'test@example.com'
        }
        historial_pedidos = {
            'total_pedidos': 3,
            'frecuencia_compra': '2 pedidos por mes',
            'ultimos_pedidos': [
                {
                    'fecha': '2025-01-01',
                    'total': 100.0,
                    'estado': 'confirmado',
                    'items': [
                        {'nombre': 'Producto 1', 'cantidad': 2}
                    ]
                }
            ],
            'productos_mas_comprados': [
                {
                    'nombre': 'Producto 1',
                    'cantidad_total': 10,
                    'veces_comprado': 3
                }
            ]
        }
        
        resultado = servicio.generar_sugerencias(
            datos_cliente=datos_cliente,
            historial_pedidos=historial_pedidos
        )
        
        assert resultado is not None
    
    @patch('requests.post')
    def test_generar_sugerencias_error_respuesta(self, mock_post):
        """Test generar sugerencias con error en respuesta"""
        servicio = ServicioVertexAI()
        
        mock_response = Mock()
        mock_response.ok = False
        mock_response.text = 'Error 400'
        mock_response.raise_for_status.side_effect = requests.HTTPError('Error 400')
        mock_post.return_value = mock_response
        
        datos_cliente = {'nombre': 'Cliente Test'}
        historial_pedidos = {'total_pedidos': 0}
        
        with pytest.raises(requests.HTTPError):
            servicio.generar_sugerencias(
                datos_cliente=datos_cliente,
                historial_pedidos=historial_pedidos
            )
    
    @patch('requests.post')
    def test_generar_sugerencias_respuesta_vacia(self, mock_post):
        """Test generar sugerencias con respuesta vacía"""
        servicio = ServicioVertexAI()
        
        mock_response = Mock()
        mock_response.ok = True
        mock_response.json.return_value = {
            'candidates': []
        }
        mock_post.return_value = mock_response
        
        datos_cliente = {'nombre': 'Cliente Test'}
        historial_pedidos = {'total_pedidos': 0}
        
        resultado = servicio.generar_sugerencias(
            datos_cliente=datos_cliente,
            historial_pedidos=historial_pedidos
        )
        
        assert resultado == 'No se recibieron sugerencias del modelo.'
    
    @patch('requests.post')
    def test_generar_sugerencias_sin_texto(self, mock_post):
        """Test generar sugerencias sin texto en respuesta"""
        servicio = ServicioVertexAI()
        
        mock_response = Mock()
        mock_response.ok = True
        mock_response.json.return_value = {
            'candidates': [{
                'content': {
                    'parts': [{
                        'other_field': 'value'  # No tiene 'text'
                    }]
                }
            }]
        }
        mock_post.return_value = mock_response
        
        datos_cliente = {'nombre': 'Cliente Test'}
        historial_pedidos = {'total_pedidos': 0}
        
        resultado = servicio.generar_sugerencias(
            datos_cliente=datos_cliente,
            historial_pedidos=historial_pedidos
        )
        
        assert resultado == 'No se recibieron sugerencias del modelo.'

