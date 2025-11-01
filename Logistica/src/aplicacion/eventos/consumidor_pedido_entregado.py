from seedwork.dominio.eventos import ManejadorEvento
from aplicacion.comandos.entrega_inventario import EntregaInventario
from seedwork.aplicacion.comandos import ejecutar_comando
import logging

logger = logging.getLogger(__name__)

class ManejadorPedidoEntregado(ManejadorEvento):
    def manejar(self, evento):
        """Maneja el evento PedidoEntregado para entregar inventario"""
        try:
            logger.info(f"Recibido evento PedidoEntregado para pedido {evento.pedido_id}")
            
            # Preparar items para entregar
            items_para_entregar = []
            for item in evento.items:
                items_para_entregar.append({
                    'producto_id': item.get('producto_id'),
                    'cantidad': item.get('cantidad', 0)
                })
            
            # Ejecutar comando para entregar inventario
            comando = EntregaInventario(items=items_para_entregar)
            resultado = ejecutar_comando(comando)
            
            if resultado.get('success'):
                logger.info(f"Inventario entregado exitosamente para pedido {evento.pedido_id}")
            else:
                logger.error(f"Error entregando inventario para pedido {evento.pedido_id}: {resultado.get('error')}")
                
        except Exception as e:
            logger.error(f"Error manejando evento PedidoEntregado: {e}")

# Registrar el manejador
from seedwork.dominio.eventos import despachador_eventos
manejador = ManejadorPedidoEntregado()
despachador_eventos.registrar_manejador('PedidoEntregado', manejador)
print("ManejadorPedidoEntregado registrado correctamente")

