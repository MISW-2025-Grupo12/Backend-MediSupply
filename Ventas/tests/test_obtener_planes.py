import pytest
import sys
import os
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
import uuid
from flask import Flask

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from aplicacion.consultas.obtener_planes import ObtenerPlanes, ObtenerPlanesPorUsuario, ObtenerPlanesHandler, ObtenerPlanesPorUsuarioHandler
from config.db import db
from infraestructura.modelos import PlanVisitaModel, VisitaModel


class TestObtenerPlanes:
    """Tests unitarios para la consulta ObtenerPlanes"""
    
    def setup_method(self):
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
    
    def test_obtener_planes_consulta(self):
        """Test para crear la consulta ObtenerPlanes"""
        consulta = ObtenerPlanes()
        assert consulta is not None
    
    def test_obtener_planes_handler_sin_resultados(self):
        """Test para obtener planes cuando no hay resultados"""
        handler = ObtenerPlanesHandler()
        consulta = ObtenerPlanes()
        
        with self.app.app_context():
            resultado = handler.handle(consulta)
        
        assert isinstance(resultado, list)
        assert len(resultado) == 0
    
    def test_obtener_planes_handler_con_resultados(self):
        """Test para obtener planes con resultados"""
        handler = ObtenerPlanesHandler()
        consulta = ObtenerPlanes()
        
        with self.app.app_context():
            # Crear un plan de prueba
            plan = PlanVisitaModel(
                id="plan-1",
                nombre="Plan Test",
                id_usuario="user-1",
                fecha_inicio=datetime.now(),
                fecha_fin=datetime.now() + timedelta(days=30)
            )
            db.session.add(plan)
            
            # Crear una visita asociada
            visita = VisitaModel(
                id="visita-1",
                vendedor_id="user-1",
                cliente_id="cliente-1",
                fecha_programada=datetime.now() + timedelta(days=5),
                direccion="Calle 123",
                telefono="3001234567",
                estado="pendiente",
                plan_id="plan-1"
            )
            db.session.add(visita)
            db.session.commit()
            
            resultado = handler.handle(consulta)
        
        assert isinstance(resultado, list)
        assert len(resultado) > 0
        assert resultado[0]['id'] == "plan-1"
        assert 'visitas_clientes' in resultado[0]


class TestObtenerPlanesPorUsuario:
    """Tests unitarios para la consulta ObtenerPlanesPorUsuario"""
    
    def setup_method(self):
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
    
    def test_obtener_planes_por_usuario_consulta(self):
        """Test para crear la consulta ObtenerPlanesPorUsuario"""
        user_id = "user-1"
        consulta = ObtenerPlanesPorUsuario(user_id=user_id)
        assert consulta.user_id == user_id
    
    def test_obtener_planes_por_usuario_handler_sin_resultados(self):
        """Test para obtener planes por usuario cuando no hay resultados"""
        handler = ObtenerPlanesPorUsuarioHandler()
        consulta = ObtenerPlanesPorUsuario(user_id="usuario-inexistente")
        
        with self.app.app_context():
            resultado = handler.handle(consulta)
        
        assert isinstance(resultado, list)
        assert len(resultado) == 0
    
    def test_obtener_planes_por_usuario_handler_con_resultados(self):
        """Test para obtener planes por usuario con resultados"""
        handler = ObtenerPlanesPorUsuarioHandler()
        user_id = "user-1"
        consulta = ObtenerPlanesPorUsuario(user_id=user_id)
        
        with self.app.app_context():
            # Crear planes de prueba
            plan1 = PlanVisitaModel(
                id="plan-1",
                nombre="Plan 1",
                id_usuario=user_id,
                fecha_inicio=datetime.now(),
                fecha_fin=datetime.now() + timedelta(days=30)
            )
            plan2 = PlanVisitaModel(
                id="plan-2",
                nombre="Plan 2",
                id_usuario="user-2",  # Otro usuario
                fecha_inicio=datetime.now(),
                fecha_fin=datetime.now() + timedelta(days=30)
            )
            db.session.add(plan1)
            db.session.add(plan2)
            
            # Crear visitas asociadas
            visita1 = VisitaModel(
                id="visita-1",
                vendedor_id=user_id,
                cliente_id="cliente-1",
                fecha_programada=datetime.now() + timedelta(days=5),
                direccion="Calle 123",
                telefono="3001234567",
                estado="pendiente",
                plan_id="plan-1"
            )
            db.session.add(visita1)
            db.session.commit()
            
            resultado = handler.handle(consulta)
        
        assert isinstance(resultado, list)
        assert len(resultado) > 0
        # Debe retornar solo los planes del usuario
        for plan in resultado:
            assert plan['id_usuario'] == user_id
    
    @patch('aplicacion.consultas.obtener_planes.RepositorioPlanes')
    def test_obtener_planes_handler_excepcion(self, mock_repo_class):
        """Test para validar manejo de excepciones en ObtenerPlanesHandler"""
        # Mock que lanza excepción
        mock_repo = MagicMock()
        mock_repo_class.return_value = mock_repo
        mock_repo.obtener_todos.side_effect = Exception("Error de base de datos")
        
        handler = ObtenerPlanesHandler()
        consulta = ObtenerPlanes()
        
        with self.app.app_context():
            resultado = handler.handle(consulta)
        
        assert isinstance(resultado, list)
        assert len(resultado) == 0
    
    @patch('aplicacion.consultas.obtener_planes.RepositorioPlanes')
    def test_obtener_planes_por_usuario_handler_excepcion(self, mock_repo_class):
        """Test para validar manejo de excepciones en ObtenerPlanesPorUsuarioHandler"""
        # Mock que lanza excepción
        mock_repo = MagicMock()
        mock_repo_class.return_value = mock_repo
        mock_repo.obtener_por_usuario.side_effect = Exception("Error de base de datos")
        
        handler = ObtenerPlanesPorUsuarioHandler()
        consulta = ObtenerPlanesPorUsuario(user_id="user-1")
        
        with self.app.app_context():
            resultado = handler.handle(consulta)
        
        assert isinstance(resultado, list)
        assert len(resultado) == 0

