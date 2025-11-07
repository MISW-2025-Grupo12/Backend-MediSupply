from dataclasses import dataclass
from seedwork.aplicacion.comandos import Comando
from seedwork.aplicacion.comandos import ejecutar_comando as comando
from infraestructura.repositorios import RepositorioPedidoSQLite
from infraestructura.servicio_logistica import ServicioLogistica
from seedwork.dominio.eventos import despachador_eventos
from dominio.eventos import PedidoConfirmado
import logging

logger = logging.getLogger(__name__)

@dataclass
class ConfirmarPedido(Comando):
    pedido_id: str

class ConfirmarPedidoHandler:
    def __init__(self):
        self._repositorio: RepositorioPedidoSQLite = RepositorioPedidoSQLite()
        self._servicio_logistica: ServicioLogistica = ServicioLogistica()
    
    def handle(self, comando: ConfirmarPedido) -> dict:
        """Confirmar un pedido y reservar inventario"""
        try:
            # Validar datos de entrada
            if not comando.pedido_id:
                return {
                    'success': False,
                    'error': 'pedido_id es obligatorio'
                }
            
            # Obtener pedido existente
            pedido = self._repositorio.obtener_por_id(comando.pedido_id)
            if not pedido:
                return {
                    'success': False,
                    'error': 'Pedido no encontrado'
                }
            
            # Verificar que el pedido esté en estado borrador
            if pedido.estado.estado != "borrador":
                return {
                    'success': False,
                    'error': 'Solo se pueden confirmar pedidos en estado borrador'
                }
            
            # Validar que el pedido tenga al menos un item
            if not pedido.items:
                return {
                    'success': False,
                    'error': 'El pedido debe tener al menos un item para ser confirmado'
                }
            
            # Validar que tenga cliente
            if not pedido.cliente_id:
                return {
                    'success': False,
                    'error': 'El pedido debe tener un cliente asignado'
                }
            
            # Calcular total del pedido usando los precios ya obtenidos al agregar items
            total_pedido = 0.0
            for item in pedido.items:
                # Calcular subtotal y sumar al total
                subtotal = item.calcular_subtotal()
                total_pedido += subtotal
            
            # Actualizar total del pedido
            from dominio.objetos_valor import Precio
            pedido.total = Precio(total_pedido)
            
            # Preparar items para reservar inventario
            items_para_reservar = []
            items_info = []  # Para información detallada de los items
            for item in pedido.items:
                items_para_reservar.append({
                    'producto_id': item.producto_id,
                    'cantidad': item.cantidad.valor
                })
                items_info.append({
                    'producto_id': item.producto_id,
                    'nombre': item.nombre_producto,
                    'cantidad': item.cantidad.valor
                })
            
            # Validar inventario antes de intentar reservar
            items_con_problemas = []
            items_validos = []
            
            for item in items_info:
                producto_id = item['producto_id']
                cantidad_solicitada = item['cantidad']
                
                # Consultar inventario del producto
                inventario = self._servicio_logistica.obtener_inventario_producto(producto_id)
                
                if not inventario:
                    # Producto no existe en inventario
                    items_con_problemas.append({
                        'producto_id': producto_id,
                        'nombre': item['nombre'],
                        'cantidad_solicitada': cantidad_solicitada,
                        'cantidad_disponible': 0,
                        'problema': 'no_existe',
                        'mensaje': 'El producto no existe en el inventario'
                    })
                else:
                    # Calcular cantidad total disponible sumando todas las bodegas
                    cantidad_disponible = 0
                    if 'bodegas' in inventario:
                        for bodega in inventario['bodegas']:
                            cantidad_disponible += bodega.get('total_disponible', 0)
                    else:
                        # Fallback para estructura antigua
                        cantidad_disponible = inventario.get('total_disponible', 0)
                    
                    if cantidad_disponible < cantidad_solicitada:
                        # Stock insuficiente
                        items_con_problemas.append({
                            'producto_id': producto_id,
                            'nombre': item['nombre'],
                            'cantidad_solicitada': cantidad_solicitada,
                            'cantidad_disponible': cantidad_disponible,
                            'problema': 'stock_insuficiente',
                            'mensaje': f'Stock insuficiente: disponible {cantidad_disponible}, solicitado {cantidad_solicitada}'
                        })
                    else:
                        # Producto válido
                        items_validos.append(item)
            
            # Si hay productos con problemas, devolver error detallado
            if items_con_problemas:
                productos_no_existen = [item for item in items_con_problemas if item['problema'] == 'no_existe']
                productos_stock_insuficiente = [item for item in items_con_problemas if item['problema'] == 'stock_insuficiente']
                
                if productos_no_existen and productos_stock_insuficiente:
                    # Mezcla de problemas
                    mensaje_principal = f"❌ Problemas de inventario: {len(productos_no_existen)} productos no existen, {len(productos_stock_insuficiente)} con stock insuficiente"
                elif productos_no_existen:
                    mensaje_principal = f"❌ {len(productos_no_existen)} productos no existen en inventario"
                else:
                    mensaje_principal = f"⚠️ {len(productos_stock_insuficiente)} productos con stock insuficiente"
                
                return {
                    'success': False,
                    'error': mensaje_principal,
                    'detalle': 'No se puede confirmar el pedido debido a problemas de inventario',
                    'items_con_problemas': items_con_problemas,
                    'items_validos': items_validos,
                    'resumen': {
                        'total_items': len(items_info),
                        'items_validos': len(items_validos),
                        'items_con_problemas': len(items_con_problemas),
                        'productos_no_existen': len(productos_no_existen),
                        'productos_stock_insuficiente': len(productos_stock_insuficiente)
                    }
                }
            
            # Confirmar el pedido
            if not pedido.confirmar():
                return {
                    'success': False,
                    'error': 'Error confirmando el pedido'
                }
            
            # Actualizar en repositorio
            pedido_confirmado = self._repositorio.actualizar(pedido)
            
            # Disparar evento de confirmación
            evento = pedido_confirmado.disparar_evento_confirmacion()
            despachador_eventos.publicar_evento(evento)
            
            return {
                'success': True,
                'message': 'Pedido confirmado exitosamente',
                'pedido_id': str(pedido_confirmado.id),
                'vendedor_id': pedido_confirmado.vendedor_id,
                'cliente_id': pedido_confirmado.cliente_id,
                'estado': pedido_confirmado.estado.estado,
                'total': pedido_confirmado.total.valor,
                'items_count': len(pedido_confirmado.items)
            }
            
        except Exception as e:
            logger.error(f"Error confirmando pedido: {e}")
            return {
                'success': False,
                'error': f'Error interno: {str(e)}'
            }

@comando.register(ConfirmarPedido)
def ejecutar_confirmar_pedido(comando: ConfirmarPedido):
    handler = ConfirmarPedidoHandler()
    return handler.handle(comando)
