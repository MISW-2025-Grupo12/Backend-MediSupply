import seedwork.presentacion.api as api
import json
from flask import request, Response, Blueprint
from aplicacion.comandos.reservar_inventario import ReservarInventario
from aplicacion.comandos.descontar_inventario import DescontarInventario
from aplicacion.consultas.buscar_productos_con_inventario import BuscarProductosConInventario
from seedwork.aplicacion.comandos import ejecutar_comando
from seedwork.aplicacion.consultas import ejecutar_consulta
from infraestructura.repositorios import RepositorioInventarioSQLite
from aplicacion.dto import InventarioDTO

import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

bp = api.crear_blueprint('inventario', '/api/inventario')

@bp.route('/buscar', methods=['GET'])
def buscar_productos_con_inventario():
    """Buscar productos con inventario disponible"""
    try:
        termino = request.args.get('q', '').strip()
        limite = int(request.args.get('limite', 50))
        
        if not termino:
            return Response(
                json.dumps([]), 
                status=200, 
                mimetype='application/json'
            )
        
        consulta = BuscarProductosConInventario(termino=termino, limite=limite)
        productos = ejecutar_consulta(consulta)
        
        return Response(
            json.dumps(productos), 
            status=200, 
            mimetype='application/json'
        )
        
    except Exception as e:
        logger.error(f"Error buscando productos con inventario: {e}")
        return Response(
            json.dumps({'error': f'Error interno del servidor: {str(e)}'}), 
            status=500, 
            mimetype='application/json'
        )

@bp.route('/reservar', methods=['POST'])
def reservar_inventario():
    """Reservar inventario para un pedido"""
    try:
        data = request.json
        
        if not data or 'items' not in data:
            return Response(
                json.dumps({'error': 'Se requiere un JSON con campo "items"'}), 
                status=400, 
                mimetype='application/json'
            )
        
        items = data.get('items', [])
        if not items or not isinstance(items, list):
            return Response(
                json.dumps({'error': 'El campo "items" debe ser una lista no vacía'}), 
                status=400, 
                mimetype='application/json'
            )
        
        # Validar estructura de cada item
        for item in items:
            if not isinstance(item, dict) or 'producto_id' not in item or 'cantidad' not in item:
                return Response(
                    json.dumps({'error': 'Cada item debe tener "producto_id" y "cantidad"'}), 
                    status=400, 
                    mimetype='application/json'
                )
        
        comando = ReservarInventario(items=items)
        resultado = ejecutar_comando(comando)
        
        if resultado.get('success'):
            return Response(
                json.dumps(resultado), 
                status=200, 
                mimetype='application/json'
            )
        else:
            return Response(
                json.dumps(resultado), 
                status=400, 
                mimetype='application/json'
            )
        
    except Exception as e:
        logger.error(f"Error reservando inventario: {e}")
        return Response(
            json.dumps({'error': f'Error interno del servidor: {str(e)}'}), 
            status=500, 
            mimetype='application/json'
        )

@bp.route('/descontar', methods=['POST'])
def descontar_inventario():
    """Descontar inventario reservado (consumido por eventos)"""
    try:
        data = request.json
        
        if not data or 'items' not in data:
            return Response(
                json.dumps({'error': 'Se requiere un JSON con campo "items"'}), 
                status=400, 
                mimetype='application/json'
            )
        
        items = data.get('items', [])
        if not items or not isinstance(items, list):
            return Response(
                json.dumps({'error': 'El campo "items" debe ser una lista no vacía'}), 
                status=400, 
                mimetype='application/json'
            )
        
        # Validar estructura de cada item
        for item in items:
            if not isinstance(item, dict) or 'producto_id' not in item or 'cantidad' not in item:
                return Response(
                    json.dumps({'error': 'Cada item debe tener "producto_id" y "cantidad"'}), 
                    status=400, 
                    mimetype='application/json'
                )
        
        comando = DescontarInventario(items=items)
        resultado = ejecutar_comando(comando)
        
        if resultado.get('success'):
            return Response(
                json.dumps(resultado), 
                status=200, 
                mimetype='application/json'
            )
        else:
            return Response(
                json.dumps(resultado), 
                status=400, 
                mimetype='application/json'
            )
        
    except Exception as e:
        logger.error(f"Error descontando inventario: {e}")
        return Response(
            json.dumps({'error': f'Error interno del servidor: {str(e)}'}), 
            status=500, 
            mimetype='application/json'
        )

@bp.route('/producto/<producto_id>', methods=['GET'])
def obtener_inventario_producto(producto_id):
    """Obtener inventario de un producto específico"""
    try:
        repositorio = RepositorioInventarioSQLite()
        lotes_inventario = repositorio.obtener_por_producto_id(producto_id)
        
        if not lotes_inventario:
            return Response(
                json.dumps({'error': 'Producto no encontrado en inventario'}), 
                status=404, 
                mimetype='application/json'
            )
        
        # Calcular totales
        total_disponible = sum(lote.cantidad_disponible for lote in lotes_inventario)
        total_reservado = sum(lote.cantidad_reservada for lote in lotes_inventario)
        
        response_data = {
            'producto_id': producto_id,
            'total_disponible': total_disponible,
            'total_reservado': total_reservado,
            'lotes': [
                {
                    'fecha_vencimiento': lote.fecha_vencimiento.isoformat(),
                    'cantidad_disponible': lote.cantidad_disponible,
                    'cantidad_reservada': lote.cantidad_reservada
                } for lote in lotes_inventario
            ]
        }
        
        return Response(
            json.dumps(response_data), 
            status=200, 
            mimetype='application/json'
        )
        
    except Exception as e:
        logger.error(f"Error obteniendo inventario del producto {producto_id}: {e}")
        return Response(
            json.dumps({'error': f'Error interno del servidor: {str(e)}'}), 
            status=500, 
            mimetype='application/json'
        )

@bp.route('/', methods=['GET'])
def obtener_todo_inventario():
    """Obtener todo el inventario agrupado por producto"""
    try:
        repositorio = RepositorioInventarioSQLite()
        lotes_inventario = repositorio.obtener_todos()
        
        if not lotes_inventario:
            return Response(
                json.dumps([]), 
                status=200, 
                mimetype='application/json'
            )
        
        # Agrupar por producto_id
        inventario_por_producto = {}
        for lote in lotes_inventario:
            producto_id = lote.producto_id
            
            if producto_id not in inventario_por_producto:
                inventario_por_producto[producto_id] = {
                    'producto_id': producto_id,
                    'total_disponible': 0,
                    'total_reservado': 0,
                    'lotes': []
                }
            
            # Sumar totales
            inventario_por_producto[producto_id]['total_disponible'] += lote.cantidad_disponible
            inventario_por_producto[producto_id]['total_reservado'] += lote.cantidad_reservada
            
            # Agregar lote
            inventario_por_producto[producto_id]['lotes'].append({
                'fecha_vencimiento': lote.fecha_vencimiento.isoformat(),
                'cantidad_disponible': lote.cantidad_disponible,
                'cantidad_reservada': lote.cantidad_reservada
            })
        
        # Convertir a lista
        inventario_completo = list(inventario_por_producto.values())
        
        return Response(
            json.dumps(inventario_completo), 
            status=200, 
            mimetype='application/json'
        )
        
    except Exception as e:
        logger.error(f"Error obteniendo todo el inventario: {e}")
        return Response(
            json.dumps({'error': f'Error interno del servidor: {str(e)}'}), 
            status=500, 
            mimetype='application/json'
        )