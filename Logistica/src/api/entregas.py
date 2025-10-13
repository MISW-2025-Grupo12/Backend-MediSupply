import seedwork.presentacion.api as api
import json
import random, uuid
from flask import request, Response, jsonify
from aplicacion.consultas.obtener_entregas import ObtenerEntregas
from seedwork.aplicacion.consultas import ejecutar_consulta
from aplicacion.mapeadores import MapeadorEntregaDTOJson
from infraestructura.servicio_pedidos import obtener_pedido_random

import random
from datetime import datetime, timedelta
from infraestructura.repositorios import RepositorioEntregaSQLite
from aplicacion.dto import EntregaDTO

import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Blueprint jerárquico bajo /api/logistica
bp = api.crear_blueprint('entrega', '/logistica/api/entregas')

# Endpoint temporal: Crear entregas
@bp.route('/creartemp', methods=['POST'])
def crear_entregas_temp():
    """
    Endpoint temporal: genera 20 entregas aleatorias (persistidas).
    Si hay pedidos disponibles, los asocia. Si no, genera datos mock.
    """
    repo = RepositorioEntregaSQLite()
    entregas_creadas = []

    try:
        for _ in range(20):
            pedido = obtener_pedido_random()

            # Si existe un pedido real
            if pedido:
                entrega_dto = EntregaDTO(
                    id=uuid.uuid4(),
                    direccion=pedido["cliente"]["direccion"],
                    fecha_entrega=datetime.now() + timedelta(days=random.randint(1, 7)),
                    pedido=pedido  # ✅ ahora asignamos todo el pedido aquí
                )

            # Si no hay pedidos disponibles, generamos datos ficticios
            else:
                entrega_dto = EntregaDTO(
                    id=uuid.uuid4(),
                    direccion=f"Calle {random.randint(10, 100)} # {random.randint(10, 50)}-{random.randint(1, 99)}",
                    fecha_entrega=datetime.now() + timedelta(days=random.randint(1, 7)),
                    pedido={
                        "id": str(uuid.uuid4()),
                        "cliente": {
                            "nombre": "Cliente Genérico",
                            "telefono": "3000000000",
                            "direccion": "Dirección genérica",
                            "avatar": "https://via.placeholder.com/64"
                        },
                        "productos": [
                            {"nombre": "Producto Mock 1", "cantidad": random.randint(1, 5)},
                            {"nombre": "Producto Mock 2", "cantidad": random.randint(1, 5)}
                        ]
                    }
                )

            # Guardamos en base de datos
            repo.crear(entrega_dto)
            entregas_creadas.append(entrega_dto.id)

        return jsonify({
            "message": f"✅ Se han creado {len(entregas_creadas)} entregas temporalmente.",
            "ids": [str(i) for i in entregas_creadas]
        }), 201

    except Exception as e:
        logger.error(f"Error creando entregas temporales: {e}")
        return jsonify({"error": str(e)}), 500

# Endpoint: Obtener entregas programadas
@bp.route('/', methods=['GET'])
def obtener_entregas():
    """
    HU-157: Consulta de entregas programadas.
    Permite visualizar las rutas asignadas a los conductores.
    """
    def parsear_fecha(valor):
            """Intenta parsear fecha con o sin hora."""
            try:
                return datetime.fromisoformat(valor)
            except ValueError:
                return datetime.strptime(valor, "%Y-%m-%d")

    try:
        fecha_inicio_str = request.args.get("fecha_inicio")
        fecha_fin_str = request.args.get("fecha_fin")

        fecha_inicio = parsear_fecha(fecha_inicio_str) if fecha_inicio_str else None
        fecha_fin = parsear_fecha(fecha_fin_str) if fecha_fin_str else None

        # Crear la consulta CQRS
        consulta = ObtenerEntregas(fecha_inicio=fecha_inicio, fecha_fin=fecha_fin)
        entregas_dto = ejecutar_consulta(consulta)

        # Aplicar filtro manual (por seguridad)
        if fecha_inicio and fecha_fin:
            # Si ambas fechas son iguales → filtrar solo ese día
            if fecha_inicio.date() == fecha_fin.date():
                entregas_dto = [
                    e for e in entregas_dto
                    if e.fecha_entrega.date() == fecha_inicio.date()
                ]
            else:
                # Si son diferentes → rango normal
                entregas_dto = [
                    e for e in entregas_dto
                    if fecha_inicio.date() <= e.fecha_entrega.date() <= fecha_fin.date()
                ]

        # Mapear DTO → JSON externo
        mapeador = MapeadorEntregaDTOJson()
        entregas_json = [mapeador.dto_a_externo(e) for e in entregas_dto]

        logger.info(f"✅ {len(entregas_json)} entregas consultadas correctamente")
        return Response(json.dumps(entregas_json), status=200, mimetype='application/json')

    except Exception as e:
        logger.error(f"❌ Error obteniendo entregas programadas: {e}")
        return Response(
            json.dumps({'error': f'Error interno del servidor: {str(e)}'}),
            status=500,
            mimetype='application/json'
        )