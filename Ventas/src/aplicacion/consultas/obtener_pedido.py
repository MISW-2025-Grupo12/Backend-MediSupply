from dataclasses import dataclass
from seedwork.aplicacion.consultas import Consulta
from seedwork.aplicacion.consultas import ejecutar_consulta as consulta
from infraestructura.repositorios import RepositorioPedidoSQLite
import logging

logger = logging.getLogger(__name__)

@dataclass
class ObtenerPedido(Consulta):
    pedido_id: str

class ObtenerPedidoHandler:
    def __init__(self):
        self._repositorio: RepositorioPedidoSQLite = RepositorioPedidoSQLite()
    
    def handle(self, consulta: ObtenerPedido) -> dict:
        """Obtener un pedido por ID con sus items"""
        try:
            # Validar datos de entrada
            if not consulta.pedido_id:
                return None
            
            # Obtener pedido del repositorio
            pedido = self._repositorio.obtener_por_id(consulta.pedido_id)
            if not pedido:
                return None
            
            # Convertir a diccionario para respuesta
            items_data = []
            for item in pedido.items:
                items_data.append({
                    'id': str(item.id),
                    'producto_id': item.producto_id,
                    'nombre_producto': item.nombre_producto,
                    'cantidad': item.cantidad.valor,
                    'precio_unitario': item.precio_unitario.valor,
                    'subtotal': item.calcular_subtotal()
                })
            
            return {
                'id': str(pedido.id),
                'vendedor_id': pedido.vendedor_id,
                'cliente_id': pedido.cliente_id,
                'estado': pedido.estado.estado,
                'total': pedido.total.valor,
                'items': items_data
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo pedido: {e}")
            return None

@consulta.register(ObtenerPedido)
def ejecutar_obtener_pedido(consulta: ObtenerPedido):
    handler = ObtenerPedidoHandler()
    return handler.handle(consulta)
