import seedwork.presentacion.api as api
import json
from flask import request, Response, Blueprint
from aplicacion.consultas.obtener_informe_ventas import ObtenerInformeVentas
from aplicacion.consultas.obtener_informe_ventas_por_vendedor import ObtenerInformeVentasPorVendedor
from seedwork.aplicacion.consultas import ejecutar_consulta
from seedwork.presentacion.paginacion import paginar_resultados, extraer_parametros_paginacion
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

bp = api.crear_blueprint('informes', '/ventas/api/informes')

@bp.route('/ventas', methods=['GET'])
def obtener_informe_ventas():
    """Obtiene el informe consolidado de ventas (solo pedidos ENTREGADOS)."""

    try:
        vendedor_id = request.args.get('vendedor_id')
        fecha_inicio = request.args.get("fecha_inicio")  # formato ISO, ejemplo: 2025-01-01T00:00:00
        fecha_fin = request.args.get("fecha_fin")        # formato ISO, ejemplo: 2025-03-31T23:59:59

        # Ejecutar consulta directamente con los valores ISO recibidos
        consulta = ObtenerInformeVentas(
            vendedor_id=vendedor_id,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin
        )

        informe_resultado = ejecutar_consulta(consulta)

        if not informe_resultado:
            return Response(
                json.dumps({'mensaje': 'No se encontraron ventas registradas'}),
                status=200,
                mimetype='application/json'
            )

        return Response(
            json.dumps(informe_resultado, default=str),
            status=200,
            mimetype='application/json'
        )

    except Exception as e:
        logger.error(f"Error obteniendo informe de ventas: {e}")
        return Response(
            json.dumps({'error': f'Error interno del servidor: {str(e)}'}),
            status=500,
            mimetype='application/json'
        )

@bp.route('/vendedores', methods=['GET'])
def obtener_informe_ventas_por_vendedor():
    try:
        fecha_inicio = request.args.get("fecha_inicio")
        fecha_fin = request.args.get("fecha_fin")
        
        page, page_size = extraer_parametros_paginacion(request.args)

        consulta = ObtenerInformeVentasPorVendedor(
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin
        )

        informe_resultado = ejecutar_consulta(consulta)

        if not informe_resultado:
            resultado_paginado = paginar_resultados([], page=page, page_size=page_size)
            return Response(
                json.dumps(resultado_paginado),
                status=200,
                mimetype='application/json'
            )

        resultado_paginado = paginar_resultados(informe_resultado, page=page, page_size=page_size)

        return Response(
            json.dumps(resultado_paginado, default=str),
            status=200,
            mimetype='application/json'
        )

    except Exception as e:
        logger.error(f"Error obteniendo informe de ventas por vendedor: {e}")
        return Response(
            json.dumps({'error': f'Error interno del servidor: {str(e)}'}),
            status=500,
            mimetype='application/json'
        )
