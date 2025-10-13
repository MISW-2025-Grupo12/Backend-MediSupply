import seedwork.presentacion.api as api
import json
from flask import request, Response
from aplicacion.comandos.inicializar_bodegas import InicializarBodegas
from aplicacion.consultas.obtener_bodegas import ObtenerBodegas
from aplicacion.consultas.obtener_productos_por_bodega import ObtenerProductosPorBodega
from aplicacion.consultas.obtener_ubicaciones_producto import ObtenerUbicacionesProducto
from seedwork.aplicacion.comandos import ejecutar_comando
from seedwork.aplicacion.consultas import ejecutar_consulta

bp = api.crear_blueprint('bodegas', '/logistica/api/bodegas')

@bp.route('/', methods=['GET'])
def obtener_bodegas():
    """Obtener todas las bodegas"""
    try:
        consulta = ObtenerBodegas()
        bodegas = ejecutar_consulta(consulta)
        return Response(json.dumps(bodegas), status=200, mimetype='application/json')
    except Exception as e:
        return Response(json.dumps({'error': str(e)}), status=500, mimetype='application/json')

@bp.route('/inicializar', methods=['POST'])
def inicializar_bodegas():
    """Inicializar bodegas por defecto"""
    try:
        comando = InicializarBodegas()
        resultado = ejecutar_comando(comando)
        return Response(json.dumps(resultado), status=200, mimetype='application/json')
    except Exception as e:
        return Response(json.dumps({'error': str(e)}), status=500, mimetype='application/json')

@bp.route('/<bodega_id>/productos', methods=['GET'])
def obtener_productos_por_bodega(bodega_id):
    """Obtener productos de una bodega específica"""
    try:
        consulta = ObtenerProductosPorBodega(bodega_id=bodega_id)
        productos = ejecutar_consulta(consulta)
        return Response(json.dumps(productos), status=200, mimetype='application/json')
    except Exception as e:
        return Response(json.dumps({'error': str(e)}), status=500, mimetype='application/json')

@bp.route('/producto/<producto_id>/ubicaciones', methods=['GET'])
def obtener_ubicaciones_producto(producto_id):
    """Obtener ubicaciones de un producto en todas las bodegas"""
    try:
        consulta = ObtenerUbicacionesProducto(producto_id=producto_id)
        ubicaciones = ejecutar_consulta(consulta)
        return Response(json.dumps(ubicaciones), status=200, mimetype='application/json')
    except Exception as e:
        return Response(json.dumps({'error': str(e)}), status=500, mimetype='application/json')
