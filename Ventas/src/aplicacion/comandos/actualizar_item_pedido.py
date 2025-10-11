from dataclasses import dataclass
from seedwork.aplicacion.comandos import Comando
from seedwork.aplicacion.comandos import ejecutar_comando as comando
from infraestructura.repositorios import RepositorioPedidoSQLite
from infraestructura.servicio_logistica import ServicioLogistica
from seedwork.dominio.eventos import despachador_eventos
from dominio.eventos import ItemQuitado
import logging

logger = logging.getLogger(__name__)

@dataclass
class ActualizarItemPedido(Comando):
    pedido_id: str
    item_id: str
    cantidad: int

class ActualizarItemPedidoHandler:
    def __init__(self):
        self._repositorio: RepositorioPedidoSQLite = RepositorioPedidoSQLite()
        self._servicio_logistica: ServicioLogistica = ServicioLogistica()
    
    def handle(self, comando: ActualizarItemPedido) -> dict:
        """Actualizar cantidad de un item del pedido"""
        try:
            # Validar datos de entrada
            if not comando.pedido_id or not comando.item_id:
                return {
                    'success': False,
                    'error': 'pedido_id e item_id son obligatorios'
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
                    'error': 'Solo se pueden actualizar items de pedidos en estado borrador'
                }
            
            # Buscar el item en el pedido
            item_encontrado = None
            for item in pedido.items:
                if str(item.id) == comando.item_id:
                    item_encontrado = item
                    break
            
            if not item_encontrado:
                return {
                    'success': False,
                    'error': 'Item no encontrado en el pedido'
                }
            
            # Si cantidad es 0 o negativa, eliminar el item
            if comando.cantidad <= 0:
                if pedido.quitar_item(comando.item_id):
                    # Actualizar en repositorio
                    self._repositorio.actualizar(pedido)
                    
                    # Disparar evento
                    evento = ItemQuitado(
                        pedido_id=pedido.id,
                        item_id=item_encontrado.id,
                        producto_id=item_encontrado.producto_id
                    )
                    despachador_eventos.publicar_evento(evento)
                    
                    return {
                        'success': True,
                        'message': 'Item eliminado del pedido',
                        'total_pedido': pedido.total.valor
                    }
                else:
                    return {
                        'success': False,
                        'error': 'Error eliminando item del pedido'
                    }
            
            # Validar cantidad mínima
            if comando.cantidad < 1:
                return {
                    'success': False,
                    'error': 'La cantidad mínima es 1'
                }
            
            # Consultar inventario disponible para validar stock
            inventario = self._servicio_logistica.obtener_inventario_producto(item_encontrado.producto_id)
            if not inventario:
                return {
                    'success': False,
                    'error': 'Producto no encontrado en inventario'
                }
            
            # Verificar stock disponible
            if inventario.get('cantidad_disponible', 0) < comando.cantidad:
                return {
                    'success': False,
                    'error': f'Stock insuficiente. Disponible: {inventario.get("cantidad_disponible", 0)}, Solicitado: {comando.cantidad}'
                }
            
            # Actualizar cantidad del item
            if not pedido.actualizar_cantidad_item(comando.item_id, comando.cantidad):
                return {
                    'success': False,
                    'error': 'Error actualizando cantidad del item'
                }
            
            # Actualizar en repositorio
            pedido_actualizado = self._repositorio.actualizar(pedido)
            
            return {
                'success': True,
                'item_id': comando.item_id,
                'producto_id': item_encontrado.producto_id,
                'cantidad': comando.cantidad,
                'subtotal': item_encontrado.calcular_subtotal(),
                'total_pedido': pedido_actualizado.total.valor
            }
            
        except Exception as e:
            logger.error(f"Error actualizando item del pedido: {e}")
            return {
                'success': False,
                'error': f'Error interno: {str(e)}'
            }

@comando.register(ActualizarItemPedido)
def ejecutar_actualizar_item_pedido(comando: ActualizarItemPedido):
    handler = ActualizarItemPedidoHandler()
    return handler.handle(comando)
