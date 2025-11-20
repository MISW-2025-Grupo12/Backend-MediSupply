import importlib
import os
import sys
from datetime import datetime, timedelta
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest
from flask import Flask


def test_create_test_app_health():
    from src.api.test_app import create_test_app

    app = create_test_app()
    client = app.test_client()

    response = client.get('/health')
    assert response.status_code == 200
    assert response.get_json()['status'] == 'up'


def test_main_main_runs(monkeypatch):
    """Test que verifica que main() puede ejecutarse correctamente"""
    # Mockear app antes de importar main
    mock_app = MagicMock()
    mock_app.run = MagicMock()
    
    # Mockear los módulos que se importan en main.py
    fake_module = SimpleNamespace(ManejadorInventarioAsignado=MagicMock())
    
    # Crear un módulo mock para api
    mock_api_module = MagicMock()
    mock_api_module.app = mock_app
    
    with patch.dict(sys.modules, {
        'aplicacion.eventos.consumidor_inventario_asignado': fake_module,
        'api': mock_api_module
    }):
        with patch('seedwork.infraestructura.pubsub.PublicadorPubSub', return_value=MagicMock()), \
             patch('seedwork.dominio.eventos.despachador_eventos.registrar_publicador'):
            
            # Limpiar el módulo main si ya está importado
            if 'src.main' in sys.modules:
                del sys.modules['src.main']
            
            # Importar main después de los mocks
            main_module = importlib.import_module('src.main')
            
            # Asegurar que app.run está mockeado
            monkeypatch.setenv('PORT', '6010')
            monkeypatch.setenv('HOST', '127.1.1.1')
            
            # Ejecutar main
            main_module.main()
            
            # Verificar que app.run fue llamado con los parámetros correctos
            mock_app.run.assert_called_once_with(host='127.1.1.1', port=6010, debug=False)


def test_seed_data_testing_mode():
    from src.config.seed import seed_data

    app = Flask(__name__)
    app.config['TESTING'] = True

    seed_data(app)


def test_seed_data_database_not_empty(monkeypatch):
    from src.config import seed

    app = Flask(__name__)
    app.config['TESTING'] = False

    monkeypatch.setattr(seed, 'is_database_empty', lambda: False)
    create_mock = MagicMock()
    monkeypatch.setattr(seed, '_create_seed_data', create_mock)

    seed.seed_data(app)
    create_mock.assert_not_called()


def test_seed_data_database_empty(monkeypatch):
    from src.config import seed

    app = Flask(__name__)
    app.config['TESTING'] = False

    monkeypatch.setattr(seed, 'is_database_empty', lambda: True)
    create_mock = MagicMock()
    monkeypatch.setattr(seed, '_create_seed_data', create_mock)

    seed.seed_data(app)
    create_mock.assert_called_once()


def test_init_test_db_creates_tables():
    from src.config.test_db import init_test_db

    app = Flask(__name__)
    init_test_db(app)

    assert app.config['SQLALCHEMY_DATABASE_URI'] == 'sqlite:///:memory:'
    assert app.config['TESTING'] is True


def test_seedwork_comandos_no_handler():
    from src.seedwork.aplicacion.comandos import Comando, ejecutar_comando

    with pytest.raises(NotImplementedError):
        ejecutar_comando(Comando())


def test_seedwork_consultas_no_handler():
    from src.seedwork.aplicacion.consultas import Consulta, ejecutar_consulta

    with pytest.raises(NotImplementedError):
        ejecutar_consulta(Consulta())


def test_dominio_fabricas_import():
    module = importlib.import_module('src.dominio.fabricas')
    assert hasattr(module, 'FabricaEntrega')


def test_dominio_repositorios_import():
    module = importlib.import_module('src.dominio.repositorios')
    assert hasattr(module, 'RepositorioEntrega')


def test_seedwork_dominio_fabricas_subclass():
    from src.seedwork.dominio.fabricas import Fabrica

    class FabricaConcreta(Fabrica):
        def crear_objeto(self, obj, mapeador=None):
            return obj

    fabrica = FabricaConcreta()
    assert fabrica.crear_objeto({'x': 1}) == {'x': 1}


class _FakeFuture:
    def result(self):
        return 'message-id'


class _FakePublisher:
    def __init__(self):
        self.created_topics = []

    def topic_path(self, project, topic):
        return f'{project}/{topic}'

    def create_topic(self, request):
        self.created_topics.append(request['name'])

    def publish(self, topic_path, data):
        return _FakeFuture()


class _FakeSubscriber:
    def __init__(self):
        self.created_subscriptions = {}

    def topic_path(self, project, topic):
        return f'{project}/{topic}'

    def subscription_path(self, project, subscription):
        return f'{project}/{subscription}'

    def create_subscription(self, request):
        self.created_subscriptions[request['name']] = request['topic']

    def get_subscription(self, request):
        raise Exception('not found')


def test_consumidor_pubsub_emulador(monkeypatch):
    monkeypatch.setenv('USE_PUBSUB_EMULATOR', 'true')

    with patch('src.seedwork.infraestructura.consumidor_pubsub.pubsub_v1.SubscriberClient', return_value=_FakeSubscriber()), \
            patch('src.seedwork.infraestructura.consumidor_pubsub.pubsub_v1.PublisherClient', return_value=_FakePublisher()), \
            patch('src.seedwork.infraestructura.consumidor_pubsub.threading.Thread') as mock_thread:

        mock_thread.return_value = MagicMock()

        from src.seedwork.infraestructura.consumidor_pubsub import ConsumidorPubSub

        consumidor = ConsumidorPubSub(project_id='demo', emulator_host='localhost:9999')
        consumidor.crear_suscripciones()
        consumidor.suscribirse_a_topic('demo-topic', 'demo-sub')
        consumidor.iniciar_escucha()

        assert 'demo-topic' in consumidor._subscriptions
        assert mock_thread.called


def test_consumidor_pubsub_sin_subscriber(monkeypatch):
    monkeypatch.setenv('USE_PUBSUB_EMULATOR', 'false')

    with patch('src.seedwork.infraestructura.consumidor_pubsub.pubsub_v1.SubscriberClient', side_effect=Exception('fail')), \
            patch('src.seedwork.infraestructura.consumidor_pubsub.pubsub_v1.PublisherClient', return_value=_FakePublisher()):

        from src.seedwork.infraestructura.consumidor_pubsub import ConsumidorPubSub

        consumidor = ConsumidorPubSub(project_id='demo', emulator_host='localhost:9999')
        assert consumidor._subscriber is None
        consumidor.crear_suscripciones()

