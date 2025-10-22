import seedwork.presentacion.api as api
import json
from flask import request, Response, Blueprint
from aplicacion.comandos.crear_vendedor import CrearVendedor
from aplicacion.consultas.obtener_vendedores import ObtenerVendedores
from aplicacion.consultas.obtener_vendedor_por_id import ObtenerVendedorPorId
from seedwork.aplicacion.comandos import ejecutar_comando
from seedwork.aplicacion.consultas import ejecutar_consulta
from aplicacion.mapeadores import MapeadorVendedorDTOJson

import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

bp = api.crear_blueprint('vendedor', '/usuarios/api/vendedores')

# Endpoint para crear vendedor
@bp.route('/', methods=['POST'])
def crear_vendedor():
    try:
        # Obtener datos del request
        vendedor_dict = request.json
        
        # Validación básica de HTTP
        if not vendedor_dict:
            return Response(
                json.dumps({'error': 'Se requiere un JSON válido'}), 
                status=400, 
                mimetype='application/json'
            )
        
        # Crear comando
        comando = CrearVendedor(
            nombre=vendedor_dict.get('nombre', ''),
            email=vendedor_dict.get('email', ''),
            identificacion=vendedor_dict.get('identificacion', ''),
            telefono=vendedor_dict.get('telefono', ''),
            direccion=vendedor_dict.get('direccion', '')
        )
        
        # Ejecutar comando
        resultado = ejecutar_comando(comando)
        
        # Convertir DTO a JSON
        mapeador = MapeadorVendedorDTOJson()
        vendedor_json = mapeador.dto_a_externo(resultado)
        
        return Response(
            json.dumps(vendedor_json), 
            status=201, 
            mimetype='application/json'
        )
        
    except Exception as e:
        logger.error(f"Error creando vendedor: {e}")
        return Response(
            json.dumps({'error': f'Error interno del servidor: {str(e)}'}), 
            status=500, 
            mimetype='application/json'
        )

# Endpoint para obtener todos los vendedores
@bp.route('/', methods=['GET'])
def obtener_vendedores():
    try:
        # Crear consulta
        consulta = ObtenerVendedores()
        
        # Ejecutar consulta
        vendedores = ejecutar_consulta(consulta)
        
        # Convertir DTOs a JSON
        mapeador = MapeadorVendedorDTOJson()
        vendedores_json = mapeador.dtos_a_externo(vendedores)
        
        return Response(
            json.dumps(vendedores_json), 
            status=200, 
            mimetype='application/json'
        )
        
    except Exception as e:
        logger.error(f"Error obteniendo vendedores: {e}")
        return Response(
            json.dumps({'error': f'Error interno del servidor: {str(e)}'}), 
            status=500, 
            mimetype='application/json'
        )

# Endpoint para obtener vendedor por ID
@bp.route('/<vendedor_id>', methods=['GET'])
def obtener_vendedor_por_id(vendedor_id):
    try:
        # Crear consulta
        consulta = ObtenerVendedorPorId(vendedor_id=vendedor_id)
        
        # Ejecutar consulta
        vendedor = ejecutar_consulta(consulta)
        
        if not vendedor:
            return Response(
                json.dumps({'error': 'Vendedor no encontrado'}), 
                status=404, 
                mimetype='application/json'
            )
        
        # Convertir DTO a JSON
        mapeador = MapeadorVendedorDTOJson()
        vendedor_json = mapeador.dto_a_externo(vendedor)
        
        return Response(
            json.dumps(vendedor_json), 
            status=200, 
            mimetype='application/json'
        )
        
    except Exception as e:
        logger.error(f"Error obteniendo vendedor por ID: {e}")
        return Response(
            json.dumps({'error': f'Error interno del servidor: {str(e)}'}), 
            status=500, 
            mimetype='application/json'
        )
