import json
import uuid
from datetime import datetime, date
from unittest.mock import patch

import pytest

from aplicacion.dto import RutaDTO, RutaEntregaDTO
from .conftest import get_logistica_url


class TestAPIRutas:
    def setup_method(self):
        self.init_db_patcher = patch('config.db.init_db')
        self.init_db_patcher.start()

        self.comando_patcher = patch('api.rutas.ejecutar_comando')
        self.mock_ejecutar_comando = self.comando_patcher.start()

        self.consulta_patcher = patch('api.rutas.ejecutar_consulta')
        self.mock_ejecutar_consulta = self.consulta_patcher.start()

        self.enriquecer_patcher = patch('api.rutas.enriquecer_ruta_con_bodega', side_effect=lambda data: data)
        self.enriquecer_patcher.start()

        from flask import Flask
        from api.rutas import bp

        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        self.app.register_blueprint(bp)
        self.client = self.app.test_client()

    def teardown_method(self):
        self.init_db_patcher.stop()
        self.comando_patcher.stop()
        self.consulta_patcher.stop()
        self.enriquecer_patcher.stop()

    def test_crear_ruta_exitoso(self):
        ruta_id = str(uuid.uuid4())
        entrega_id = str(uuid.uuid4())
        fecha_ruta = date.today()
        fecha_entrega = datetime.now()

        ruta_dto = RutaDTO(
            id=ruta_id,
            fecha_ruta=fecha_ruta,
            repartidor_id='repartidor-123',
            bodega_id='bodega-123',
            estado='Pendiente',
            entregas=[
                RutaEntregaDTO(
                    entrega_id=entrega_id,
                    direccion='Calle 123',
                    fecha_entrega=fecha_entrega,
                    pedido={'id': 'pedido-123', 'estado': 'confirmado'}
                )
            ]
        )

        self.mock_ejecutar_comando.return_value = ruta_dto

        payload = {
            'fecha_ruta': fecha_ruta.isoformat(),
            'repartidor_id': 'repartidor-123',
            'bodega_id': 'bodega-123',
            'entregas': [entrega_id]
        }

        response = self.client.post(get_logistica_url('rutas') + '/', json=payload)

        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['id'] == ruta_id
        assert data['repartidor_id'] == 'repartidor-123'
        assert data['entregas'][0]['id'] == entrega_id

    def test_crear_ruta_validacion_faltante(self):
        payload = {
            'repartidor_id': 'repartidor-123',
            'entregas': ['entrega-1']
        }

        response = self.client.post(get_logistica_url('rutas') + '/', json=payload)

        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert 'bodega_id' in data['error'].lower() or 'obligatorio' in data['error'].lower()

    def test_crear_ruta_sin_bodega_id(self):
        payload = {
            'fecha_ruta': date.today().isoformat(),
            'repartidor_id': 'repartidor-123',
            'entregas': ['entrega-1']
        }

        response = self.client.post(get_logistica_url('rutas') + '/', json=payload)

        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data

    def test_crear_ruta_error_comando(self):
        self.mock_ejecutar_comando.side_effect = Exception('Fallo al crear ruta')

        payload = {
            'fecha_ruta': date.today().isoformat(),
            'repartidor_id': 'repartidor-123',
            'bodega_id': 'bodega-123',
            'entregas': ['entrega-1']
        }

        response = self.client.post(get_logistica_url('rutas') + '/', json=payload)

        assert response.status_code == 500
        data = json.loads(response.data)
        assert 'error' in data

    def test_obtener_rutas_exitoso(self):
        ruta_dto = RutaDTO(
            id=str(uuid.uuid4()),
            fecha_ruta=date.today(),
            repartidor_id='repartidor-123',
            bodega_id='bodega-123',
            estado='Pendiente',
            entregas=[]
        )

        self.mock_ejecutar_consulta.return_value = [ruta_dto]

        response = self.client.get(get_logistica_url('rutas') + '/')

        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]['repartidor_id'] == 'repartidor-123'

    @patch('api.rutas.ejecutar_consulta')
    def test_obtener_rutas_error(self, mock_ejecutar_consulta):
        mock_ejecutar_consulta.side_effect = Exception('Error consultando rutas')

        response = self.client.get(get_logistica_url('rutas') + '/')

        assert response.status_code == 500
        data = json.loads(response.data)
        assert 'error' in data

    def test_obtener_rutas_por_repartidor(self):
        ruta_dto = RutaDTO(
            id=str(uuid.uuid4()),
            fecha_ruta=date.today(),
            repartidor_id='repartidor-999',
            bodega_id='bodega-999',
            estado='Pendiente',
            entregas=[]
        )

        self.mock_ejecutar_consulta.return_value = [ruta_dto]

        response = self.client.get(get_logistica_url('rutas_repartidor') + '/repartidor-999')

        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list)
        assert data[0]['repartidor_id'] == 'repartidor-999'

    def test_crear_ruta_fecha_invalida(self):
        payload = {
            'fecha_ruta': '31-12-2025',
            'repartidor_id': 'repartidor-123',
            'bodega_id': 'bodega-123',
            'entregas': ['entrega-1']
        }

        response = self.client.post(get_logistica_url('rutas') + '/', json=payload)

        assert response.status_code == 400

    def test_crear_ruta_sin_entregas(self):
        payload = {
            'fecha_ruta': date.today().isoformat(),
            'repartidor_id': 'repartidor-123',
            'bodega_id': 'bodega-123',
            'entregas': []
        }

        response = self.client.post(get_logistica_url('rutas') + '/', json=payload)

        assert response.status_code == 400

    def test_obtener_rutas_fecha_invalida(self):
        response = self.client.get(get_logistica_url('rutas') + '/?fecha=31-12-2025')

        assert response.status_code == 400

    def test_obtener_rutas_error(self):
        self.mock_ejecutar_consulta.side_effect = Exception('fallo consulta')

        response = self.client.get(get_logistica_url('rutas') + '/')

        assert response.status_code == 500

    def test_obtener_rutas_por_repartidor_error(self):
        self.mock_ejecutar_consulta.side_effect = ValueError('fecha mala')

        response = self.client.get(get_logistica_url('rutas_repartidor') + '/repartidor-1?fecha=2025-10-33')

        assert response.status_code == 400

