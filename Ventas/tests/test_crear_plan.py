import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
import uuid
from flask import Flask

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from aplicacion.comandos.crear_plan import CrearPlan, ClienteVisita, CrearPlanHandler
from config.db import db
from infraestructura.modelos import PlanVisitaModel, VisitaModel


class TestCrearPlan:
    """Tests unitarios para el comando CrearPlan"""
    
    def setup_method(self):
        self.handler = CrearPlanHandler()
        self.app = Flask(__name__)
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        db.init_app(self.app)
        
        with self.app.app_context():
            db.create_all()
    
    def teardown_method(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
    
    @patch('aplicacion.comandos.crear_plan.ServicioUsuarios')
    def test_crear_plan_exitoso(self, mock_servicio_usuarios_class):
        """Test para crear un plan exitosamente"""
        # Mock del servicio de usuarios
        mock_servicio = MagicMock()
        mock_servicio_usuarios_class.return_value = mock_servicio
        mock_servicio.obtener_cliente_por_id.return_value = {
            "id": "cliente-1",
            "direccion": "Calle 123 #45-67",
            "telefono": "3001234567"
        }
        
        comando = CrearPlan(
            nombre="Plan de Visitas",
            id_usuario="user-1",
            fecha_inicio="2025-10-01T00:00:00",
            fecha_fin="2025-10-31T23:59:59",
            visitas_clientes=[
                ClienteVisita(
                    id_cliente="cliente-1",
                    visitas=["2025-10-05T10:00:00", "2025-10-15T14:00:00"]
                )
            ]
        )
        
        with self.app.app_context():
            resultado = self.handler.handle(comando)
        
        assert resultado['success'] is True
        assert 'plan_id' in resultado
    
    @patch('aplicacion.comandos.crear_plan.ServicioUsuarios')
    def test_crear_plan_nombre_vacio(self, mock_servicio_usuarios_class):
        """Test para validar error con nombre vacío"""
        comando = CrearPlan(
            nombre="",
            id_usuario="user-1",
            fecha_inicio="2025-10-01T00:00:00",
            fecha_fin="2025-10-31T23:59:59",
            visitas_clientes=[
                ClienteVisita(id_cliente="cliente-1", visitas=["2025-10-05T10:00:00"])
            ]
        )
        
        with self.app.app_context():
            resultado = self.handler.handle(comando)
        
        assert resultado['success'] is False
        assert resultado['code'] == 400
        assert 'nombre' in resultado['error'].lower()
    
    @patch('aplicacion.comandos.crear_plan.ServicioUsuarios')
    def test_crear_plan_id_usuario_vacio(self, mock_servicio_usuarios_class):
        """Test para validar error con id_usuario vacío"""
        comando = CrearPlan(
            nombre="Plan de Visitas",
            id_usuario="",
            fecha_inicio="2025-10-01T00:00:00",
            fecha_fin="2025-10-31T23:59:59",
            visitas_clientes=[
                ClienteVisita(id_cliente="cliente-1", visitas=["2025-10-05T10:00:00"])
            ]
        )
        
        with self.app.app_context():
            resultado = self.handler.handle(comando)
        
        assert resultado['success'] is False
        assert resultado['code'] == 400
        assert 'usuario' in resultado['error'].lower()
    
    @patch('aplicacion.comandos.crear_plan.ServicioUsuarios')
    def test_crear_plan_sin_visitas_clientes(self, mock_servicio_usuarios_class):
        """Test para validar error sin visitas_clientes"""
        comando = CrearPlan(
            nombre="Plan de Visitas",
            id_usuario="user-1",
            fecha_inicio="2025-10-01T00:00:00",
            fecha_fin="2025-10-31T23:59:59",
            visitas_clientes=[]
        )
        
        with self.app.app_context():
            resultado = self.handler.handle(comando)
        
        assert resultado['success'] is False
        assert resultado['code'] == 400
        assert 'cliente' in resultado['error'].lower() or 'visita' in resultado['error'].lower()
    
    @patch('aplicacion.comandos.crear_plan.ServicioUsuarios')
    def test_crear_plan_cliente_no_encontrado(self, mock_servicio_usuarios_class):
        """Test para validar error cuando cliente no existe"""
        mock_servicio = MagicMock()
        mock_servicio_usuarios_class.return_value = mock_servicio
        mock_servicio.obtener_cliente_por_id.return_value = None
        
        comando = CrearPlan(
            nombre="Plan de Visitas",
            id_usuario="user-1",
            fecha_inicio="2025-10-01T00:00:00",
            fecha_fin="2025-10-31T23:59:59",
            visitas_clientes=[
                ClienteVisita(id_cliente="cliente-inexistente", visitas=["2025-10-05T10:00:00"])
            ]
        )
        
        with self.app.app_context():
            resultado = self.handler.handle(comando)
        
        assert resultado['success'] is False
        assert resultado['code'] == 404
        assert 'no encontrado' in resultado['error'].lower()
    
    @patch('aplicacion.comandos.crear_plan.ServicioUsuarios')
    def test_crear_plan_fecha_visita_invalida(self, mock_servicio_usuarios_class):
        """Test para validar error con fecha de visita inválida"""
        mock_servicio = MagicMock()
        mock_servicio_usuarios_class.return_value = mock_servicio
        mock_servicio.obtener_cliente_por_id.return_value = {
            "id": "cliente-1",
            "direccion": "Calle 123 #45-67",
            "telefono": "3001234567"
        }
        
        comando = CrearPlan(
            nombre="Plan de Visitas",
            id_usuario="user-1",
            fecha_inicio="2025-10-01T00:00:00",
            fecha_fin="2025-10-31T23:59:59",
            visitas_clientes=[
                ClienteVisita(id_cliente="cliente-1", visitas=["fecha-invalida"])
            ]
        )
        
        with self.app.app_context():
            resultado = self.handler.handle(comando)
        
        assert resultado['success'] is False
        assert resultado['code'] == 400
        assert 'fecha' in resultado['error'].lower()
    
    @patch('aplicacion.comandos.crear_plan.ServicioUsuarios')
    def test_crear_plan_direccion_invalida(self, mock_servicio_usuarios_class):
        """Test para validar error con dirección inválida del cliente"""
        mock_servicio = MagicMock()
        mock_servicio_usuarios_class.return_value = mock_servicio
        mock_servicio.obtener_cliente_por_id.return_value = {
            "id": "cliente-1",
            "direccion": "",  # Dirección vacía
            "telefono": "3001234567"
        }
        
        comando = CrearPlan(
            nombre="Plan de Visitas",
            id_usuario="user-1",
            fecha_inicio="2025-10-01T00:00:00",
            fecha_fin="2025-10-31T23:59:59",
            visitas_clientes=[
                ClienteVisita(id_cliente="cliente-1", visitas=["2025-10-05T10:00:00"])
            ]
        )
        
        with self.app.app_context():
            resultado = self.handler.handle(comando)
        
        assert resultado['success'] is False
        assert resultado['code'] == 400
        assert 'dirección' in resultado['error'].lower() or 'direccion' in resultado['error'].lower()
    
    @patch('aplicacion.comandos.crear_plan.ServicioUsuarios')
    def test_crear_plan_direccion_muy_larga(self, mock_servicio_usuarios_class):
        """Test para validar error con dirección muy larga (>200 caracteres)"""
        mock_servicio = MagicMock()
        mock_servicio_usuarios_class.return_value = mock_servicio
        mock_servicio.obtener_cliente_por_id.return_value = {
            "id": "cliente-1",
            "direccion": "a" * 201,  # Más de 200 caracteres
            "telefono": "3001234567"
        }
        
        comando = CrearPlan(
            nombre="Plan de Visitas",
            id_usuario="user-1",
            fecha_inicio="2025-10-01T00:00:00",
            fecha_fin="2025-10-31T23:59:59",
            visitas_clientes=[
                ClienteVisita(id_cliente="cliente-1", visitas=["2025-10-05T10:00:00"])
            ]
        )
        
        with self.app.app_context():
            resultado = self.handler.handle(comando)
        
        assert resultado['success'] is False
        assert resultado['code'] == 400
        assert '200' in resultado['error'] or 'dirección' in resultado['error'].lower()
    
    @patch('aplicacion.comandos.crear_plan.ServicioUsuarios')
    def test_crear_plan_excepcion_general(self, mock_servicio_usuarios_class):
        """Test para validar manejo de excepciones generales"""
        # Mock que lanza excepción al obtener cliente
        mock_servicio = MagicMock()
        mock_servicio_usuarios_class.return_value = mock_servicio
        mock_servicio.obtener_cliente_por_id.side_effect = Exception("Error de conexión")
        
        comando = CrearPlan(
            nombre="Plan de Visitas",
            id_usuario="user-1",
            fecha_inicio="2025-10-01T00:00:00",
            fecha_fin="2025-10-31T23:59:59",
            visitas_clientes=[
                ClienteVisita(id_cliente="cliente-1", visitas=["2025-10-05T10:00:00"])
            ]
        )
        
        with self.app.app_context():
            resultado = self.handler.handle(comando)
        
        assert resultado['success'] is False
        assert 'error' in resultado
        # Debe tener código 500 o no tener código (default)
        assert 'code' not in resultado or resultado.get('code', 500) >= 500

