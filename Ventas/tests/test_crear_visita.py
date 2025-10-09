import pytest
import sys
import os
from unittest.mock import Mock, patch
from datetime import datetime, timedelta
import uuid
from flask import Flask

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from aplicacion.comandos.crear_visita import CrearVisita, CrearVisitaHandler
from aplicacion.dto import VisitaDTO
from aplicacion.dto_agregacion import VisitaAgregacionDTO
from config.db import db


class TestCrearVisita:
    
    def setup_method(self):
        self.handler = CrearVisitaHandler()
        self.fecha_futura = datetime.now() + timedelta(days=1)
        self.vendedor_id = str(uuid.uuid4())
        self.cliente_id = str(uuid.uuid4())
        self.app = Flask(__name__)
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        db.init_app(self.app)
    
    def test_crear_visita_exitoso(self):
        comando = CrearVisita(
            vendedor_id=self.vendedor_id,
            cliente_id=self.cliente_id,
            fecha_programada=self.fecha_futura,
            direccion="Calle 123 #45-67",
            telefono="3001234567",
            estado="pendiente",
            descripcion="Visita programada"
        )
        
        vendedor_mock = {
            'id': self.vendedor_id,
            'nombre': 'Juan Pérez',
            'email': 'juan.perez@empresa.com',
            'telefono': '3001234567',
            'direccion': 'Calle 123 #45-67'
        }
        
        cliente_mock = {
            'id': self.cliente_id,
            'nombre': 'Hospital San Ignacio',
            'email': 'contacto@sanignacio.com',
            'telefono': '3115566778',
            'direccion': 'Cra 11 # 89 - 76'
        }
        
        visita_guardada = VisitaDTO(
            id=uuid.uuid4(),
            vendedor_id=self.vendedor_id,
            cliente_id=self.cliente_id,
            fecha_programada=self.fecha_futura,
            direccion="Calle 123 #45-67",
            telefono="3001234567",
            estado="pendiente",
            descripcion="Visita programada"
        )
        
        mock_repo = Mock()
        mock_servicio_usuarios = Mock()
        
        mock_servicio_usuarios.obtener_vendedor_por_id.return_value = vendedor_mock
        mock_servicio_usuarios.obtener_cliente_por_id.return_value = cliente_mock
        mock_repo.crear.return_value = visita_guardada
        
        handler = CrearVisitaHandler(
            repositorio=mock_repo,
            servicio_usuarios=mock_servicio_usuarios
        )
        
        with self.app.app_context():
            db.create_all()
            resultado = handler.handle(comando)
        
        assert isinstance(resultado, VisitaAgregacionDTO)
        assert resultado.vendedor_nombre == "Juan Pérez"
        assert resultado.cliente_nombre == "Hospital San Ignacio"
        mock_servicio_usuarios.obtener_vendedor_por_id.assert_called_once_with(self.vendedor_id)
        mock_servicio_usuarios.obtener_cliente_por_id.assert_called_once_with(self.cliente_id)
        mock_repo.crear.assert_called_once()
    
    def test_crear_visita_vendedor_no_existe(self):
        comando = CrearVisita(
            vendedor_id=self.vendedor_id,
            cliente_id=self.cliente_id,
            fecha_programada=self.fecha_futura,
            direccion="Calle 123 #45-67",
            telefono="3001234567",
            estado="pendiente",
            descripcion="Visita programada"
        )
        
        mock_servicio_usuarios = Mock()
        mock_servicio_usuarios.obtener_vendedor_por_id.return_value = None
        
        handler = CrearVisitaHandler(servicio_usuarios=mock_servicio_usuarios)
        
        with self.app.app_context():
            db.create_all()
            with pytest.raises(ValueError, match="Vendedor .* no existe"):
                handler.handle(comando)
    
    def test_crear_visita_cliente_no_existe(self):
        comando = CrearVisita(
            vendedor_id=self.vendedor_id,
            cliente_id=self.cliente_id,
            fecha_programada=self.fecha_futura,
            direccion="Calle 123 #45-67",
            telefono="3001234567",
            estado="pendiente",
            descripcion="Visita programada"
        )
        
        vendedor_mock = {
            'id': self.vendedor_id,
            'nombre': 'Juan Pérez',
            'email': 'juan.perez@empresa.com',
            'telefono': '3001234567',
            'direccion': 'Calle 123 #45-67'
        }
        
        mock_servicio_usuarios = Mock()
        mock_servicio_usuarios.obtener_vendedor_por_id.return_value = vendedor_mock
        mock_servicio_usuarios.obtener_cliente_por_id.return_value = None
        
        handler = CrearVisitaHandler(servicio_usuarios=mock_servicio_usuarios)
        
        with self.app.app_context():
            db.create_all()
            with pytest.raises(ValueError, match="Cliente .* no existe"):
                handler.handle(comando)
    
    def test_crear_visita_vendedor_id_vacio(self):
        comando = CrearVisita(
            vendedor_id="",
            cliente_id=self.cliente_id,
            fecha_programada=self.fecha_futura,
            direccion="Calle 123 #45-67",
            telefono="3001234567",
            estado="pendiente",
            descripcion="Visita programada"
        )
        
        with self.app.app_context():
            db.create_all()
            with pytest.raises(Exception):
                self.handler.handle(comando)
    
    def test_crear_visita_cliente_id_vacio(self):
        comando = CrearVisita(
            vendedor_id=self.vendedor_id,
            cliente_id="",
            fecha_programada=self.fecha_futura,
            direccion="Calle 123 #45-67",
            telefono="3001234567",
            estado="pendiente",
            descripcion="Visita programada"
        )
        
        with self.app.app_context():
            db.create_all()
            with pytest.raises(Exception):
                self.handler.handle(comando)
    
    def test_crear_visita_fecha_pasada(self):
        fecha_pasada = datetime.now() - timedelta(days=1)
        comando = CrearVisita(
            vendedor_id=self.vendedor_id,
            cliente_id=self.cliente_id,
            fecha_programada=fecha_pasada,
            direccion="Calle 123 #45-67",
            telefono="3001234567",
            estado="pendiente",
            descripcion="Visita programada"
        )
        
        with self.app.app_context():
            db.create_all()
            with pytest.raises(Exception):
                self.handler.handle(comando)
    
    def test_crear_visita_estado_invalido(self):
        comando = CrearVisita(
            vendedor_id=self.vendedor_id,
            cliente_id=self.cliente_id,
            fecha_programada=self.fecha_futura,
            direccion="Calle 123 #45-67",
            telefono="3001234567",
            estado="invalido",
            descripcion="Visita programada"
        )
        
        with self.app.app_context():
            db.create_all()
            with pytest.raises(Exception):
                self.handler.handle(comando)
