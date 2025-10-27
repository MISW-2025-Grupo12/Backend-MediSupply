import seedwork.presentacion.api as api
import json
from flask import request, Response, Blueprint
from aplicacion.comandos.crear_pedido import CrearPedido
from aplicacion.comandos.agregar_item_pedido import AgregarItemPedido
from aplicacion.comandos.actualizar_item_pedido import ActualizarItemPedido
from aplicacion.comandos.quitar_item_pedido import QuitarItemPedido
from aplicacion.comandos.confirmar_pedido import ConfirmarPedido
from aplicacion.comandos.cambiar_estado_pedido import CambiarEstadoPedido
from aplicacion.comandos.crear_pedido_completo import CrearPedidoCompleto, ItemPedidoCompleto
from aplicacion.consultas.obtener_pedido import ObtenerPedido
from aplicacion.consultas.obtener_pedidos import ObtenerPedidos
from aplicacion.servicios.validador_pedidos import ValidadorPedidos
from seedwork.aplicacion.comandos import ejecutar_comando
from seedwork.aplicacion.consultas import ejecutar_consulta
from infraestructura.servicio_logistica import ServicioLogistica

import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

bp = api.crear_blueprint('pedidos', '/ventas/api/pedidos')

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
        
        # Usar validador de reglas de negocio
        es_valido, error = ValidadorPedidos.validar_datos_basicos_pedido(vendedor_id, cliente_id)
        if not es_valido:
            return Response(
                json.dumps({'error': error}), 
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
        
        
        from aplicacion.servicios.validador_pedidos import ValidadorItemsPedido
        es_valido, error = ValidadorItemsPedido.validar_item_individual({
            'producto_id': producto_id,
            'cantidad': cantidad
        }, 0)
        
        if not es_valido:
            return Response(
                json.dumps({'error': error}), 
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
        
        # Usar validador de reglas de negocio
        from aplicacion.servicios.validador_pedidos import ValidadorItemsPedido
        es_valido, error = ValidadorItemsPedido.validar_item_individual({
            'producto_id': 'dummy',  # No validamos producto_id en actualización
            'cantidad': cantidad
        }, 0)
        
        if not es_valido:
            return Response(
                json.dumps({'error': error}), 
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

@bp.route('/completo', methods=['POST'])
def crear_pedido_completo():
    """Crear un pedido completo con items y confirmarlo en una sola operación"""
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
        items_data = data.get('items', [])
        
        # Usar validador de reglas de negocio
        es_valido, error, items_validados = ValidadorPedidos.validar_pedido_completo(
            vendedor_id, cliente_id, items_data
        )
        
        if not es_valido:
            return Response(
                json.dumps({'error': error}), 
                status=400, 
                mimetype='application/json'
            )
        
        # Convertir items validados a objetos de dominio
        items = []
        for item_data in items_validados:
            items.append(ItemPedidoCompleto(
                producto_id=item_data['producto_id'],
                cantidad=item_data['cantidad']
            ))
        
        comando = CrearPedidoCompleto(
            vendedor_id=vendedor_id,
            cliente_id=cliente_id,
            items=items
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
        logger.error(f"Error creando pedido completo: {e}")
        return Response(
            json.dumps({'error': f'Error interno del servidor: {str(e)}'}), 
            status=500, 
            mimetype='application/json'
        )

@bp.route('/<pedido_id>/estado', methods=['PUT'])
def cambiar_estado_pedido(pedido_id):
    """Cambiar el estado de un pedido (en_transito, entregado)"""
    try:
        data = request.json
        
        if not data:
            return Response(
                json.dumps({'error': 'Se requiere un JSON válido'}), 
                status=400, 
                mimetype='application/json'
            )
        
        nuevo_estado = data.get('estado', '').strip()
        
        if not nuevo_estado:
            return Response(
                json.dumps({'error': 'El campo "estado" es obligatorio'}), 
                status=400, 
                mimetype='application/json'
            )
        
        # Obtener información del usuario desde el token JWT
        usuario_id = request.headers.get('X-User-Id', '')
        tipo_usuario = request.headers.get('X-User-Role', '')
        
        # Debug: Log de headers
        logger.info(f"Headers recibidos: {dict(request.headers)}")
        logger.info(f"X-User-Id: '{usuario_id}', X-User-Role: '{tipo_usuario}'")
        
        if not usuario_id or not tipo_usuario:
            logger.error(f"Headers faltantes - X-User-Id: '{usuario_id}', X-User-Role: '{tipo_usuario}'")
            return Response(
                json.dumps({'error': 'Información de usuario no disponible'}), 
                status=401, 
                mimetype='application/json'
            )
        
        comando = CambiarEstadoPedido(
            pedido_id=pedido_id,
            nuevo_estado=nuevo_estado,
            usuario_id=usuario_id,
            tipo_usuario=tipo_usuario
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
        logger.error(f"Error cambiando estado del pedido: {e}")
        return Response(
            json.dumps({'error': f'Error interno del servidor: {str(e)}'}), 
            status=500, 
            mimetype='application/json'
        )
