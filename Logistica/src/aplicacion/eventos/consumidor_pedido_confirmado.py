from seedwork.dominio.eventos import ManejadorEvento
from aplicacion.comandos.descontar_inventario import DescontarInventario
from seedwork.aplicacion.comandos import ejecutar_comando
import logging

logger = logging.getLogger(__name__)

class ManejadorPedidoConfirmado(ManejadorEvento):
    def manejar(self, evento):
        """Maneja el evento PedidoConfirmado para descontar inventario"""
        try:
            logger.info(f"Recibido evento PedidoConfirmado para pedido {evento.pedido_id}")
            
            # Preparar items para descontar
            items_para_descontar = []
            for item in evento.items:
                items_para_descontar.append({
                    'producto_id': item.get('producto_id'),
                    'cantidad': item.get('cantidad', 0)
                })
            
            # Ejecutar comando para descontar inventario
            comando = DescontarInventario(items=items_para_descontar)
            resultado = ejecutar_comando(comando)
            
            if resultado.get('success'):
                logger.info(f"Inventario descontado exitosamente para pedido {evento.pedido_id}")
            else:
                logger.error(f"Error descontando inventario para pedido {evento.pedido_id}: {resultado.get('error')}")
                
        except Exception as e:
            logger.error(f"Error manejando evento PedidoConfirmado: {e}")

# Registrar el manejador
from seedwork.dominio.eventos import despachador_eventos
manejador = ManejadorPedidoConfirmado()
despachador_eventos.registrar_manejador('PedidoConfirmado', manejador)
