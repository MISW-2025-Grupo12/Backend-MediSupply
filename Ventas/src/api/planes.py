import seedwork.presentacion.api as api
import json
from flask import request, Response
from aplicacion.comandos.crear_plan import CrearPlan, ClienteVisita
from aplicacion.consultas.obtener_planes import ObtenerPlanes, ObtenerPlanesPorUsuario
from seedwork.aplicacion.comandos import ejecutar_comando
from seedwork.aplicacion.consultas import ejecutar_consulta
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

bp = api.crear_blueprint('planes', '/ventas/api/planes')


@bp.route('/', methods=['POST'])
def crear_plan():
    """Crear un nuevo plan de ventas con sus visitas asociadas"""
    try:
        data = request.json

        if not data:
            return Response(
                json.dumps({'error': 'Se requiere un JSON válido'}),
                status=400,
                mimetype='application/json'
            )

        # Convertir diccionarios de visitas_clientes a objetos ClienteVisita
        visitas_clientes_raw = data.get('visitas_clientes', [])
        visitas_clientes = [
            ClienteVisita(
                id_cliente=cliente_dict.get('id_cliente', ''),
                visitas=cliente_dict.get('visitas', [])
            )
            for cliente_dict in visitas_clientes_raw
        ]

        comando = CrearPlan(
            nombre=data.get('nombre', ''),
            id_usuario=data.get('id_usuario', ''),
            fecha_inicio=data.get('fecha_inicio'),
            fecha_fin=data.get('fecha_fin'),
            visitas_clientes=visitas_clientes
        )

        resultado = ejecutar_comando(comando)
        status_code = 201 if resultado.get('success') else resultado.get('code', 400)
        return Response(
            json.dumps(resultado),
            status=status_code,
            mimetype='application/json'
        )

    except Exception as e:
        logger.error(f"Error creando plan: {e}")
        return Response(
            json.dumps({'error': f'Error interno: {str(e)}'}),
            status=500,
            mimetype='application/json'
        )


@bp.route('/', methods=['GET'])
def obtener_planes():
    """Obtener planes de ventas, filtrados por usuario si aplica"""
    try:
        user_id = request.args.get('user_id', '')
        rol = request.headers.get('X-User-Role', 'VENDEDOR')

        if rol.upper() == 'ADMINISTRADOR' and not user_id:
            consulta = ObtenerPlanes()
        else:
            consulta = ObtenerPlanesPorUsuario(user_id=user_id)

        planes = ejecutar_consulta(consulta)
        return Response(
            json.dumps({'success': True, 'planes': planes}),
            status=200,
            mimetype='application/json'
        )

    except Exception as e:
        logger.error(f"Error obteniendo planes: {e}")
        return Response(
            json.dumps({'error': f'Error interno: {str(e)}'}),
            status=500,
            mimetype='application/json'
        )
