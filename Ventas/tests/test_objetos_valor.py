import pytest
import sys
import os
from datetime import datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from dominio.objetos_valor import EstadoVisita, FechaProgramada, Direccion, Telefono, Descripcion, EstadoPedido


class TestObjetosValor:
    
    def test_estado_visita_valido(self):
        estado = EstadoVisita("pendiente")
        assert estado.estado == "pendiente"
        
        estado = EstadoVisita("completada")
        assert estado.estado == "completada"
    
    def test_estado_visita_invalido(self):
        with pytest.raises(ValueError, match="Estado debe ser 'pendiente' o 'completada'"):
            EstadoVisita("invalido")
    
    def test_fecha_programada_futura(self):
        fecha_futura = datetime.now() + timedelta(days=1)
        fecha = FechaProgramada(fecha_futura)
        assert fecha.fecha == fecha_futura
    
    def test_fecha_programada_pasada(self):
        fecha_pasada = datetime.now() - timedelta(days=1)
        with pytest.raises(ValueError, match="La fecha programada no puede ser en el pasado"):
            FechaProgramada(fecha_pasada)
    
    def test_fecha_programada_hoy_valida(self):
        # Las fechas de hoy deben ser válidas
        fecha_hoy = datetime.now()
        fecha = FechaProgramada(fecha_hoy)
        assert fecha.fecha == fecha_hoy
    
    def test_direccion(self):
        direccion = Direccion("Calle 123 #45-67")
        assert direccion.direccion == "Calle 123 #45-67"
    
    def test_telefono(self):
        telefono = Telefono("3001234567")
        assert telefono.telefono == "3001234567"
    
    def test_descripcion(self):
        descripcion = Descripcion("Visita programada")
        assert descripcion.descripcion == "Visita programada"
    
    def test_estado_pedido_validos(self):
        """Test para estados válidos de pedido"""
        # Estados originales
        estado_borrador = EstadoPedido("borrador")
        assert estado_borrador.estado == "borrador"
        
        estado_confirmado = EstadoPedido("confirmado")
        assert estado_confirmado.estado == "confirmado"
        
        estado_cancelado = EstadoPedido("cancelado")
        assert estado_cancelado.estado == "cancelado"
        
        # Nuevos estados
        estado_en_transito = EstadoPedido("en_transito")
        assert estado_en_transito.estado == "en_transito"
        
        estado_entregado = EstadoPedido("entregado")
        assert estado_entregado.estado == "entregado"
    
    def test_estado_pedido_invalido(self):
        """Test para estado inválido de pedido"""
        with pytest.raises(ValueError, match="Estado debe ser 'borrador', 'confirmado', 'en_transito', 'entregado' o 'cancelado'"):
            EstadoPedido("estado_invalido")
        
        with pytest.raises(ValueError, match="Estado debe ser 'borrador', 'confirmado', 'en_transito', 'entregado' o 'cancelado'"):
            EstadoPedido("")
        
        with pytest.raises(ValueError, match="Estado debe ser 'borrador', 'confirmado', 'en_transito', 'entregado' o 'cancelado'"):
            EstadoPedido(None)
    
    def test_estado_pedido_case_sensitive(self):
        """Test para verificar que los estados son case sensitive"""
        with pytest.raises(ValueError, match="Estado debe ser 'borrador', 'confirmado', 'en_transito', 'entregado' o 'cancelado'"):
            EstadoPedido("BORRADOR")
        
        with pytest.raises(ValueError, match="Estado debe ser 'borrador', 'confirmado', 'en_transito', 'entregado' o 'cancelado'"):
            EstadoPedido("En_Transito")
        
        with pytest.raises(ValueError, match="Estado debe ser 'borrador', 'confirmado', 'en_transito', 'entregado' o 'cancelado'"):
            EstadoPedido("ENTREGADO")
