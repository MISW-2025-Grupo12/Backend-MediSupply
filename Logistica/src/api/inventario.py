import seedwork.presentacion.api as api
import json
import queue
import threading
import os
from flask import request, Response, Blueprint, stream_with_context, send_from_directory
from aplicacion.comandos.reservar_inventario import ReservarInventario
from aplicacion.comandos.descontar_inventario import DescontarInventario
from aplicacion.consultas.buscar_productos_con_inventario import BuscarProductosConInventario
from seedwork.aplicacion.comandos import ejecutar_comando
from seedwork.aplicacion.consultas import ejecutar_consulta
from infraestructura.repositorios import RepositorioInventarioSQLite
from aplicacion.dto import InventarioDTO
from infraestructura.sse_manager import sse_client_manager

import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

bp = api.crear_blueprint('inventario', '/logistica/api/inventario')

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
    """Obtener inventario de un producto específico con ubicaciones"""
    try:
        repositorio = RepositorioInventarioSQLite()
        lotes_inventario = repositorio.obtener_por_producto_id(producto_id)
        
        if not lotes_inventario:
            return Response(
                json.dumps({'error': 'Producto no encontrado en inventario'}), 
                status=404, 
                mimetype='application/json'
            )
        
        # Agrupar por bodega
        por_bodega = {}
        for lote in lotes_inventario:
            bid = lote.bodega_id or 'sin_asignar'
            if bid not in por_bodega:
                por_bodega[bid] = {
                    'bodega_id': lote.bodega_id,
                    'ubicaciones': [],
                    'total_disponible': 0,
                    'total_reservado': 0
                }
            
            por_bodega[bid]['total_disponible'] += lote.cantidad_disponible
            por_bodega[bid]['total_reservado'] += lote.cantidad_reservada
            por_bodega[bid]['ubicaciones'].append({
                'pasillo': lote.pasillo,
                'estante': lote.estante,
                'ubicacion': f"Bodega #{lote.bodega_id} - Pasillo {lote.pasillo} - Estante {lote.estante}" if lote.bodega_id else None,
                'cantidad_disponible': lote.cantidad_disponible,
                'cantidad_reservada': lote.cantidad_reservada,
                'fecha_vencimiento': lote.fecha_vencimiento.isoformat()
            })
        
        response_data = {
            'producto_id': producto_id,
            'bodegas': list(por_bodega.values())
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

@bp.route('/stream', methods=['GET'])
def stream_inventario():
    """Endpoint SSE para recibir actualizaciones de inventario en tiempo real"""
    def generar_eventos():
        """Generador de eventos SSE"""
        # Crear cola para este cliente
        client_queue = queue.Queue(maxsize=100)
        
        try:
            # Registrar cliente en el manager
            sse_client_manager.agregar_cliente(client_queue)
            logger.info("Cliente SSE conectado")
            
            # Enviar estado inicial del inventario
            repositorio = RepositorioInventarioSQLite()
            lotes_inventario = repositorio.obtener_todos()
            
            # Agrupar por producto_id y calcular total disponible
            inventario_por_producto = {}
            for lote in lotes_inventario:
                producto_id = lote.producto_id
                if producto_id not in inventario_por_producto:
                    inventario_por_producto[producto_id] = {
                        'producto_id': producto_id,
                        'cantidad_disponible': 0
                    }
                inventario_por_producto[producto_id]['cantidad_disponible'] += lote.cantidad_disponible
            
            # Enviar estado inicial
            for producto_data in inventario_por_producto.values():
                evento_initial = f"event: inventory\ndata: {json.dumps(producto_data)}\n\n"
                yield evento_initial
            
            # Enviar heartbeat periódico y escuchar actualizaciones
            import time
            last_heartbeat = time.time()
            heartbeat_interval = 30  # segundos
            
            while True:
                try:
                    # Verificar si hay mensajes en la cola (timeout corto)
                    try:
                        message = client_queue.get(timeout=1)
                        yield message
                    except queue.Empty:
                        pass
                    
                    # Enviar heartbeat periódico
                    current_time = time.time()
                    if current_time - last_heartbeat >= heartbeat_interval:
                        heartbeat = "event: heartbeat\ndata: {}\n\n"
                        yield heartbeat
                        last_heartbeat = current_time
                        
                except GeneratorExit:
                    logger.info("Cliente SSE desconectado (GeneratorExit)")
                    break
                except Exception as e:
                    logger.error(f"Error en generador SSE: {e}")
                    break
                    
        except Exception as e:
            logger.error(f"Error en stream SSE: {e}")
        finally:
            # Remover cliente del manager
            sse_client_manager.remover_cliente(client_queue)
            logger.info("Cliente SSE desconectado")
    
    return Response(
        stream_with_context(generar_eventos()),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no',
            'Connection': 'keep-alive'
        }
    )

@bp.route('/stream/test', methods=['GET'])
def test_sse_page():
    """Página HTML de prueba para el endpoint SSE - sirve archivo estático"""
    # Obtener la ruta del directorio estático
    static_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'static')
    return send_from_directory(static_dir, 'test_sse.html')