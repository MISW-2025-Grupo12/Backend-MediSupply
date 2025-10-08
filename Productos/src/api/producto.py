import seedwork.presentacion.api as api
import json
from datetime import datetime
from flask import request, Response, Blueprint
from aplicacion.comandos.crear_producto import CrearProducto
from aplicacion.consultas.obtener_productos import ObtenerProductos
from seedwork.aplicacion.comandos import ejecutar_comando
from seedwork.aplicacion.consultas import ejecutar_consulta
from aplicacion.mapeadores import MapeadorProductoDTOJson, MapeadorProductoAgregacionDTOJson

import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

bp = api.crear_blueprint('producto', '/api/productos')

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
        
        # Convertir fecha_vencimiento de string a datetime
        fecha_vencimiento = None
        if 'fecha_vencimiento' in producto_dict:
            try:
                # Parsear fecha ISO y remover zona horaria para evitar problemas de comparación
                fecha_vencimiento = datetime.fromisoformat(producto_dict['fecha_vencimiento'].replace('Z', '+00:00'))
                # Remover zona horaria para que sea compatible con datetime.now()
                if fecha_vencimiento.tzinfo is not None:
                    fecha_vencimiento = fecha_vencimiento.replace(tzinfo=None)
            except ValueError:
                # Intentar formato dd/mm/aaaa
                try:
                    fecha_vencimiento = datetime.strptime(producto_dict['fecha_vencimiento'], '%d/%m/%Y')
                except ValueError:
                    return Response(
                        json.dumps({'error': 'Formato de fecha inválido. Use ISO format o dd/mm/aaaa'}), 
                        status=400, 
                        mimetype='application/json'
                    )
        
            # Crear comando - las validaciones se harán en el dominio
            comando = CrearProducto(
                nombre=producto_dict.get('nombre', ''),
                descripcion=producto_dict.get('descripcion', ''),
                precio=float(producto_dict.get('precio', 0)),
                stock=int(producto_dict.get('stock', 0)),
                fecha_vencimiento=fecha_vencimiento or datetime.now(),
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

