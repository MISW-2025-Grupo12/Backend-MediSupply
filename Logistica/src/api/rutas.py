import seedwork.presentacion.api as api
import json
from datetime import datetime
from flask import request, Response
from seedwork.aplicacion.comandos import ejecutar_comando
from seedwork.aplicacion.consultas import ejecutar_consulta
from aplicacion.comandos.crear_ruta import CrearRuta
from aplicacion.consultas.obtener_rutas import ObtenerRutas
from aplicacion.mapeadores import MapeadorRutaDTOJson
from infraestructura.repositorios import RepositorioInventarioSQLite, RepositorioBodegaSQLite

bp = api.crear_blueprint('ruta', '/logistica/api/rutas')


def parsear_fecha(valor):
    if not valor:
        return None
    try:
        return datetime.fromisoformat(valor).date()
    except ValueError:
        return datetime.strptime(valor, "%Y-%m-%d").date()


def enriquecer_ubicaciones(ruta_json):
    repo_inventario = RepositorioInventarioSQLite()
    repo_bodega = RepositorioBodegaSQLite()

    for entrega in ruta_json.get('entregas', []):
        pedido = entrega.get('pedido') or {}
        productos = pedido.get('productos') or []

        for producto in productos:
            producto_id = producto.get('producto_id')
            ubicaciones = []

            if producto_id:
                inventarios = repo_inventario.obtener_por_producto_id(producto_id)
                inventario = next((inv for inv in inventarios if inv.bodega_id), None)

                if inventario:
                    bodega = repo_bodega.obtener_por_id(inventario.bodega_id) if inventario.bodega_id else None
                    ubicaciones.append({
                        'bodega_id': inventario.bodega_id,
                        'nombre_bodega': bodega.nombre if bodega else 'Sin asignar',
                        'direccion_bodega': bodega.direccion if bodega else '',
                        'pasillo': getattr(inventario, 'pasillo', None),
                        'estante': getattr(inventario, 'estante', None)
                    })

            producto['ubicaciones'] = ubicaciones

    return ruta_json


@bp.route('/', methods=['POST'])
def crear_ruta():
    try:
        payload = request.get_json() or {}
        fecha_ruta = parsear_fecha(payload.get('fecha_ruta'))
        repartidor_id = payload.get('repartidor_id')
        entregas = payload.get('entregas', [])

        if not fecha_ruta:
            return Response(json.dumps({'error': 'El campo fecha_ruta es obligatorio'}),
                            status=400, mimetype='application/json')
        if not repartidor_id:
            return Response(json.dumps({'error': 'El campo repartidor_id es obligatorio'}),
                            status=400, mimetype='application/json')
        if not entregas or not isinstance(entregas, list):
            return Response(json.dumps({'error': 'Debe proporcionar una lista de entregas'}),
                            status=400, mimetype='application/json')

        comando = CrearRuta(
            fecha_ruta=fecha_ruta,
            repartidor_id=repartidor_id,
            entregas=entregas
        )

        ruta_creada = ejecutar_comando(comando)
        mapeador = MapeadorRutaDTOJson()
        ruta_json = enriquecer_ubicaciones(mapeador.dto_a_externo(ruta_creada))

        return Response(json.dumps(ruta_json), status=201, mimetype='application/json')
    except ValueError as error:
        return Response(json.dumps({'error': str(error)}), status=400, mimetype='application/json')
    except Exception as error:
        return Response(json.dumps({'error': f'Error interno del servidor: {str(error)}'}),
                        status=500, mimetype='application/json')


@bp.route('/', methods=['GET'])
def obtener_rutas():
    try:
        fecha = parsear_fecha(request.args.get('fecha'))
        repartidor_id = request.args.get('repartidor_id')

        consulta = ObtenerRutas(fecha=fecha, repartidor_id=repartidor_id)
        rutas = ejecutar_consulta(consulta)
        mapeador = MapeadorRutaDTOJson()

        rutas_json = [enriquecer_ubicaciones(mapeador.dto_a_externo(ruta)) for ruta in rutas]

        return Response(json.dumps(rutas_json), status=200, mimetype='application/json')
    except ValueError as error:
        return Response(json.dumps({'error': str(error)}), status=400, mimetype='application/json')
    except Exception as error:
        return Response(json.dumps({'error': f'Error interno del servidor: {str(error)}'}),
                        status=500, mimetype='application/json')


@bp.route('/repartidor/<repartidor_id>', methods=['GET'])
def obtener_rutas_por_repartidor(repartidor_id):
    try:
        fecha = parsear_fecha(request.args.get('fecha'))
        consulta = ObtenerRutas(fecha=fecha, repartidor_id=repartidor_id)
        rutas = ejecutar_consulta(consulta)
        mapeador = MapeadorRutaDTOJson()
        rutas_json = [enriquecer_ubicaciones(mapeador.dto_a_externo(ruta)) for ruta in rutas]
        return Response(json.dumps(rutas_json), status=200, mimetype='application/json')
    except ValueError as error:
        return Response(json.dumps({'error': str(error)}), status=400, mimetype='application/json')
    except Exception as error:
        return Response(json.dumps({'error': f'Error interno del servidor: {str(error)}'}),
                        status=500, mimetype='application/json')

