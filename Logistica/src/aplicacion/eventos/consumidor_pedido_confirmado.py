from seedwork.dominio.eventos import ManejadorEvento
from aplicacion.comandos.descontar_inventario import DescontarInventario
from aplicacion.comandos.crear_entrega import CrearEntrega
from seedwork.aplicacion.comandos import ejecutar_comando
import logging

logger = logging.getLogger(__name__)

class ManejadorPedidoConfirmado(ManejadorEvento):
    def manejar(self, evento):
        """Maneja el evento PedidoConfirmado para descontar inventario y crear entrega"""
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
            comando_descontar = DescontarInventario(items=items_para_descontar)
            resultado_descontar = ejecutar_comando(comando_descontar)
            
            if resultado_descontar.get('success'):
                logger.info(f"Inventario descontado exitosamente para pedido {evento.pedido_id}")
                
                # Crear entrega automáticamente después de descontar inventario
                comando_crear_entrega = CrearEntrega(
                    pedido_id=str(evento.pedido_id),
                    cliente_id=evento.cliente_id,
                    vendedor_id=evento.vendedor_id,
                    items=evento.items,
                    total=evento.total
                )
                resultado_entrega = ejecutar_comando(comando_crear_entrega)
                
                if resultado_entrega.get('success'):
                    logger.info(f"Entrega creada exitosamente para pedido {evento.pedido_id}")
                else:
                    logger.error(f"Error creando entrega para pedido {evento.pedido_id}: {resultado_entrega.get('error')}")
            else:
                logger.error(f"Error descontando inventario para pedido {evento.pedido_id}: {resultado_descontar.get('error')}")
                
        except Exception as e:
            logger.error(f"Error manejando evento PedidoConfirmado: {e}")

# Registrar el manejador
from seedwork.dominio.eventos import despachador_eventos
manejador = ManejadorPedidoConfirmado()
despachador_eventos.registrar_manejador('PedidoConfirmado', manejador)
