"""Servicio para obtener historial de compras del cliente"""
import logging
from typing import Dict, List
from infraestructura.repositorios import RepositorioPedidoSQLite

logger = logging.getLogger(__name__)

class ServicioHistorialCliente:
    """Servicio para obtener y procesar historial de compras del cliente"""
    
    def __init__(self, repositorio_pedidos=None):
        self.repositorio_pedidos = repositorio_pedidos or RepositorioPedidoSQLite()
    
    def obtener_historial_cliente(self, cliente_id: str, limite: int = 10) -> Dict:
        """
        Obtener historial de compras del cliente
        
        Args:
            cliente_id: ID del cliente
            limite: Número máximo de pedidos a obtener (default: 10)
        
        Returns:
            Dict con resumen del historial:
            - total_pedidos: Total de pedidos del cliente
            - ultimos_pedidos: Lista de últimos pedidos
            - productos_mas_comprados: Lista de productos más comprados
            - frecuencia_compra: Frecuencia aproximada de compra
        """
        try:
            # Obtener todos los pedidos del cliente
            todos_los_pedidos = self.repositorio_pedidos.obtener_todos()
            pedidos_cliente = [p for p in todos_los_pedidos if p.cliente_id == cliente_id]
            
            if not pedidos_cliente:
                return {
                    'total_pedidos': 0,
                    'ultimos_pedidos': [],
                    'productos_mas_comprados': [],
                    'frecuencia_compra': 'Sin compras anteriores'
                }
            
            # Ordenar por fecha de creación (más recientes primero)
            pedidos_ordenados = sorted(
                pedidos_cliente,
                key=lambda p: getattr(p, '_created_at_model', None) or getattr(p, 'created_at', None) or None,
                reverse=True
            )
            
            # Obtener últimos N pedidos
            ultimos_pedidos = pedidos_ordenados[:limite]
            
            # Procesar últimos pedidos para el resumen
            ultimos_pedidos_resumen = []
            for pedido in ultimos_pedidos:
                fecha_creacion = getattr(pedido, '_created_at_model', None)
                fecha_str = fecha_creacion.isoformat() if fecha_creacion else 'Fecha no disponible'
                
                items_resumen = []
                for item in pedido.items:
                    items_resumen.append({
                        'producto_id': item.producto_id,
                        'nombre': item.nombre_producto,
                        'cantidad': item.cantidad.valor,
                        'precio_unitario': item.precio_unitario.valor
                    })
                
                ultimos_pedidos_resumen.append({
                    'id': str(pedido.id),
                    'fecha': fecha_str,
                    'total': pedido.total.valor,
                    'estado': pedido.estado.estado,
                    'items': items_resumen
                })
            
            # Calcular productos más comprados
            productos_comprados = {}
            for pedido in pedidos_cliente:
                for item in pedido.items:
                    producto_id = item.producto_id
                    if producto_id not in productos_comprados:
                        productos_comprados[producto_id] = {
                            'producto_id': producto_id,
                            'nombre': item.nombre_producto,
                            'cantidad_total': 0,
                            'veces_comprado': 0,
                            'precio_promedio': 0.0
                        }
                    
                    productos_comprados[producto_id]['cantidad_total'] += item.cantidad.valor
                    productos_comprados[producto_id]['veces_comprado'] += 1
                    # Calcular precio promedio
                    precio_actual = productos_comprados[producto_id]['precio_promedio']
                    veces = productos_comprados[producto_id]['veces_comprado']
                    precio_nuevo = item.precio_unitario.valor
                    productos_comprados[producto_id]['precio_promedio'] = (
                        (precio_actual * (veces - 1) + precio_nuevo) / veces
                    )
            
            # Ordenar productos por cantidad total (más comprados primero)
            productos_mas_comprados = sorted(
                productos_comprados.values(),
                key=lambda x: x['cantidad_total'],
                reverse=True
            )[:10]  # Top 10 productos más comprados
            
            # Calcular frecuencia de compra
            if len(pedidos_cliente) > 1:
                fechas = [
                    getattr(p, '_created_at_model', None)
                    for p in pedidos_cliente
                    if getattr(p, '_created_at_model', None) is not None
                ]
                if fechas:
                    fechas_ordenadas = sorted(fechas)
                    dias_entre = (fechas_ordenadas[-1] - fechas_ordenadas[0]).days
                    if dias_entre > 0:
                        frecuencia = len(pedidos_cliente) / (dias_entre / 30)  # Pedidos por mes
                        if frecuencia >= 4:
                            frecuencia_str = f"{frecuencia:.1f} pedidos por mes (frecuente)"
                        elif frecuencia >= 2:
                            frecuencia_str = f"{frecuencia:.1f} pedidos por mes (regular)"
                        else:
                            frecuencia_str = f"{frecuencia:.1f} pedidos por mes (ocasional)"
                    else:
                        frecuencia_str = "Cliente nuevo"
                else:
                    frecuencia_str = "Frecuencia no calculable"
            else:
                frecuencia_str = "Cliente con una sola compra"
            
            return {
                'total_pedidos': len(pedidos_cliente),
                'ultimos_pedidos': ultimos_pedidos_resumen,
                'productos_mas_comprados': productos_mas_comprados,
                'frecuencia_compra': frecuencia_str
            }
            
        except Exception as e:
            logger.error(f"Error obteniendo historial del cliente {cliente_id}: {e}")
            return {
                'total_pedidos': 0,
                'ultimos_pedidos': [],
                'productos_mas_comprados': [],
                'frecuencia_compra': 'Error al obtener historial'
            }

