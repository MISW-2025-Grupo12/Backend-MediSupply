import seedwork.presentacion.api as api
import json
from flask import request, Response, Blueprint
from aplicacion.comandos.crear_categoria import CrearCategoria
from aplicacion.consultas.obtener_categorias import ObtenerCategorias
from aplicacion.consultas.obtener_categoria_por_id import ObtenerCategoriaPorId
from seedwork.aplicacion.comandos import ejecutar_comando
from seedwork.aplicacion.consultas import ejecutar_consulta
from aplicacion.mapeadores import MapeadorCategoriaDTOJson

import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Blueprint para categorías (POST y GET) - Jerárquico bajo productos
bp = api.crear_blueprint('categoria', '/api/productos/categorias')

# Endpoint para crear categoría
@bp.route('/', methods=['POST'])
def crear_categoria():
    try:
        # Obtener datos del request
        categoria_dict = request.json
        
        # Validación básica de HTTP - solo verificar que el JSON existe
        if not categoria_dict:
            return Response(
                json.dumps({'error': 'Se requiere un JSON válido'}), 
                status=400, 
                mimetype='application/json'
            )
        
        # Crear comando
        comando = CrearCategoria(
            nombre=categoria_dict.get('nombre', ''),
            descripcion=categoria_dict.get('descripcion', '')
        )
        
        # Ejecutar comando
        resultado = ejecutar_comando(comando)
        
        # Convertir resultado a JSON
        mapeador = MapeadorCategoriaDTOJson()
        categoria_json = mapeador.dto_a_externo(resultado)
        
        return Response(
            json.dumps(categoria_json), 
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
        logger.error(f"Error creando categoría: {e}")
        return Response(
            json.dumps({'error': f'Error interno del servidor: {str(e)}'}), 
            status=500, 
            mimetype='application/json'
        )

# Endpoint para obtener todas las categorías
@bp.route('/', methods=['GET'])
def obtener_categorias():
    try:
        # Crear consulta
        consulta = ObtenerCategorias()
        
        # Ejecutar consulta
        categorias = ejecutar_consulta(consulta)
        
        # Convertir categorías a JSON
        mapeador = MapeadorCategoriaDTOJson()
        categorias_json = []
        for categoria in categorias:
            categorias_json.append(mapeador.dto_a_externo(categoria))
        
        return Response(
            json.dumps(categorias_json), 
            status=200, 
            mimetype='application/json'
        )
        
    except Exception as e:
        logger.error(f"Error obteniendo categorías: {e}")
        return Response(
            json.dumps({'error': f'Error interno del servidor: {str(e)}'}), 
            status=500, 
            mimetype='application/json'
        )

# Endpoint para obtener categoría por ID
@bp.route('/<categoria_id>', methods=['GET'])
def obtener_categoria_por_id(categoria_id):
    try:
        # Crear consulta
        consulta = ObtenerCategoriaPorId(categoria_id=categoria_id)
        
        # Ejecutar consulta
        categoria = ejecutar_consulta(consulta)
        
        if not categoria:
            return Response(
                json.dumps({'error': 'Categoría no encontrada'}), 
                status=404, 
                mimetype='application/json'
            )
        
        # Convertir categoría a JSON
        mapeador = MapeadorCategoriaDTOJson()
        categoria_json = mapeador.dto_a_externo(categoria)
        
        return Response(
            json.dumps(categoria_json), 
            status=200, 
            mimetype='application/json'
        )
        
    except Exception as e:
        logger.error(f"Error obteniendo categoría {categoria_id}: {e}")
        return Response(
            json.dumps({'error': f'Error interno del servidor: {str(e)}'}), 
            status=500, 
            mimetype='application/json'
        )
