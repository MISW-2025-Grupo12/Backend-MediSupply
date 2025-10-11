from dataclasses import dataclass
from seedwork.aplicacion.consultas import Consulta
from seedwork.aplicacion.consultas import ejecutar_consulta as consulta
from infraestructura.repositorios import RepositorioPedidoSQLite
import logging

logger = logging.getLogger(__name__)

@dataclass
class ObtenerPedidos(Consulta):
    """Consulta para obtener todos los pedidos"""
    vendedor_id: str = None  # Filtro opcional por vendedor
    estado: str = None       # Filtro opcional por estado

class ObtenerPedidosHandler:
    def __init__(self):
        self._repositorio: RepositorioPedidoSQLite = RepositorioPedidoSQLite()
    
    def handle(self, consulta: ObtenerPedidos) -> list[dict]:
        """Obtener todos los pedidos con filtros opcionales"""
        try:
            # Obtener todos los pedidos del repositorio
            pedidos = self._repositorio.obtener_todos()
            
            # Aplicar filtros si se especifican
            if consulta.vendedor_id:
                pedidos = [p for p in pedidos if p.vendedor_id == consulta.vendedor_id]
            
            if consulta.estado:
                pedidos = [p for p in pedidos if p.estado.estado == consulta.estado]
            
            # Convertir a diccionarios para respuesta
            pedidos_data = []
            for pedido in pedidos:
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
                
                pedidos_data.append({
                    'id': str(pedido.id),
                    'vendedor_id': pedido.vendedor_id,
                    'cliente_id': pedido.cliente_id,
                    'estado': pedido.estado.estado,
                    'total': pedido.total.valor,
                    'items': items_data
                })
            
            logger.info(f"Retornando {len(pedidos_data)} pedidos")
            return pedidos_data
            
        except Exception as e:
            logger.error(f"Error obteniendo pedidos: {e}")
            return []

@consulta.register(ObtenerPedidos)
def ejecutar_obtener_pedidos(consulta: ObtenerPedidos):
    handler = ObtenerPedidosHandler()
    return handler.handle(consulta)
