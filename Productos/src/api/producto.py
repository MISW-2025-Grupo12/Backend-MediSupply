import seedwork.presentacion.api as api
import json
from datetime import datetime
from flask import request, Response, Blueprint
from aplicacion.comandos.crear_producto import CrearProducto
from aplicacion.comandos.crear_producto_con_inventario import CrearProductoConInventario
from aplicacion.consultas.obtener_productos import ObtenerProductos
from aplicacion.consultas.obtener_producto_por_id import ObtenerProductoPorId
from seedwork.aplicacion.comandos import ejecutar_comando
from seedwork.aplicacion.consultas import ejecutar_consulta
from aplicacion.mapeadores import MapeadorProductoDTOJson, MapeadorProductoAgregacionDTOJson

import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

bp = api.crear_blueprint('producto', '/productos/api/productos')

# Endpoint para crear producto
@bp.route('/', methods=['POST'])
def crear_producto():
    try:
        # Obtener datos del request
        producto_dict = request.json
        
        # Validación básica de HTTP - solo verificar que el JSON existe
        if not producto_dict:
            return Response(
                json.dumps({'error': 'Se requiere un JSON válido'}), 
                status=400, 
                mimetype='application/json'
            )
        
        # Crear comando - las validaciones se harán en el dominio
        comando = CrearProducto(
            nombre=producto_dict.get('nombre', ''),
            descripcion=producto_dict.get('descripcion', ''),
            precio=float(producto_dict.get('precio', 0)),
            categoria=producto_dict.get('categoria', ''),
            categoria_id=producto_dict.get('categoria_id', ''),
            proveedor_id=producto_dict.get('proveedor_id', '')
        )
        
        # Ejecutar comando - las reglas de negocio se validan aquí
        resultado = ejecutar_comando(comando)
        
        # Convertir agregación a JSON
        mapeador = MapeadorProductoAgregacionDTOJson()
        producto_json = mapeador.agregacion_a_externo(resultado)
        
        return Response(
            json.dumps(producto_json), 
            status=201, 
            mimetype='application/json'
        )
        
    except ValueError as e:
        # Las reglas de negocio lanzan ValueError
        return Response(
            json.dumps({'error': str(e)}), 
            status=400, 
            mimetype='application/json'
        )
    except Exception as e:
        logger.error(f"Error creando producto: {e}")
        return Response(
            json.dumps({'error': f'Error interno del servidor: {str(e)}'}), 
            status=500, 
            mimetype='application/json'
        )

# Endpoint para crear producto con inventario
@bp.route('/con-inventario', methods=['POST'])
def crear_producto_con_inventario():
    try:
        # Obtener datos del request
        producto_dict = request.json
        
        # Validación básica de HTTP
        if not producto_dict:
            return Response(
                json.dumps({'error': 'Se requiere un JSON válido'}), 
                status=400, 
                mimetype='application/json'
            )
        
        # Crear comando con inventario
        comando = CrearProductoConInventario(
            nombre=producto_dict.get('nombre', ''),
            descripcion=producto_dict.get('descripcion', ''),
            precio=float(producto_dict.get('precio', 0)),
            stock=int(producto_dict.get('stock', 0)),
            fecha_vencimiento=producto_dict.get('fecha_vencimiento', ''),
            categoria=producto_dict.get('categoria', ''),
            categoria_id=producto_dict.get('categoria_id', ''),
            proveedor_id=producto_dict.get('proveedor_id', '')
        )
        
        # Ejecutar comando
        resultado = ejecutar_comando(comando)
        
        # Convertir agregación a JSON
        mapeador = MapeadorProductoAgregacionDTOJson()
        producto_json = mapeador.agregacion_a_externo(resultado)
        
        return Response(
            json.dumps(producto_json), 
            status=201, 
            mimetype='application/json'
        )
        
    except ValueError as e:
        # Las reglas de negocio lanzan ValueError
        return Response(
            json.dumps({'error': str(e)}), 
            status=400, 
            mimetype='application/json'
        )
    except Exception as e:
        logger.error(f"Error creando producto con inventario: {e}")
        return Response(
            json.dumps({'error': f'Error interno del servidor: {str(e)}'}), 
            status=500, 
            mimetype='application/json'
        )

# Endpoint para obtener todos los productos con agregación completa
@bp.route('/', methods=['GET'])
def obtener_productos():
    try:
        # Crear consulta
        consulta = ObtenerProductos()
        
        # Ejecutar consulta (retorna agregaciones completas)
        productos_agregacion = ejecutar_consulta(consulta)
        
        # Convertir agregaciones a JSON
        mapeador = MapeadorProductoAgregacionDTOJson()
        productos_json = mapeador.agregaciones_a_externo(productos_agregacion)
        
        return Response(
            json.dumps(productos_json), 
            status=200, 
            mimetype='application/json'
        )
        
    except Exception as e:
        logger.error(f"Error obteniendo productos con agregación: {e}")
        return Response(
            json.dumps({'error': f'Error interno del servidor: {str(e)}'}), 
            status=500, 
            mimetype='application/json'
        )

# Endpoint para obtener un producto por ID
@bp.route('/<producto_id>', methods=['GET'])
def obtener_producto_por_id(producto_id):
    try:
        # Crear consulta
        consulta = ObtenerProductoPorId(producto_id=producto_id)
        
        # Ejecutar consulta
        producto = ejecutar_consulta(consulta)
        
        if not producto:
            return Response(
                json.dumps({'error': 'Producto no encontrado'}), 
                status=404, 
                mimetype='application/json'
            )
        
        return Response(
            json.dumps(producto), 
            status=200, 
            mimetype='application/json'
        )
        
    except Exception as e:
        logger.error(f"Error obteniendo producto por ID: {e}")
        return Response(
            json.dumps({'error': f'Error interno del servidor: {str(e)}'}), 
            status=500, 
            mimetype='application/json'
        )

