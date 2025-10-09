import seedwork.presentacion.api as api
import json
from flask import request, Response
from aplicacion.consultas.obtener_entregas import ObtenerEntregas
from seedwork.aplicacion.consultas import ejecutar_consulta
from aplicacion.mapeadores import MapeadorEntregaDTOJson

import random
from datetime import datetime, timedelta
from infraestructura.repositorios import RepositorioEntregaSQLite
from aplicacion.dto import EntregaDTO

import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Blueprint jerárquico bajo /api/logistica
bp = api.crear_blueprint('entrega', '/api/logistica/entregas')

# Endpoint temporal: Crear entregas
@bp.route('/creartemp', methods=['POST'])
def crear_entregas_temp():
    """
    Endpoint temporal: genera 20 entregas aleatorias para pruebas.
    """
    try:
        repo = RepositorioEntregaSQLite()
        for i in range(20):
            entrega = EntregaDTO(
                direccion=f"Calle {random.randint(1, 99)} #{random.randint(1, 99)}-{random.randint(1, 99)}",
                fecha_entrega=datetime.now() + timedelta(days=random.randint(1, 10)),
                producto_id=f"producto-{random.randint(1000, 9999)}",
                cliente_id=f"cliente-{random.randint(1000, 9999)}"
            )
            repo.crear(entrega)

        return {"message": "✅ 20 entregas generadas exitosamente"}, 201

    except Exception as e:
        return {"error": f"❌ Error generando entregas: {str(e)}"}, 500

# Endpoint: Obtener entregas programadas
@bp.route('/', methods=['GET'])
def obtener_entregas():
    """
    HU-157: Consulta de entregas programadas.
    Permite visualizar las rutas asignadas a los conductores.
    """
    try:
        # Crear la consulta CQRS
        consulta = ObtenerEntregas()

        # Ejecutar la consulta (mock por ahora)
        entregas_dto = ejecutar_consulta(consulta)

        # Convertir DTO → JSON externo
        mapeador = MapeadorEntregaDTOJson()
        entregas_json = []
        for entrega in entregas_dto:
            entregas_json.append(mapeador.dto_a_externo(entrega))

        logger.info(f"✅ {len(entregas_json)} entregas programadas consultadas correctamente")

        return Response(
            json.dumps(entregas_json),
            status=200,
            mimetype='application/json'
        )

    except Exception as e:
        logger.error(f"❌ Error obteniendo entregas programadas: {e}")
        return Response(
            json.dumps({'error': f'Error interno del servidor: {str(e)}'}),
            status=500,
            mimetype='application/json'
        )
