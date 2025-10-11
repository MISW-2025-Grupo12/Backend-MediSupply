import seedwork.presentacion.api as api
import json
from flask import request, Response, Blueprint
from aplicacion.comandos.crear_pedido import CrearPedido
from aplicacion.comandos.agregar_item_pedido import AgregarItemPedido
from aplicacion.comandos.actualizar_item_pedido import ActualizarItemPedido
from aplicacion.comandos.quitar_item_pedido import QuitarItemPedido
from aplicacion.comandos.confirmar_pedido import ConfirmarPedido
from aplicacion.consultas.obtener_pedido import ObtenerPedido
from aplicacion.consultas.obtener_pedidos import ObtenerPedidos
from seedwork.aplicacion.comandos import ejecutar_comando
from seedwork.aplicacion.consultas import ejecutar_consulta
from infraestructura.servicio_logistica import ServicioLogistica

import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

bp = api.crear_blueprint('pedidos', '/api/pedidos')

@bp.route('/', methods=['POST'])
def crear_pedido():
    """Crear un nuevo pedido en estado borrador"""
    try:
        data = request.json
        
        if not data:
            return Response(
                json.dumps({'error': 'Se requiere un JSON válido'}), 
                status=400, 
                mimetype='application/json'
            )
        
        vendedor_id = data.get('vendedor_id', '').strip()
        cliente_id = data.get('cliente_id', '').strip()
        
        if not vendedor_id or not cliente_id:
            return Response(
                json.dumps({'error': 'vendedor_id y cliente_id son obligatorios'}), 
                status=400, 
                mimetype='application/json'
            )
        
        comando = CrearPedido(
            vendedor_id=vendedor_id,
            cliente_id=cliente_id
        )
        
        resultado = ejecutar_comando(comando)
        
        if resultado.get('success'):
            return Response(
                json.dumps(resultado), 
                status=201, 
                mimetype='application/json'
            )
        else:
            return Response(
                json.dumps(resultado), 
                status=400, 
                mimetype='application/json'
            )
        
    except Exception as e:
        logger.error(f"Error creando pedido: {e}")
        return Response(
            json.dumps({'error': f'Error interno del servidor: {str(e)}'}), 
            status=500, 
            mimetype='application/json'
        )

@bp.route('/<pedido_id>', methods=['GET'])
def obtener_pedido(pedido_id):
    """Obtener detalle de un pedido con sus items"""
    try:
        consulta = ObtenerPedido(pedido_id=pedido_id)
        pedido = ejecutar_consulta(consulta)
        
        if not pedido:
            return Response(
                json.dumps({'error': 'Pedido no encontrado'}), 
                status=404, 
                mimetype='application/json'
            )
        
        return Response(
            json.dumps(pedido), 
            status=200, 
            mimetype='application/json'
        )
        
    except Exception as e:
        logger.error(f"Error obteniendo pedido: {e}")
        return Response(
            json.dumps({'error': f'Error interno del servidor: {str(e)}'}), 
            status=500, 
            mimetype='application/json'
        )

@bp.route('/', methods=['GET'])
def obtener_pedidos():
    """Obtener todos los pedidos con filtros opcionales"""
    try:
        # Obtener parámetros de filtro de la query string
        vendedor_id = request.args.get('vendedor_id', '').strip()
        estado = request.args.get('estado', '').strip()
        
        # Crear consulta con filtros opcionales
        consulta = ObtenerPedidos(
            vendedor_id=vendedor_id if vendedor_id else None,
            estado=estado if estado else None
        )
        
        pedidos = ejecutar_consulta(consulta)
        
        return Response(
            json.dumps(pedidos), 
            status=200, 
            mimetype='application/json'
        )
        
    except Exception as e:
        logger.error(f"Error obteniendo pedidos: {e}")
        return Response(
            json.dumps({'error': f'Error interno del servidor: {str(e)}'}), 
            status=500, 
            mimetype='application/json'
        )

@bp.route('/<pedido_id>/items', methods=['POST'])
def agregar_item_pedido(pedido_id):
    """Agregar un producto al pedido"""
    try:
        data = request.json
        
        if not data:
            return Response(
                json.dumps({'error': 'Se requiere un JSON válido'}), 
                status=400, 
                mimetype='application/json'
            )
        
        producto_id = data.get('producto_id', '').strip()
        cantidad = data.get('cantidad', 0)
        
        if not producto_id or cantidad <= 0:
            return Response(
                json.dumps({'error': 'producto_id y cantidad > 0 son obligatorios'}), 
                status=400, 
                mimetype='application/json'
            )
        
        comando = AgregarItemPedido(
            pedido_id=pedido_id,
            producto_id=producto_id,
            cantidad=cantidad
        )
        
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
        logger.error(f"Error agregando item al pedido: {e}")
        return Response(
            json.dumps({'error': f'Error interno del servidor: {str(e)}'}), 
            status=500, 
            mimetype='application/json'
        )

@bp.route('/<pedido_id>/items/<item_id>', methods=['PUT'])
def actualizar_item_pedido(pedido_id, item_id):
    """Actualizar cantidad de un item del pedido"""
    try:
        data = request.json
        
        if not data:
            return Response(
                json.dumps({'error': 'Se requiere un JSON válido'}), 
                status=400, 
                mimetype='application/json'
            )
        
        cantidad = data.get('cantidad', 0)
        
        if cantidad < 0:
            return Response(
                json.dumps({'error': 'La cantidad no puede ser negativa'}), 
                status=400, 
                mimetype='application/json'
            )
        
        comando = ActualizarItemPedido(
            pedido_id=pedido_id,
            item_id=item_id,
            cantidad=cantidad
        )
        
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
        logger.error(f"Error actualizando item del pedido: {e}")
        return Response(
            json.dumps({'error': f'Error interno del servidor: {str(e)}'}), 
            status=500, 
            mimetype='application/json'
        )

@bp.route('/<pedido_id>/items/<item_id>', methods=['DELETE'])
def quitar_item_pedido(pedido_id, item_id):
    """Quitar un item del pedido"""
    try:
        comando = QuitarItemPedido(
            pedido_id=pedido_id,
            item_id=item_id
        )
        
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
        logger.error(f"Error quitando item del pedido: {e}")
        return Response(
            json.dumps({'error': f'Error interno del servidor: {str(e)}'}), 
            status=500, 
            mimetype='application/json'
        )

@bp.route('/<pedido_id>/confirmar', methods=['POST'])
def confirmar_pedido(pedido_id):
    """Confirmar un pedido y reservar inventario"""
    try:
        comando = ConfirmarPedido(pedido_id=pedido_id)
        
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
        logger.error(f"Error confirmando pedido: {e}")
        return Response(
            json.dumps({'error': f'Error interno del servidor: {str(e)}'}), 
            status=500, 
            mimetype='application/json'
        )

@bp.route('/productos/buscar', methods=['GET'])
def buscar_productos():
    """Buscar productos con inventario disponible (proxy a Logística)"""
    try:
        termino = request.args.get('q', '').strip()
        
        if not termino:
            return Response(
                json.dumps([]), 
                status=200, 
                mimetype='application/json'
            )
        
        if len(termino) > 100:
            return Response(
                json.dumps({'error': 'El término de búsqueda no puede exceder 100 caracteres'}), 
                status=400, 
                mimetype='application/json'
            )
        
        servicio_logistica = ServicioLogistica()
        productos = servicio_logistica.buscar_productos(termino)
        
        return Response(
            json.dumps(productos), 
            status=200, 
            mimetype='application/json'
        )
        
    except Exception as e:
        logger.error(f"Error buscando productos: {e}")
        return Response(
            json.dumps({'error': f'Error interno del servidor: {str(e)}'}), 
            status=500, 
            mimetype='application/json'
        )
