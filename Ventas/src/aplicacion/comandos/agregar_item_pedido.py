from dataclasses import dataclass
from seedwork.aplicacion.comandos import Comando
from seedwork.aplicacion.comandos import ejecutar_comando as comando
from infraestructura.repositorios import RepositorioPedidoSQLite
from infraestructura.servicio_logistica import ServicioLogistica
from infraestructura.servicio_productos import ServicioProductos
from dominio.entidades import ItemPedido
from dominio.objetos_valor import Cantidad, Precio
from seedwork.dominio.eventos import despachador_eventos
from dominio.eventos import ItemAgregado
import uuid
import logging

logger = logging.getLogger(__name__)

@dataclass
class AgregarItemPedido(Comando):
    pedido_id: str
    producto_id: str
    cantidad: int

class AgregarItemPedidoHandler:
    def __init__(self):
        self._repositorio: RepositorioPedidoSQLite = RepositorioPedidoSQLite()
        self._servicio_logistica: ServicioLogistica = ServicioLogistica()
        self._servicio_productos: ServicioProductos = ServicioProductos()
    
    def handle(self, comando: AgregarItemPedido) -> dict:
        """Agregar un item al pedido"""
        try:
            # Validar datos de entrada
            if not comando.pedido_id or not comando.producto_id or comando.cantidad <= 0:
                return {
                    'success': False,
                    'error': 'pedido_id, producto_id y cantidad > 0 son obligatorios'
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
                    'error': 'Solo se pueden agregar items a pedidos en estado borrador'
                }
            
            # Consultar producto para obtener nombre y precio
            producto = self._servicio_productos.obtener_producto_por_id(comando.producto_id)
            if not producto:
                return {
                    'success': False,
                    'error': f'Producto {comando.producto_id} no encontrado en el catálogo'
                }
            
            # Validar precio del producto
            precio_actual = producto.get('precio', 0.0)
            if precio_actual <= 0:
                return {
                    'success': False,
                    'error': f'El producto {comando.producto_id} no tiene un precio válido'
                }
            
            # Crear item de pedido con datos reales del producto
            item = ItemPedido(
                id=uuid.uuid4(),
                producto_id=comando.producto_id,
                nombre_producto=producto.get('nombre', 'Producto'),
                cantidad=Cantidad(comando.cantidad),
                precio_unitario=Precio(precio_actual)
            )
            
            # Agregar item al pedido
            if not pedido.agregar_item(item):
                return {
                    'success': False,
                    'error': 'Error agregando item al pedido'
                }
            
            # Actualizar en repositorio
            pedido_actualizado = self._repositorio.actualizar(pedido)
            
            # Disparar evento
            evento = ItemAgregado(
                pedido_id=pedido.id,
                item_id=item.id,
                producto_id=item.producto_id,
                cantidad=item.cantidad.valor,
                subtotal=item.calcular_subtotal()
            )
            despachador_eventos.publicar_evento(evento)
            
            return {
                'success': True,
                'item_id': str(item.id),
                'producto_id': item.producto_id,
                'nombre_producto': item.nombre_producto,
                'cantidad': item.cantidad.valor,
                'precio_unitario': item.precio_unitario.valor,
                'subtotal': item.calcular_subtotal(),
                'mensaje': 'Item agregado exitosamente con nombre y precio del producto.'
            }
            
        except Exception as e:
            logger.error(f"Error agregando item al pedido: {e}")
            return {
                'success': False,
                'error': f'Error interno: {str(e)}'
            }

@comando.register(AgregarItemPedido)
def ejecutar_agregar_item_pedido(comando: AgregarItemPedido):
    handler = AgregarItemPedidoHandler()
    return handler.handle(comando)
