import seedwork.presentacion.api as api
import json
from flask import request, Response, Blueprint
from aplicacion.consultas.obtener_repartidores import ObtenerRepartidores
from seedwork.aplicacion.consultas import ejecutar_consulta
from aplicacion.mapeadores import MapeadorRepartidorDTOJson
from seedwork.presentacion.paginacion import paginar_resultados, extraer_parametros_paginacion

import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

bp = api.crear_blueprint('repartidor', '/usuarios/api/repartidores')

# Endpoint para obtener todos los repartidores
@bp.route('/', methods=['GET'])
def obtener_repartidores():
    try:
        # Obtener parámetros de paginación
        page, page_size = extraer_parametros_paginacion(request.args)
        
        # Crear consulta
        consulta = ObtenerRepartidores()
        
        # Ejecutar consulta
        repartidores = ejecutar_consulta(consulta)
        
        # Convertir DTOs a JSON
        mapeador = MapeadorRepartidorDTOJson()
        repartidores_json = mapeador.dtos_a_externo(repartidores)
        
        # Aplicar paginación
        resultado_paginado = paginar_resultados(repartidores_json, page=page, page_size=page_size)
        
        return Response(
            json.dumps(resultado_paginado), 
            status=200, 
            mimetype='application/json'
        )
        
    except Exception as e:
        logger.error(f"Error obteniendo repartidores: {e}")
        return Response(
            json.dumps({'error': f'Error interno del servidor: {str(e)}'}), 
            status=500, 
            mimetype='application/json'
        )

