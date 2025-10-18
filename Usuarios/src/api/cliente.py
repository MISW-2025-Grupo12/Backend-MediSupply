import seedwork.presentacion.api as api
import json
from flask import request, Response, Blueprint
from aplicacion.comandos.crear_cliente import CrearCliente
from aplicacion.consultas.obtener_clientes import ObtenerClientes
from aplicacion.consultas.obtener_cliente_por_id import ObtenerClientePorId
from seedwork.aplicacion.comandos import ejecutar_comando
from seedwork.aplicacion.consultas import ejecutar_consulta
from aplicacion.mapeadores import MapeadorClienteDTOJson

import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

bp = api.crear_blueprint('cliente', '/usuarios/api/clientes')

# Endpoint para crear cliente
@bp.route('/', methods=['POST'])
def crear_cliente():
    try:
        # Obtener datos del request
        cliente_dict = request.json
        
        # Validación básica de HTTP
        if not cliente_dict:
            return Response(
                json.dumps({'error': 'Se requiere un JSON válido'}), 
                status=400, 
                mimetype='application/json'
            )
        
        # Crear comando
        comando = CrearCliente(
            nombre=cliente_dict.get('nombre', ''),
            email=cliente_dict.get('email', ''),
            telefono=cliente_dict.get('telefono', ''),
            direccion=cliente_dict.get('direccion', '')
        )
        
        # Ejecutar comando
        resultado = ejecutar_comando(comando)
        
        # Convertir DTO a JSON
        mapeador = MapeadorClienteDTOJson()
        cliente_json = mapeador.dto_a_externo(resultado)
        
        return Response(
            json.dumps(cliente_json), 
            status=201, 
            mimetype='application/json'
        )
        
    except Exception as e:
        logger.error(f"Error creando cliente: {e}")
        return Response(
            json.dumps({'error': f'Error interno del servidor: {str(e)}'}), 
            status=500, 
            mimetype='application/json'
        )

# Endpoint para obtener todos los clientes
@bp.route('/', methods=['GET'])
def obtener_clientes():
    try:
        # Crear consulta
        consulta = ObtenerClientes()
        
        # Ejecutar consulta
        clientes = ejecutar_consulta(consulta)
        
        # Convertir DTOs a JSON
        mapeador = MapeadorClienteDTOJson()
        clientes_json = mapeador.dtos_a_externo(clientes)
        
        return Response(
            json.dumps(clientes_json), 
            status=200, 
            mimetype='application/json'
        )
        
    except Exception as e:
        logger.error(f"Error obteniendo clientes: {e}")
        return Response(
            json.dumps({'error': f'Error interno del servidor: {str(e)}'}), 
            status=500, 
            mimetype='application/json'
        )

# Endpoint para obtener cliente por ID
@bp.route('/<cliente_id>', methods=['GET'])
def obtener_cliente_por_id(cliente_id):
    try:
        # Crear consulta
        consulta = ObtenerClientePorId(cliente_id=cliente_id)
        
        # Ejecutar consulta
        cliente = ejecutar_consulta(consulta)
        
        if not cliente:
            return Response(
                json.dumps({'error': 'Cliente no encontrado'}), 
                status=404, 
                mimetype='application/json'
            )
        
        # Convertir DTO a JSON
        mapeador = MapeadorClienteDTOJson()
        cliente_json = mapeador.dto_a_externo(cliente)
        
        return Response(
            json.dumps(cliente_json), 
            status=200, 
            mimetype='application/json'
        )
        
    except Exception as e:
        logger.error(f"Error obteniendo cliente por ID: {e}")
        return Response(
            json.dumps({'error': f'Error interno del servidor: {str(e)}'}), 
            status=500, 
            mimetype='application/json'
        )
