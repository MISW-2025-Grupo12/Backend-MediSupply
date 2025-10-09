import pytest
import sys
import os
from unittest.mock import Mock
from datetime import datetime, timedelta
import uuid
from flask import Flask

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from aplicacion.consultas.obtener_visitas import ObtenerVisitas, ObtenerVisitasHandler
from aplicacion.dto import VisitaDTO
from aplicacion.dto_agregacion import VisitaAgregacionDTO
from config.db import db


class TestObtenerVisitas:
    
    def setup_method(self):
        self.handler = ObtenerVisitasHandler()
        self.fecha_futura = datetime.now() + timedelta(days=1)
        self.vendedor_id = str(uuid.uuid4())
        self.cliente_id = str(uuid.uuid4())
        self.app = Flask(__name__)
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        db.init_app(self.app)
    
    def test_obtener_visitas_exitoso(self):
        consulta = ObtenerVisitas()
        
        visita1 = VisitaDTO(
            id=uuid.uuid4(),
            vendedor_id=self.vendedor_id,
            cliente_id=self.cliente_id,
            fecha_programada=self.fecha_futura,
            direccion="Calle 123",
            telefono="3001234567",
            estado="pendiente",
            descripcion="Visita 1"
        )
        
        visita2 = VisitaDTO(
            id=uuid.uuid4(),
            vendedor_id=self.vendedor_id,
            cliente_id=str(uuid.uuid4()),
            fecha_programada=self.fecha_futura,
            direccion="Calle 456",
            telefono="3009876543",
            estado="completada",
            descripcion="Visita 2"
        )
        
        vendedor_mock = {
            'id': self.vendedor_id,
            'nombre': 'Juan Pérez',
            'email': 'juan.perez@empresa.com',
            'telefono': '3001234567',
            'direccion': 'Calle 123'
        }
        
        cliente1_mock = {
            'id': self.cliente_id,
            'nombre': 'Hospital San Ignacio',
            'email': 'contacto@sanignacio.com',
            'telefono': '3115566778',
            'direccion': 'Cra 11 #89-76'
        }
        
        cliente2_mock = {
            'id': str(uuid.uuid4()),
            'nombre': 'Clínica Marly',
            'email': 'contacto@clinica.com',
            'telefono': '3115566778',
            'direccion': 'Cra 11 #89-76'
        }
        
        mock_repo = Mock()
        mock_servicio_usuarios = Mock()
        
        mock_repo.obtener_todos.return_value = [visita1, visita2]
        mock_servicio_usuarios.obtener_vendedor_por_id.return_value = vendedor_mock
        mock_servicio_usuarios.obtener_cliente_por_id.side_effect = [cliente1_mock, cliente2_mock]
        
        handler = ObtenerVisitasHandler(
            repositorio=mock_repo,
            servicio_usuarios=mock_servicio_usuarios
        )
        
        with self.app.app_context():
            db.create_all()
            resultado = handler.handle(consulta)
        
        assert len(resultado) == 2
        assert all(isinstance(agregacion, VisitaAgregacionDTO) for agregacion in resultado)
        assert resultado[0].vendedor_nombre == "Juan Pérez"
        assert resultado[0].cliente_nombre == "Hospital San Ignacio"
        assert resultado[1].cliente_nombre == "Clínica Marly"
    
    def test_obtener_visitas_filtro_estado(self):
        consulta = ObtenerVisitas(estado="pendiente")
        
        visita1 = VisitaDTO(
            id=uuid.uuid4(),
            vendedor_id=self.vendedor_id,
            cliente_id=self.cliente_id,
            fecha_programada=self.fecha_futura,
            direccion="Calle 123",
            telefono="3001234567",
            estado="pendiente",
            descripcion="Visita pendiente"
        )
        
        visita2 = VisitaDTO(
            id=uuid.uuid4(),
            vendedor_id=self.vendedor_id,
            cliente_id=str(uuid.uuid4()),
            fecha_programada=self.fecha_futura,
            direccion="Calle 456",
            telefono="3009876543",
            estado="completada",
            descripcion="Visita completada"
        )
        
        vendedor_mock = {
            'id': self.vendedor_id,
            'nombre': 'Juan Pérez',
            'email': 'juan.perez@empresa.com',
            'telefono': '3001234567',
            'direccion': 'Calle 123'
        }
        
        cliente_mock = {
            'id': self.cliente_id,
            'nombre': 'Hospital San Ignacio',
            'email': 'contacto@sanignacio.com',
            'telefono': '3115566778',
            'direccion': 'Cra 11 #89-76'
        }
        
        mock_repo = Mock()
        mock_servicio_usuarios = Mock()
        
        mock_repo.obtener_todos.return_value = [visita1, visita2]
        mock_servicio_usuarios.obtener_vendedor_por_id.return_value = vendedor_mock
        mock_servicio_usuarios.obtener_cliente_por_id.return_value = cliente_mock
        
        handler = ObtenerVisitasHandler(
            repositorio=mock_repo,
            servicio_usuarios=mock_servicio_usuarios
        )
        
        with self.app.app_context():
            db.create_all()
            resultado = handler.handle(consulta)
        
        assert len(resultado) == 1
        assert resultado[0].estado == "pendiente"
    
    def test_obtener_visitas_vendedor_no_existe(self):
        consulta = ObtenerVisitas()
        
        visita = VisitaDTO(
            id=uuid.uuid4(),
            vendedor_id=self.vendedor_id,
            cliente_id=self.cliente_id,
            fecha_programada=self.fecha_futura,
            direccion="Calle 123",
            telefono="3001234567",
            estado="pendiente",
            descripcion="Visita 1"
        )
        
        mock_repo = Mock()
        mock_servicio_usuarios = Mock()
        
        mock_repo.obtener_todos.return_value = [visita]
        mock_servicio_usuarios.obtener_vendedor_por_id.return_value = None
        
        handler = ObtenerVisitasHandler(
            repositorio=mock_repo,
            servicio_usuarios=mock_servicio_usuarios
        )
        
        with self.app.app_context():
            db.create_all()
            resultado = handler.handle(consulta)
        
        assert len(resultado) == 0
    
    def test_obtener_visitas_cliente_no_existe(self):
        consulta = ObtenerVisitas()
        
        visita = VisitaDTO(
            id=uuid.uuid4(),
            vendedor_id=self.vendedor_id,
            cliente_id=self.cliente_id,
            fecha_programada=self.fecha_futura,
            direccion="Calle 123",
            telefono="3001234567",
            estado="pendiente",
            descripcion="Visita 1"
        )
        
        vendedor_mock = {
            'id': self.vendedor_id,
            'nombre': 'Juan Pérez',
            'email': 'juan.perez@empresa.com',
            'telefono': '3001234567',
            'direccion': 'Calle 123'
        }
        
        mock_repo = Mock()
        mock_servicio_usuarios = Mock()
        
        mock_repo.obtener_todos.return_value = [visita]
        mock_servicio_usuarios.obtener_vendedor_por_id.return_value = vendedor_mock
        mock_servicio_usuarios.obtener_cliente_por_id.return_value = None
        
        handler = ObtenerVisitasHandler(
            repositorio=mock_repo,
            servicio_usuarios=mock_servicio_usuarios
        )
        
        with self.app.app_context():
            db.create_all()
            resultado = handler.handle(consulta)
        
        assert len(resultado) == 0
