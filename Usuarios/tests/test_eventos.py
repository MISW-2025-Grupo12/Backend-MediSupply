import pytest
import sys
import os
import uuid
from datetime import datetime
from unittest.mock import Mock, patch

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from dominio.eventos import ClienteCreado, VendedorCreado, ProveedorCreado
from seedwork.dominio.eventos import (
    EventoDominio, 
    ManejadorEvento, 
    PublicadorEventos, 
    DespachadorEventos
)


class TestEventos:
    """Test para los eventos de dominio"""
    
    def test_cliente_creado_creacion(self):
        """Test creación de evento ClienteCreado"""
        # Arrange
        cliente_id = uuid.uuid4()
        nombre = "Juan Pérez"
        email = "juan@email.com"
        telefono = "1234567890"
        direccion = "Calle 123 #45-67"
        
        # Act
        evento = ClienteCreado(
            cliente_id=cliente_id,
            nombre=nombre,
            email=email,
            telefono=telefono,
            direccion=direccion
        )
        
        # Assert
        assert evento.cliente_id == cliente_id
        assert evento.nombre == nombre
        assert evento.email == email
        assert evento.telefono == telefono
        assert evento.direccion == direccion
    
    def test_cliente_creado_get_datos_evento(self):
        """Test conversión de ClienteCreado a diccionario"""
        # Arrange
        cliente_id = uuid.uuid4()
        evento = ClienteCreado(
            cliente_id=cliente_id,
            nombre="Juan Pérez",
            email="juan@email.com",
            telefono="1234567890",
            direccion="Calle 123 #45-67"
        )
        
        # Act
        dict_result = evento._get_datos_evento()
        
        # Assert
        assert isinstance(dict_result, dict)
        assert dict_result['cliente_id'] == str(cliente_id)
        assert dict_result['nombre'] == "Juan Pérez"
        assert dict_result['email'] == "juan@email.com"
        assert dict_result['telefono'] == "1234567890"
        assert dict_result['direccion'] == "Calle 123 #45-67"
    
    def test_vendedor_creado_creacion(self):
        """Test creación de evento VendedorCreado"""
        # Arrange
        vendedor_id = uuid.uuid4()
        nombre = "María García"
        email = "maria@email.com"
        telefono = "0987654321"
        direccion = "Avenida 456 #78-90"
        
        # Act
        evento = VendedorCreado(
            vendedor_id=vendedor_id,
            nombre=nombre,
            email=email,
            telefono=telefono,
            direccion=direccion
        )
        
        # Assert
        assert evento.vendedor_id == vendedor_id
        assert evento.nombre == nombre
        assert evento.email == email
        assert evento.telefono == telefono
        assert evento.direccion == direccion
    
    def test_vendedor_creado_get_datos_evento(self):
        """Test conversión de VendedorCreado a diccionario"""
        # Arrange
        vendedor_id = uuid.uuid4()
        evento = VendedorCreado(
            vendedor_id=vendedor_id,
            nombre="María García",
            email="maria@email.com",
            telefono="0987654321",
            direccion="Avenida 456 #78-90"
        )
        
        # Act
        dict_result = evento._get_datos_evento()
        
        # Assert
        assert isinstance(dict_result, dict)
        assert dict_result['vendedor_id'] == str(vendedor_id)
        assert dict_result['nombre'] == "María García"
        assert dict_result['email'] == "maria@email.com"
        assert dict_result['telefono'] == "0987654321"
        assert dict_result['direccion'] == "Avenida 456 #78-90"
    
    def test_proveedor_creado_creacion(self):
        """Test creación de evento ProveedorCreado"""
        # Arrange
        proveedor_id = uuid.uuid4()
        nombre = "Farmacia Central"
        email = "contacto@farmacia.com"
        direccion = "Calle Principal #100"
        
        # Act
        evento = ProveedorCreado(
            proveedor_id=proveedor_id,
            nombre=nombre,
            email=email,
            direccion=direccion
        )
        
        # Assert
        assert evento.proveedor_id == proveedor_id
        assert evento.nombre == nombre
        assert evento.email == email
        assert evento.direccion == direccion
    
    def test_proveedor_creado_get_datos_evento(self):
        """Test conversión de ProveedorCreado a diccionario"""
        # Arrange
        proveedor_id = uuid.uuid4()
        evento = ProveedorCreado(
            proveedor_id=proveedor_id,
            nombre="Farmacia Central",
            email="contacto@farmacia.com",
            direccion="Calle Principal #100"
        )
        
        # Act
        dict_result = evento._get_datos_evento()
        
        # Assert
        assert isinstance(dict_result, dict)
        assert dict_result['proveedor_id'] == str(proveedor_id)
        assert dict_result['nombre'] == "Farmacia Central"
        assert dict_result['email'] == "contacto@farmacia.com"
        assert dict_result['direccion'] == "Calle Principal #100"
    
    def test_eventos_valores_por_defecto(self):
        """Test eventos con valores por defecto"""
        # Arrange & Act
        cliente_evento = ClienteCreado(
            cliente_id=uuid.uuid4(),
            nombre="Test",
            email="test@test.com",
            telefono="0000000000",
            direccion="Test"
        )
        
        vendedor_evento = VendedorCreado(
            vendedor_id=uuid.uuid4(),
            nombre="Test",
            email="test@test.com",
            telefono="0000000000",
            direccion="Test"
        )
        
        proveedor_evento = ProveedorCreado(
            proveedor_id=uuid.uuid4(),
            nombre="Test",
            email="test@test.com",
            direccion="Test"
        )
        
        # Assert
        assert cliente_evento.nombre == "Test"
        assert vendedor_evento.nombre == "Test"
        assert proveedor_evento.nombre == "Test"


class EventoTest(EventoDominio):
    """Evento de prueba para testing"""
    
    def __init__(self, datos_test="test"):
        super().__init__()
        self.datos_test = datos_test
    
    def _get_datos_evento(self) -> dict:
        return {
            'datos_test': self.datos_test,
            'timestamp': datetime.now().isoformat()
        }


class ManejadorTest(ManejadorEvento):
    """Manejador de prueba para testing"""
    
    def __init__(self):
        self.eventos_manejados = []
    
    def manejar(self, evento: EventoDominio):
        self.eventos_manejados.append(evento)


class PublicadorTest(PublicadorEventos):
    """Publicador de prueba para testing"""
    
    def __init__(self):
        self.eventos_publicados = []
    
    def publicar(self, evento: EventoDominio):
        self.eventos_publicados.append(evento)


class TestEventoDominio:
    """Test para EventoDominio"""
    
    def test_evento_dominio_creacion(self):
        """Test creación de evento de dominio"""
        # Arrange & Act
        evento = EventoTest("datos de prueba")
        
        # Assert
        assert isinstance(evento.id, uuid.UUID)
        assert isinstance(evento.fecha_evento, datetime)
        assert evento.version == 1
        assert evento.datos_test == "datos de prueba"
    
    def test_evento_dominio_to_dict(self):
        """Test conversión a diccionario"""
        # Arrange
        evento = EventoTest("datos de prueba")
        
        # Act
        resultado = evento.to_dict()
        
        # Assert
        assert isinstance(resultado, dict)
        assert 'id' in resultado
        assert 'fecha_evento' in resultado
        assert 'version' in resultado
        assert 'tipo_evento' in resultado
        assert 'datos' in resultado
        assert resultado['tipo_evento'] == 'EventoTest'
        assert resultado['version'] == 1
        assert resultado['datos']['datos_test'] == "datos de prueba"
    
    def test_evento_dominio_abstracto(self):
        """Test que EventoDominio es abstracto"""
        # Arrange & Act & Assert
        with pytest.raises(TypeError):
            EventoDominio()


class TestManejadorEvento:
    """Test para ManejadorEvento"""
    
    def test_manejador_evento_abstracto(self):
        """Test que ManejadorEvento es abstracto"""
        # Arrange & Act & Assert
        with pytest.raises(TypeError):
            ManejadorEvento()
    
    def test_manejador_evento_implementacion(self):
        """Test implementación de ManejadorEvento"""
        # Arrange
        manejador = ManejadorTest()
        evento = EventoTest("test")
        
        # Act
        manejador.manejar(evento)
        
        # Assert
        assert len(manejador.eventos_manejados) == 1
        assert manejador.eventos_manejados[0] == evento


class TestPublicadorEventos:
    """Test para PublicadorEventos"""
    
    def test_publicador_eventos_abstracto(self):
        """Test que PublicadorEventos es abstracto"""
        # Arrange & Act & Assert
        with pytest.raises(TypeError):
            PublicadorEventos()
    
    def test_publicador_eventos_implementacion(self):
        """Test implementación de PublicadorEventos"""
        # Arrange
        publicador = PublicadorTest()
        evento = EventoTest("test")
        
        # Act
        publicador.publicar(evento)
        
        # Assert
        assert len(publicador.eventos_publicados) == 1
        assert publicador.eventos_publicados[0] == evento


class TestDespachadorEventos:
    """Test para DespachadorEventos"""
    
    def test_despachador_eventos_creacion(self):
        """Test creación de despachador de eventos"""
        # Arrange & Act
        despachador = DespachadorEventos()
        
        # Assert
        assert isinstance(despachador._manejadores, dict)
        assert len(despachador._manejadores) == 0
    
    def test_registrar_manejador(self):
        """Test registro de manejador"""
        # Arrange
        despachador = DespachadorEventos()
        manejador = ManejadorTest()
        tipo_evento = "EventoTest"
        
        # Act
        despachador.registrar_manejador(tipo_evento, manejador)
        
        # Assert
        assert tipo_evento in despachador._manejadores
        assert manejador in despachador._manejadores[tipo_evento]
    
    def test_registrar_multiples_manejadores(self):
        """Test registro de múltiples manejadores para el mismo tipo"""
        # Arrange
        despachador = DespachadorEventos()
        manejador1 = ManejadorTest()
        manejador2 = ManejadorTest()
        tipo_evento = "EventoTest"
        
        # Act
        despachador.registrar_manejador(tipo_evento, manejador1)
        despachador.registrar_manejador(tipo_evento, manejador2)
        
        # Assert
        assert len(despachador._manejadores[tipo_evento]) == 2
        assert manejador1 in despachador._manejadores[tipo_evento]
        assert manejador2 in despachador._manejadores[tipo_evento]
    
    def test_publicar_evento_sin_manejadores(self):
        """Test publicación de evento sin manejadores registrados"""
        # Arrange
        despachador = DespachadorEventos()
        evento = EventoTest("test")
        
        # Act & Assert - No debe lanzar excepción
        despachador.publicar_evento(evento)
    
    def test_publicar_evento_con_manejadores(self):
        """Test publicación de evento con manejadores registrados"""
        # Arrange
        despachador = DespachadorEventos()
        manejador1 = ManejadorTest()
        manejador2 = ManejadorTest()
        evento = EventoTest("test")
        
        despachador.registrar_manejador("EventoTest", manejador1)
        despachador.registrar_manejador("EventoTest", manejador2)
        
        # Act
        despachador.publicar_evento(evento)
        
        # Assert
        assert len(manejador1.eventos_manejados) == 1
        assert len(manejador2.eventos_manejados) == 1
        assert manejador1.eventos_manejados[0] == evento
        assert manejador2.eventos_manejados[0] == evento
    
    def test_publicar_evento_con_manejador_que_falla(self):
        """Test publicación de evento cuando un manejador falla"""
        # Arrange
        despachador = DespachadorEventos()
        manejador1 = ManejadorTest()
        manejador2 = Mock()
        manejador2.manejar.side_effect = Exception("Error en manejador")
        evento = EventoTest("test")
        
        despachador.registrar_manejador("EventoTest", manejador1)
        despachador.registrar_manejador("EventoTest", manejador2)
        
        # Act & Assert - Debe lanzar excepción cuando un manejador falla
        with pytest.raises(Exception, match="Error en manejador"):
            despachador.publicar_evento(evento)
        
        # Assert - El primer manejador sí fue ejecutado antes de que fallara el segundo
        assert len(manejador1.eventos_manejados) == 1
        assert manejador1.eventos_manejados[0] == evento