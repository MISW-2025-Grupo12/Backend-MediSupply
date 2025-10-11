import pytest
import sys
import os
from datetime import date, time
from unittest.mock import Mock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from aplicacion.comandos.registrar_visita import RegistrarVisita, RegistrarVisitaHandler
from aplicacion.dto import VisitaDTO

class TestRegistrarVisita:
    def test_crear_comando(self):
        comando = RegistrarVisita(
            visita_id="123e4567-e89b-12d3-a456-426614174000",
            fecha_realizada="2025-10-15",
            hora_realizada="14:30:00",
            cliente_id="cliente-123",
            novedades="Cliente solicita más información",
            pedido_generado=True
        )
        
        assert comando.visita_id == "123e4567-e89b-12d3-a456-426614174000"
        assert comando.fecha_realizada == "2025-10-15"
        assert comando.hora_realizada == "14:30:00"
        assert comando.cliente_id == "cliente-123"
        assert comando.novedades == "Cliente solicita más información"
        assert comando.pedido_generado == True

class TestRegistrarVisitaHandler:
    def setup_method(self):
        self.mock_repositorio = Mock()
        self.handler = RegistrarVisitaHandler(repositorio=self.mock_repositorio)

    def test_handle_exitoso(self):
        from datetime import date, timedelta
        fecha_pasada = (date.today() - timedelta(days=1)).isoformat()
        
        comando = RegistrarVisita(
            visita_id="123e4567-e89b-12d3-a456-426614174000",
            fecha_realizada=fecha_pasada,
            hora_realizada="14:30:00",
            cliente_id="cliente-123",
            novedades="Cliente solicita más información",
            pedido_generado=True
        )
        
        visita_existente = VisitaDTO(
            vendedor_id="vendedor-123",
            cliente_id="cliente-456",
            fecha_programada=date.today(),
            direccion="Calle 123",
            telefono="3001234567",
            estado="pendiente",
            descripcion="Visita programada"
        )
        
        visita_actualizada = VisitaDTO(
            vendedor_id="vendedor-123",
            cliente_id="cliente-123",
            fecha_programada=date.today(),
            direccion="Calle 123",
            telefono="3001234567",
            estado="completada",
            descripcion="Visita programada",
            fecha_realizada=date.today() - timedelta(days=1),
            hora_realizada=time(14, 30, 0),
            novedades="Cliente solicita más información",
            pedido_generado=True
        )
        
        self.mock_repositorio.obtener_por_id.return_value = visita_existente
        self.mock_repositorio.actualizar.return_value = visita_actualizada
        
        resultado = self.handler.handle(comando)
        
        assert resultado.estado == "completada"
        assert resultado.fecha_realizada == date.today() - timedelta(days=1)
        assert resultado.hora_realizada == time(14, 30, 0)
        assert resultado.novedades == "Cliente solicita más información"
        assert resultado.pedido_generado == True
        self.mock_repositorio.obtener_por_id.assert_called_once_with(comando.visita_id)
        self.mock_repositorio.actualizar.assert_called_once()

    def test_handle_formato_fecha_invalido(self):
        comando = RegistrarVisita(
            visita_id="123e4567-e89b-12d3-a456-426614174000",
            fecha_realizada="15/10/2025",
            hora_realizada="14:30:00",
            cliente_id="cliente-123"
        )
        
        with pytest.raises(ValueError, match="Formato de fecha inválido"):
            self.handler.handle(comando)

    def test_handle_formato_hora_invalido(self):
        comando = RegistrarVisita(
            visita_id="123e4567-e89b-12d3-a456-426614174000",
            fecha_realizada="2025-10-15",
            hora_realizada="2:30 PM",
            cliente_id="cliente-123"
        )
        
        with pytest.raises(ValueError, match="Formato de hora inválido"):
            self.handler.handle(comando)

    def test_handle_fecha_futura(self):
        from datetime import date, timedelta
        fecha_futura = (date.today() + timedelta(days=1)).isoformat()
        
        comando = RegistrarVisita(
            visita_id="123e4567-e89b-12d3-a456-426614174000",
            fecha_realizada=fecha_futura,
            hora_realizada="14:30:00",
            cliente_id="cliente-123"
        )
        
        with pytest.raises(ValueError, match="La fecha realizada no puede ser futura"):
            self.handler.handle(comando)

    def test_handle_cliente_vacio(self):
        from datetime import date, timedelta
        fecha_pasada = (date.today() - timedelta(days=1)).isoformat()
        
        comando = RegistrarVisita(
            visita_id="123e4567-e89b-12d3-a456-426614174000",
            fecha_realizada=fecha_pasada,
            hora_realizada="14:30:00",
            cliente_id=""
        )
        
        with pytest.raises(ValueError, match="Debe seleccionar un cliente"):
            self.handler.handle(comando)

    def test_handle_novedades_muy_largas(self):
        from datetime import date, timedelta
        fecha_pasada = (date.today() - timedelta(days=1)).isoformat()
        
        comando = RegistrarVisita(
            visita_id="123e4567-e89b-12d3-a456-426614174000",
            fecha_realizada=fecha_pasada,
            hora_realizada="14:30:00",
            cliente_id="cliente-123",
            novedades="x" * 501
        )
        
        with pytest.raises(ValueError, match="Las novedades no pueden exceder 500 caracteres"):
            self.handler.handle(comando)

    def test_handle_visita_no_encontrada(self):
        from datetime import date, timedelta
        fecha_pasada = (date.today() - timedelta(days=1)).isoformat()
        
        comando = RegistrarVisita(
            visita_id="123e4567-e89b-12d3-a456-426614174000",
            fecha_realizada=fecha_pasada,
            hora_realizada="14:30:00",
            cliente_id="cliente-123"
        )
        
        self.mock_repositorio.obtener_por_id.return_value = None
        
        with pytest.raises(ValueError, match="Visita .* no encontrada"):
            self.handler.handle(comando)
