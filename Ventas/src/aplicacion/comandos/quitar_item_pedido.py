from dataclasses import dataclass
from seedwork.aplicacion.comandos import Comando
from seedwork.aplicacion.comandos import ejecutar_comando as comando
from infraestructura.repositorios import RepositorioPedidoSQLite
from seedwork.dominio.eventos import despachador_eventos
from dominio.eventos import ItemQuitado
import logging

logger = logging.getLogger(__name__)

@dataclass
class QuitarItemPedido(Comando):
    pedido_id: str
    item_id: str

class QuitarItemPedidoHandler:
    def __init__(self):
        self._repositorio: RepositorioPedidoSQLite = RepositorioPedidoSQLite()
    
    def handle(self, comando: QuitarItemPedido) -> dict:
        """Quitar un item del pedido"""
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
                    'error': 'Solo se pueden quitar items de pedidos en estado borrador'
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
            
            # Quitar el item del pedido
            if not pedido.quitar_item(comando.item_id):
                return {
                    'success': False,
                    'error': 'Error quitando item del pedido'
                }
            
            # Actualizar en repositorio
            pedido_actualizado = self._repositorio.actualizar(pedido)
            
            # Disparar evento
            evento = ItemQuitado(
                pedido_id=pedido.id,
                item_id=item_encontrado.id,
                producto_id=item_encontrado.producto_id
            )
            despachador_eventos.publicar_evento(evento)
            
            return {
                'success': True,
                'message': 'Item quitado del pedido exitosamente',
                'total_pedido': pedido_actualizado.total.valor
            }
            
        except Exception as e:
            logger.error(f"Error quitando item del pedido: {e}")
            return {
                'success': False,
                'error': f'Error interno: {str(e)}'
            }

@comando.register(QuitarItemPedido)
def ejecutar_quitar_item_pedido(comando: QuitarItemPedido):
    handler = QuitarItemPedidoHandler()
    return handler.handle(comando)
