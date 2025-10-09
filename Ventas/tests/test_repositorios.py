import pytest
import sys
import os
from datetime import datetime, timedelta
import uuid
from flask import Flask

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from infraestructura.repositorios import RepositorioVisitaSQLite
from infraestructura.modelos import VisitaModel
from aplicacion.dto import VisitaDTO
from config.db import db


class TestRepositorioVisitaSQLite:
    
    def setup_method(self):
        self.app = Flask(__name__)
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        db.init_app(self.app)
        self.repositorio = RepositorioVisitaSQLite()
        self.fecha_futura = datetime.now() + timedelta(days=1)
    
    def test_crear_visita(self):
        visita_dto = VisitaDTO(
            id=uuid.uuid4(),
            vendedor_id=str(uuid.uuid4()),
            cliente_id=str(uuid.uuid4()),
            fecha_programada=self.fecha_futura,
            direccion="Calle 123 #45-67",
            telefono="3001234567",
            estado="pendiente",
            descripcion="Visita programada"
        )
        
        with self.app.app_context():
            db.create_all()
            resultado = self.repositorio.crear(visita_dto)
            
            assert resultado.id == visita_dto.id
            assert resultado.vendedor_id == visita_dto.vendedor_id
            assert resultado.cliente_id == visita_dto.cliente_id
            assert resultado.fecha_programada == visita_dto.fecha_programada
            assert resultado.direccion == visita_dto.direccion
            assert resultado.telefono == visita_dto.telefono
            assert resultado.estado == visita_dto.estado
            assert resultado.descripcion == visita_dto.descripcion
    
    def test_obtener_por_id_existente(self):
        visita_dto = VisitaDTO(
            id=uuid.uuid4(),
            vendedor_id=str(uuid.uuid4()),
            cliente_id=str(uuid.uuid4()),
            fecha_programada=self.fecha_futura,
            direccion="Calle 123 #45-67",
            telefono="3001234567",
            estado="pendiente",
            descripcion="Visita programada"
        )
        
        with self.app.app_context():
            db.create_all()
            self.repositorio.crear(visita_dto)
            
            resultado = self.repositorio.obtener_por_id(str(visita_dto.id))
            
            assert resultado is not None
            assert resultado.id == visita_dto.id
            assert resultado.vendedor_id == visita_dto.vendedor_id
            assert resultado.cliente_id == visita_dto.cliente_id
    
    def test_obtener_por_id_no_existente(self):
        with self.app.app_context():
            db.create_all()
            resultado = self.repositorio.obtener_por_id(str(uuid.uuid4()))
            
            assert resultado is None
    
    def test_obtener_todos(self):
        visita1_dto = VisitaDTO(
            id=uuid.uuid4(),
            vendedor_id=str(uuid.uuid4()),
            cliente_id=str(uuid.uuid4()),
            fecha_programada=self.fecha_futura,
            direccion="Calle 123",
            telefono="3001234567",
            estado="pendiente",
            descripcion="Visita 1"
        )
        
        visita2_dto = VisitaDTO(
            id=uuid.uuid4(),
            vendedor_id=str(uuid.uuid4()),
            cliente_id=str(uuid.uuid4()),
            fecha_programada=self.fecha_futura,
            direccion="Calle 456",
            telefono="3009876543",
            estado="completada",
            descripcion="Visita 2"
        )
        
        with self.app.app_context():
            db.create_all()
            self.repositorio.crear(visita1_dto)
            self.repositorio.crear(visita2_dto)
            
            resultado = self.repositorio.obtener_todos()
            
            assert len(resultado) == 2
            assert any(v.id == visita1_dto.id for v in resultado)
            assert any(v.id == visita2_dto.id for v in resultado)
    
    def test_obtener_todos_vacio(self):
        with self.app.app_context():
            db.create_all()
            resultado = self.repositorio.obtener_todos()
            
            assert len(resultado) == 0
