import seedwork.presentacion.api as api
import json
from flask import request, Response
from aplicacion.comandos.inicializar_bodegas import InicializarBodegas
from aplicacion.consultas.obtener_bodegas import ObtenerBodegas
from aplicacion.consultas.obtener_productos_por_bodega import ObtenerProductosPorBodega
from aplicacion.consultas.obtener_ubicaciones_producto import ObtenerUbicacionesProducto
from aplicacion.consultas.obtener_todos_los_productos import ObtenerTodosLosProductos
from seedwork.aplicacion.comandos import ejecutar_comando
from seedwork.aplicacion.consultas import ejecutar_consulta
from seedwork.presentacion.paginacion import paginar_resultados, extraer_parametros_paginacion

bp = api.crear_blueprint('bodegas', '/logistica/api/bodegas')

@bp.route('/', methods=['GET'])
def obtener_bodegas():
    """Obtener todas las bodegas"""
    try:
        # Obtener parámetros de paginación
        page, page_size = extraer_parametros_paginacion(request.args)
        
        consulta = ObtenerBodegas()
        bodegas = ejecutar_consulta(consulta)
        
        # Aplicar paginación
        resultado_paginado = paginar_resultados(bodegas, page=page, page_size=page_size)
        
        return Response(json.dumps(resultado_paginado), status=200, mimetype='application/json')
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
        # Obtener parámetros de paginación
        page, page_size = extraer_parametros_paginacion(request.args)
        
        consulta = ObtenerProductosPorBodega(bodega_id=bodega_id)
        productos = ejecutar_consulta(consulta)
        
        # Aplicar paginación
        resultado_paginado = paginar_resultados(productos, page=page, page_size=page_size)
        
        return Response(json.dumps(resultado_paginado), status=200, mimetype='application/json')
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

@bp.route('/productos', methods=['GET'])
def obtener_todos_los_productos():
    """Obtener todos los productos de todas las bodegas"""
    try:
        # Obtener parámetros de paginación
        page, page_size = extraer_parametros_paginacion(request.args)
        
        consulta = ObtenerTodosLosProductos()
        productos = ejecutar_consulta(consulta)
        
        # Aplicar paginación
        resultado_paginado = paginar_resultados(productos, page=page, page_size=page_size)
        
        return Response(json.dumps(resultado_paginado), status=200, mimetype='application/json')
    except Exception as e:
        return Response(json.dumps({'error': str(e)}), status=500, mimetype='application/json')