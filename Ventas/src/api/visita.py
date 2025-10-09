import seedwork.presentacion.api as api
import json
from datetime import datetime
from flask import request, Response, Blueprint
from aplicacion.comandos.crear_visita import CrearVisita
from aplicacion.consultas.obtener_visitas import ObtenerVisitas
from aplicacion.consultas.obtener_visitas_por_vendedor import ObtenerVisitasPorVendedor
from seedwork.aplicacion.comandos import ejecutar_comando
from seedwork.aplicacion.consultas import ejecutar_consulta
from aplicacion.mapeadores import MapeadorVisitaAgregacionDTOJson

import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

bp = api.crear_blueprint('visita', '/api/visitas')

@bp.route('/', methods=['POST'])
def crear_visita():
    try:
        visita_dict = request.json
        
        if not visita_dict:
            return Response(
                json.dumps({'error': 'Se requiere un JSON válido'}), 
                status=400, 
                mimetype='application/json'
            )
        
        # Convertir fecha_programada de string a datetime
        fecha_programada = None
        if 'fecha_programada' in visita_dict:
            try:
                # Parsear fecha ISO
                fecha_programada = datetime.fromisoformat(visita_dict['fecha_programada'].replace('Z', '+00:00'))
                # Remover zona horaria para que sea compatible con datetime.now()
                if fecha_programada.tzinfo is not None:
                    fecha_programada = fecha_programada.replace(tzinfo=None)
            except ValueError:
                return Response(
                    json.dumps({'error': 'Formato de fecha inválido. Use ISO format'}), 
                    status=400, 
                    mimetype='application/json'
                )
        
        comando = CrearVisita(
            vendedor_id=visita_dict.get('vendedor_id', ''),
            cliente_id=visita_dict.get('cliente_id', ''),
            fecha_programada=fecha_programada or datetime.now(),
            direccion=visita_dict.get('direccion', ''),
            telefono=visita_dict.get('telefono', ''),
            estado=visita_dict.get('estado', 'pendiente'),
            descripcion=visita_dict.get('descripcion', '')
        )
        
        resultado = ejecutar_comando(comando)
        
        mapeador = MapeadorVisitaAgregacionDTOJson()
        visita_json = mapeador.agregacion_a_externo(resultado)
        
        return Response(
            json.dumps(visita_json), 
            status=201, 
            mimetype='application/json'
        )
        
    except ValueError as e:
        return Response(
            json.dumps({'error': str(e)}), 
            status=400, 
            mimetype='application/json'
        )
    except Exception as e:
        logger.error(f"Error creando visita: {e}")
        return Response(
            json.dumps({'error': f'Error interno del servidor: {str(e)}'}), 
            status=500, 
            mimetype='application/json'
        )

@bp.route('/', methods=['GET'])
def obtener_visitas():
    try:
        estado = request.args.get('estado')
        
        consulta = ObtenerVisitas(estado=estado)
        
        visitas_agregacion = ejecutar_consulta(consulta)
        
        mapeador = MapeadorVisitaAgregacionDTOJson()
        visitas_json = mapeador.agregaciones_a_externo(visitas_agregacion)
        
        return Response(
            json.dumps(visitas_json), 
            status=200, 
            mimetype='application/json'
        )
        
    except Exception as e:
        logger.error(f"Error obteniendo visitas con agregación: {e}")
        return Response(
            json.dumps({'error': f'Error interno del servidor: {str(e)}'}), 
            status=500, 
            mimetype='application/json'
        )

@bp.route('/vendedor/<vendedor_id>', methods=['GET'])
def obtener_visitas_por_vendedor(vendedor_id):
    try:
        estado = request.args.get('estado')
        
        consulta = ObtenerVisitasPorVendedor(vendedor_id=vendedor_id, estado=estado)
        
        visitas_agregacion = ejecutar_consulta(consulta)
        
        mapeador = MapeadorVisitaAgregacionDTOJson()
        visitas_json = mapeador.agregaciones_a_externo(visitas_agregacion)
        
        return Response(
            json.dumps(visitas_json), 
            status=200, 
            mimetype='application/json'
        )
        
    except Exception as e:
        logger.error(f"Error obteniendo visitas por vendedor: {e}")
        return Response(
            json.dumps({'error': f'Error interno del servidor: {str(e)}'}), 
            status=500, 
            mimetype='application/json'
        )
