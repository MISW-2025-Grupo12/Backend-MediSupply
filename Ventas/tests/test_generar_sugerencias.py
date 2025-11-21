"""Tests para el comando de generar sugerencias"""
import pytest
import uuid
import sys
import os
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from aplicacion.comandos.generar_sugerencias import GenerarSugerencias, GenerarSugerenciasHandler
from aplicacion.dto import VisitaDTO, EvidenciaVisitaDTO, SugerenciaClienteDTO


class TestGenerarSugerencias:
    """Tests para el comando GenerarSugerencias"""
    
    def test_crear_comando(self):
        """Test crear comando de generar sugerencias"""
        visita_id = str(uuid.uuid4())
        comando = GenerarSugerencias(visita_id=visita_id)
        
        assert comando.visita_id == visita_id


class TestGenerarSugerenciasHandler:
    """Tests para el handler de generar sugerencias"""
    
    def setup_method(self):
        """Configuración antes de cada test"""
        self.visita_id = str(uuid.uuid4())
        self.cliente_id = str(uuid.uuid4())
        self.vendedor_id = str(uuid.uuid4())
        
        # Mocks de repositorios
        self.mock_repositorio_sugerencia = Mock()
        self.mock_repositorio_evidencia = Mock()
        self.mock_repositorio_visita = Mock()
        self.mock_servicio_ia = Mock()
        self.mock_servicio_usuarios = Mock()
        self.mock_servicio_historial = Mock()
        
        # Configurar propiedades del mock de servicio IA
        self.mock_servicio_ia.nombre_proveedor = 'vertex-ai'
        self.mock_servicio_ia.modelo_actual = 'gemini-2.5-flash-lite'
        # Compatibilidad hacia atrás
        self.mock_servicio_ia.base_model = 'gemini-2.5-flash-lite'
        
        # Crear handler con mocks
        self.handler = GenerarSugerenciasHandler(
            repositorio_sugerencia=self.mock_repositorio_sugerencia,
            repositorio_evidencia=self.mock_repositorio_evidencia,
            repositorio_visita=self.mock_repositorio_visita,
            servicio_ia=self.mock_servicio_ia,
            servicio_usuarios=self.mock_servicio_usuarios,
            servicio_historial=self.mock_servicio_historial
        )
    
    def test_visita_no_encontrada(self):
        """Test cuando la visita no existe"""
        comando = GenerarSugerencias(visita_id=self.visita_id)
        self.mock_repositorio_visita.obtener_por_id.return_value = None
        
        with pytest.raises(ValueError, match="Visita.*no encontrada"):
            self.handler.handle(comando)
    
    def test_cliente_no_encontrado(self):
        """Test cuando el cliente no existe"""
        comando = GenerarSugerencias(visita_id=self.visita_id)
        
        # Mock de visita
        visita = VisitaDTO(
            id=uuid.UUID(self.visita_id),
            vendedor_id=self.vendedor_id,
            cliente_id=self.cliente_id,
            fecha_programada=datetime.now(),
            direccion="Calle Test",
            telefono="3001234567",
            estado="pendiente",
            descripcion="Visita de prueba"
        )
        self.mock_repositorio_visita.obtener_por_id.return_value = visita
        self.mock_servicio_usuarios.obtener_cliente_por_id.return_value = None
        
        with pytest.raises(ValueError, match="Cliente.*no encontrado"):
            self.handler.handle(comando)
    
    def test_generar_sugerencias_sin_evidencias(self):
        """Test generar sugerencias sin evidencias"""
        comando = GenerarSugerencias(visita_id=self.visita_id)
        
        # Mock de visita
        visita = VisitaDTO(
            id=uuid.UUID(self.visita_id),
            vendedor_id=self.vendedor_id,
            cliente_id=self.cliente_id,
            fecha_programada=datetime.now(),
            direccion="Calle Test",
            telefono="3001234567",
            estado="pendiente",
            descripcion="Visita de prueba"
        )
        
        # Mock de datos del cliente
        datos_cliente = {
            'nombre': 'Cliente Test',
            'direccion': 'Calle Test 123',
            'telefono': '3001234567'
        }
        
        # Mock de historial
        historial_pedidos = {
            'total_pedidos': 5,
            'frecuencia_compra': '3 pedidos por mes',
            'ultimos_pedidos': [],
            'productos_mas_comprados': []
        }
        
        # Mock de sugerencia generada
        sugerencia_texto = "Sugerencias de prueba"
        self.mock_servicio_ia.modelo_actual = 'gemini-2.5-flash-lite'
        self.mock_servicio_ia.generar_sugerencias.return_value = sugerencia_texto
        
        # Mock de sugerencia guardada
        sugerencia_guardada = SugerenciaClienteDTO(
            cliente_id=self.cliente_id,
            evidencia_id=None,
            sugerencias_texto=sugerencia_texto,
            modelo_usado='gemini-2.5-flash-lite'
        )
        self.mock_repositorio_sugerencia.crear.return_value = sugerencia_guardada
        
        # Configurar mocks
        self.mock_repositorio_visita.obtener_por_id.return_value = visita
        self.mock_servicio_usuarios.obtener_cliente_por_id.return_value = datos_cliente
        self.mock_servicio_historial.obtener_historial_cliente.return_value = historial_pedidos
        self.mock_repositorio_evidencia.obtener_por_visita.return_value = []
        
        # Ejecutar
        resultado = self.handler.handle(comando)
        
        # Verificar
        assert resultado.cliente_id == self.cliente_id
        assert resultado.evidencia_id is None
        assert resultado.sugerencias_texto == sugerencia_texto
        self.mock_servicio_ia.generar_sugerencias.assert_called_once()
        self.mock_repositorio_sugerencia.crear.assert_called_once()
    
    def test_generar_sugerencias_con_evidencias(self):
        """Test generar sugerencias con evidencias"""
        comando = GenerarSugerencias(visita_id=self.visita_id)
        
        # Mock de visita
        visita = VisitaDTO(
            id=uuid.UUID(self.visita_id),
            vendedor_id=self.vendedor_id,
            cliente_id=self.cliente_id,
            fecha_programada=datetime.now(),
            direccion="Calle Test",
            telefono="3001234567",
            estado="pendiente",
            descripcion="Visita de prueba"
        )
        
        # Mock de evidencia
        evidencia_id = str(uuid.uuid4())
        evidencia = EvidenciaVisitaDTO(
            id=uuid.UUID(evidencia_id),
            visita_id=self.visita_id,
            archivo_url='https://storage.googleapis.com/bucket/image.jpg',
            nombre_archivo='image.jpg',
            formato='jpg',
            tamaño_bytes=1024,
            comentarios='Comentario de prueba',
            vendedor_id=self.vendedor_id,
            created_at=datetime.now()
        )
        
        # Mock de datos del cliente
        datos_cliente = {
            'nombre': 'Cliente Test',
            'direccion': 'Calle Test 123',
            'telefono': '3001234567'
        }
        
        # Mock de historial
        historial_pedidos = {
            'total_pedidos': 5,
            'frecuencia_compra': '3 pedidos por mes',
            'ultimos_pedidos': [],
            'productos_mas_comprados': []
        }
        
        # Mock de sugerencia generada
        sugerencia_texto = "Sugerencias con evidencia"
        self.mock_servicio_ia.modelo_actual = 'gemini-2.5-flash-lite'
        self.mock_servicio_ia.obtener_mime_type.return_value = 'image/jpeg'
        self.mock_servicio_ia.generar_sugerencias.return_value = sugerencia_texto
        
        # Mock de sugerencia guardada
        sugerencia_guardada = SugerenciaClienteDTO(
            cliente_id=self.cliente_id,
            evidencia_id=evidencia_id,
            sugerencias_texto=sugerencia_texto,
            modelo_usado='gemini-2.5-flash-lite'
        )
        self.mock_repositorio_sugerencia.crear.return_value = sugerencia_guardada
        
        # Configurar mocks
        self.mock_repositorio_visita.obtener_por_id.return_value = visita
        self.mock_servicio_usuarios.obtener_cliente_por_id.return_value = datos_cliente
        self.mock_servicio_historial.obtener_historial_cliente.return_value = historial_pedidos
        self.mock_repositorio_evidencia.obtener_por_visita.return_value = [evidencia]
        
        # Ejecutar
        resultado = self.handler.handle(comando)
        
        # Verificar
        assert resultado.cliente_id == self.cliente_id
        assert resultado.evidencia_id == evidencia_id
        assert resultado.sugerencias_texto == sugerencia_texto
        
        # Verificar que se llamó con la URL y mime type correctos
        call_args = self.mock_servicio_ia.generar_sugerencias.call_args
        assert call_args[1]['archivo_url'] == evidencia.archivo_url
        assert call_args[1]['mime_type'] == 'image/jpeg'
        assert call_args[1]['comentarios_evidencia'] == 'Comentario de prueba'
        
        self.mock_servicio_ia.obtener_mime_type.assert_called_once_with('jpg')
    
    def test_generar_sugerencias_con_multiples_evidencias(self):
        """Test generar sugerencias con múltiples evidencias"""
        comando = GenerarSugerencias(visita_id=self.visita_id)
        
        # Mock de visita
        visita = VisitaDTO(
            id=uuid.UUID(self.visita_id),
            vendedor_id=self.vendedor_id,
            cliente_id=self.cliente_id,
            fecha_programada=datetime.now(),
            direccion="Calle Test",
            telefono="3001234567",
            estado="pendiente",
            descripcion="Visita de prueba"
        )
        
        # Mock de múltiples evidencias
        evidencia1 = EvidenciaVisitaDTO(
            id=uuid.uuid4(),
            visita_id=self.visita_id,
            archivo_url='https://storage.googleapis.com/bucket/image1.jpg',
            nombre_archivo='image1.jpg',
            formato='jpg',
            tamaño_bytes=1024,
            comentarios='Comentario 1',
            vendedor_id=self.vendedor_id,
            created_at=datetime.now() - timedelta(days=1)
        )
        
        evidencia2 = EvidenciaVisitaDTO(
            id=uuid.uuid4(),
            visita_id=self.visita_id,
            archivo_url='https://storage.googleapis.com/bucket/image2.jpg',
            nombre_archivo='image2.jpg',
            formato='jpg',
            tamaño_bytes=2048,
            comentarios='Comentario 2',
            vendedor_id=self.vendedor_id,
            created_at=datetime.now()  # Más reciente
        )
        
        # Mock de datos del cliente
        datos_cliente = {'nombre': 'Cliente Test'}
        historial_pedidos = {'total_pedidos': 0}
        
        # Mock de sugerencia generada
        sugerencia_texto = "Sugerencias con múltiples evidencias"
        self.mock_servicio_ia.modelo_actual = 'gemini-2.5-flash-lite'
        self.mock_servicio_ia.obtener_mime_type.return_value = 'image/jpeg'
        self.mock_servicio_ia.generar_sugerencias.return_value = sugerencia_texto
        
        sugerencia_guardada = SugerenciaClienteDTO(
            cliente_id=self.cliente_id,
            evidencia_id=str(evidencia2.id),  # La más reciente
            sugerencias_texto=sugerencia_texto,
            modelo_usado='gemini-2.5-flash-lite'
        )
        self.mock_repositorio_sugerencia.crear.return_value = sugerencia_guardada
        
        # Configurar mocks
        self.mock_repositorio_visita.obtener_por_id.return_value = visita
        self.mock_servicio_usuarios.obtener_cliente_por_id.return_value = datos_cliente
        self.mock_servicio_historial.obtener_historial_cliente.return_value = historial_pedidos
        self.mock_repositorio_evidencia.obtener_por_visita.return_value = [evidencia1, evidencia2]
        
        # Ejecutar
        resultado = self.handler.handle(comando)
        
        # Verificar que se usó la evidencia más reciente
        call_args = self.mock_servicio_ia.generar_sugerencias.call_args
        assert call_args[1]['archivo_url'] == evidencia2.archivo_url
        # Verificar que se combinaron los comentarios
        assert 'Comentario 1' in call_args[1]['comentarios_evidencia']
        assert 'Comentario 2' in call_args[1]['comentarios_evidencia']
    
    def test_generar_sugerencias_evidencia_sin_comentarios(self):
        """Test generar sugerencias con evidencia sin comentarios"""
        comando = GenerarSugerencias(visita_id=self.visita_id)
        
        # Mock de visita
        visita = VisitaDTO(
            id=uuid.UUID(self.visita_id),
            vendedor_id=self.vendedor_id,
            cliente_id=self.cliente_id,
            fecha_programada=datetime.now(),
            direccion="Calle Test",
            telefono="3001234567",
            estado="pendiente",
            descripcion="Visita de prueba"
        )
        
        # Mock de evidencia sin comentarios
        evidencia = EvidenciaVisitaDTO(
            id=uuid.uuid4(),
            visita_id=self.visita_id,
            archivo_url='https://storage.googleapis.com/bucket/image.jpg',
            nombre_archivo='image.jpg',
            formato='jpg',
            tamaño_bytes=1024,
            comentarios=None,  # Sin comentarios
            vendedor_id=self.vendedor_id,
            created_at=datetime.now()
        )
        
        datos_cliente = {'nombre': 'Cliente Test'}
        historial_pedidos = {'total_pedidos': 0}
        
        sugerencia_texto = "Sugerencias"
        self.mock_servicio_ia.modelo_actual = 'gemini-2.5-flash-lite'
        self.mock_servicio_ia.obtener_mime_type.return_value = 'image/jpeg'
        self.mock_servicio_ia.generar_sugerencias.return_value = sugerencia_texto
        
        sugerencia_guardada = SugerenciaClienteDTO(
            cliente_id=self.cliente_id,
            evidencia_id=str(evidencia.id),
            sugerencias_texto=sugerencia_texto,
            modelo_usado='gemini-2.5-flash-lite'
        )
        self.mock_repositorio_sugerencia.crear.return_value = sugerencia_guardada
        
        self.mock_repositorio_visita.obtener_por_id.return_value = visita
        self.mock_servicio_usuarios.obtener_cliente_por_id.return_value = datos_cliente
        self.mock_servicio_historial.obtener_historial_cliente.return_value = historial_pedidos
        self.mock_repositorio_evidencia.obtener_por_visita.return_value = [evidencia]
        
        resultado = self.handler.handle(comando)
        
        # Verificar que no se pasaron comentarios
        call_args = self.mock_servicio_ia.generar_sugerencias.call_args
        assert call_args[1]['comentarios_evidencia'] is None or call_args[1]['comentarios_evidencia'] == ''
    
    def test_generar_sugerencias_error_exception(self):
        """Test que maneja errores correctamente"""
        comando = GenerarSugerencias(visita_id=self.visita_id)
        
        # Mock que lanza excepción
        self.mock_repositorio_visita.obtener_por_id.side_effect = Exception("Error de BD")
        
        with pytest.raises(Exception):
            self.handler.handle(comando)

