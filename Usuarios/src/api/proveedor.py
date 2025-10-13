import seedwork.presentacion.api as api
import json
from flask import request, Response
from aplicacion.comandos.crear_proveedor import CrearProveedor
from aplicacion.consultas.obtener_proveedores import ObtenerProveedores
from aplicacion.consultas.obtener_proveedor_por_id import ObtenerProveedorPorId
from seedwork.aplicacion.comandos import ejecutar_comando
from seedwork.aplicacion.consultas import ejecutar_consulta
from aplicacion.mapeadores import MapeadorProveedorDTOJson
import logging

logger = logging.getLogger(__name__)

bp = api.crear_blueprint('proveedor', '/usuarios/api/proveedores')

@bp.route('/', methods=['POST'])
def crear_proveedor():
    try:
        proveedor_dict = request.json
        if not proveedor_dict:
            return Response(json.dumps({'error': 'Se requiere un JSON válido'}), status=400, mimetype='application/json')
        
        comando = CrearProveedor(
            nombre=proveedor_dict.get('nombre', ''),
            email=proveedor_dict.get('email', ''),
            direccion=proveedor_dict.get('direccion', '')
        )
        
        resultado = ejecutar_comando(comando)
        mapeador = MapeadorProveedorDTOJson()
        proveedor_json = mapeador.dto_a_externo(resultado)
        
        return Response(json.dumps(proveedor_json), status=201, mimetype='application/json')
    except ValueError as e:
        return Response(json.dumps({'error': str(e)}), status=400, mimetype='application/json')
    except Exception as e:
        logger.error(f"Error creando proveedor: {e}")
        return Response(json.dumps({'error': f'Error interno del servidor: {str(e)}'}), status=500, mimetype='application/json')

@bp.route('/', methods=['GET'])
def obtener_proveedores():
    try:
        consulta = ObtenerProveedores()
        proveedores = ejecutar_consulta(consulta)
        
        mapeador = MapeadorProveedorDTOJson()
        proveedores_json = [mapeador.dto_a_externo(p) for p in proveedores]
        
        return Response(json.dumps(proveedores_json), status=200, mimetype='application/json')
    except Exception as e:
        logger.error(f"Error obteniendo proveedores: {e}")
        return Response(json.dumps({'error': f'Error interno del servidor: {str(e)}'}), status=500, mimetype='application/json')

@bp.route('/<proveedor_id>', methods=['GET'])
def obtener_proveedor_por_id(proveedor_id):
    try:
        consulta = ObtenerProveedorPorId(proveedor_id=proveedor_id)
        proveedor = ejecutar_consulta(consulta)
        
        if not proveedor:
            return Response(
                json.dumps({'error': 'Proveedor no encontrado'}), 
                status=404, 
                mimetype='application/json'
            )
        
        mapeador = MapeadorProveedorDTOJson()
        proveedor_json = mapeador.dto_a_externo(proveedor)
        
        return Response(json.dumps(proveedor_json), status=200, mimetype='application/json')
    except Exception as e:
        logger.error(f"Error obteniendo proveedor {proveedor_id}: {e}")
        return Response(json.dumps({'error': f'Error interno del servidor: {str(e)}'}), status=500, mimetype='application/json')
