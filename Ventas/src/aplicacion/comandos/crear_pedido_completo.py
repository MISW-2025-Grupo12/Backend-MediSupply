from dataclasses import dataclass, field
from typing import List, Dict, Optional
from seedwork.aplicacion.comandos import Comando
from seedwork.aplicacion.comandos import ejecutar_comando as comando
from infraestructura.repositorios import RepositorioPedidoSQLite
from infraestructura.servicio_logistica import ServicioLogistica
from infraestructura.servicio_productos import ServicioProductos
from dominio.entidades import Pedido, ItemPedido
from dominio.objetos_valor import EstadoPedido, Precio, Cantidad
from seedwork.dominio.eventos import despachador_eventos
from dominio.eventos import PedidoCreado, PedidoConfirmado
import logging
import uuid

logger = logging.getLogger(__name__)

@dataclass
class ItemPedidoCompleto:
    producto_id: str
    cantidad: int

@dataclass
class CrearPedidoCompleto(Comando):
    vendedor_id: Optional[str] = None
    cliente_id: str = ""
    items: List[ItemPedidoCompleto] = field(default_factory=list)

class CrearPedidoCompletoHandler:
    def __init__(self):
        self._repositorio: RepositorioPedidoSQLite = RepositorioPedidoSQLite()
        self._servicio_logistica: ServicioLogistica = ServicioLogistica()
        self._servicio_productos: ServicioProductos = ServicioProductos()
    
    def handle(self, comando: CrearPedidoCompleto) -> dict:
        """Crear un pedido completo con items y confirmarlo en una sola operación"""
        try:
            # Validar datos de entrada (vendedor_id es opcional)
            if not comando.cliente_id:
                return {
                    'success': False,
                    'error': 'cliente_id es obligatorio'
                }
            
            if not comando.items or len(comando.items) == 0:
                return {
                    'success': False,
                    'error': 'El pedido debe tener al menos un item'
                }
            
            # Validar que todos los items tengan datos válidos
            for item in comando.items:
                if not item.producto_id or item.cantidad <= 0:
                    return {
                        'success': False,
                        'error': 'Todos los items deben tener producto_id y cantidad > 0'
                    }
            
            # Normalizar vendedor_id: convertir None a string vacío para la entidad de dominio
            vendedor_id_final = comando.vendedor_id if comando.vendedor_id else ""
            
            # Crear entidad de dominio del pedido
            pedido = Pedido(
                vendedor_id=vendedor_id_final,
                cliente_id=comando.cliente_id,
                estado=EstadoPedido("borrador"),
                total=Precio(0.0)
            )
            
            # Procesar cada item del pedido
            items_procesados = []
            items_con_problemas = []
            items_validos = []
            total_pedido = 0.0
            
            for item_data in comando.items:
                producto_id = item_data.producto_id
                cantidad_solicitada = item_data.cantidad
                
                # Consultar producto para obtener nombre y precio
                producto = self._servicio_productos.obtener_producto_por_id(producto_id)
                if not producto:
                    items_con_problemas.append({
                        'producto_id': producto_id,
                        'nombre': 'Producto no encontrado',
                        'cantidad_solicitada': cantidad_solicitada,
                        'cantidad_disponible': 0,
                        'problema': 'no_existe',
                        'mensaje': f'El producto {producto_id} no existe en el catálogo'
                    })
                    continue
                
                # Validar precio del producto
                precio_actual = producto.get('precio', 0.0)
                if precio_actual <= 0:
                    items_con_problemas.append({
                        'producto_id': producto_id,
                        'nombre': producto.get('nombre', 'Producto'),
                        'cantidad_solicitada': cantidad_solicitada,
                        'cantidad_disponible': 0,
                        'problema': 'precio_invalido',
                        'mensaje': f'El producto {producto_id} no tiene un precio válido'
                    })
                    continue
                
                # Consultar inventario del producto
                inventario = self._servicio_logistica.obtener_inventario_producto(producto_id)
                
                if not inventario:
                    # Producto no existe en inventario
                    items_con_problemas.append({
                        'producto_id': producto_id,
                        'nombre': producto.get('nombre', 'Producto'),
                        'cantidad_solicitada': cantidad_solicitada,
                        'cantidad_disponible': 0,
                        'problema': 'no_existe_inventario',
                        'mensaje': 'El producto no existe en el inventario'
                    })
                    continue
                
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
                        'nombre': producto.get('nombre', 'Producto'),
                        'cantidad_solicitada': cantidad_solicitada,
                        'cantidad_disponible': cantidad_disponible,
                        'problema': 'stock_insuficiente',
                        'mensaje': f'Stock insuficiente: disponible {cantidad_disponible}, solicitado {cantidad_solicitada}'
                    })
                    continue
                
                # Producto válido - crear item
                item = ItemPedido(
                    id=uuid.uuid4(),
                    producto_id=producto_id,
                    nombre_producto=producto.get('nombre', 'Producto'),
                    cantidad=Cantidad(cantidad_solicitada),
                    precio_unitario=Precio(precio_actual)
                )
                
                # Agregar item al pedido
                if pedido.agregar_item(item):
                    items_procesados.append(item)
                    items_validos.append({
                        'producto_id': producto_id,
                        'nombre': producto.get('nombre', 'Producto'),
                        'cantidad': cantidad_solicitada,
                        'precio_unitario': precio_actual,
                        'subtotal': item.calcular_subtotal()
                    })
                    total_pedido += item.calcular_subtotal()
            
            # Si hay productos con problemas, devolver error detallado
            if items_con_problemas:
                productos_no_existen = [item for item in items_con_problemas if item['problema'] in ['no_existe', 'no_existe_inventario']]
                productos_stock_insuficiente = [item for item in items_con_problemas if item['problema'] == 'stock_insuficiente']
                productos_precio_invalido = [item for item in items_con_problemas if item['problema'] == 'precio_invalido']
                
                mensaje_principal = "❌ Problemas con productos del pedido:"
                if productos_no_existen:
                    mensaje_principal += f" {len(productos_no_existen)} no existen"
                if productos_stock_insuficiente:
                    mensaje_principal += f", {len(productos_stock_insuficiente)} con stock insuficiente"
                if productos_precio_invalido:
                    mensaje_principal += f", {len(productos_precio_invalido)} con precio inválido"
                
                return {
                    'success': False,
                    'error': mensaje_principal,
                    'detalle': 'No se puede crear el pedido debido a problemas con los productos',
                    'items_con_problemas': items_con_problemas,
                    'items_validos': items_validos,
                    'resumen': {
                        'total_items_solicitados': len(comando.items),
                        'items_validos': len(items_validos),
                        'items_con_problemas': len(items_con_problemas),
                        'productos_no_existen': len(productos_no_existen),
                        'productos_stock_insuficiente': len(productos_stock_insuficiente),
                        'productos_precio_invalido': len(productos_precio_invalido)
                    }
                }
            
            # Si no hay items válidos, error
            if not items_procesados:
                return {
                    'success': False,
                    'error': 'No se pudieron procesar ningún item del pedido'
                }
            
            # Actualizar total del pedido
            pedido.total = Precio(total_pedido)
            
            # Preparar items para reservar inventario
            items_para_reservar = []
            for item in items_procesados:
                items_para_reservar.append({
                    'producto_id': item.producto_id,
                    'cantidad': item.cantidad.valor
                })
            
            # Reservar inventario
            resultado_reserva = self._servicio_logistica.reservar_inventario(items_para_reservar)
            
            if not resultado_reserva.get('success', False):
                error_detalle = resultado_reserva.get("error", "Error desconocido")
                return {
                    'success': False,
                    'error': f'❌ Error reservando inventario: {error_detalle}',
                    'detalle': 'Error inesperado durante la reserva de inventario',
                    'items_pedido': items_validos
                }
            
            # Confirmar el pedido
            if not pedido.confirmar():
                return {
                    'success': False,
                    'error': 'Error confirmando el pedido'
                }
            
            # Guardar en repositorio
            pedido_confirmado = self._repositorio.crear(pedido)
            
            # Disparar eventos
            evento_creacion = pedido_confirmado.disparar_evento_creacion()
            despachador_eventos.publicar_evento(evento_creacion)
            
            evento_confirmacion = pedido_confirmado.disparar_evento_confirmacion()
            despachador_eventos.publicar_evento(evento_confirmacion)
            
            return {
                'success': True,
                'message': 'Pedido creado y confirmado exitosamente',
                'pedido_id': str(pedido_confirmado.id),
                'vendedor_id': pedido_confirmado.vendedor_id,
                'cliente_id': pedido_confirmado.cliente_id,
                'estado': pedido_confirmado.estado.estado,
                'total': pedido_confirmado.total.valor,
                'items': items_validos,
                'items_count': len(pedido_confirmado.items)
            }
            
        except Exception as e:
            logger.error(f"Error creando pedido completo: {e}")
            return {
                'success': False,
                'error': f'Error interno: {str(e)}'
            }

@comando.register(CrearPedidoCompleto)
def ejecutar_crear_pedido_completo(comando: CrearPedidoCompleto):
    handler = CrearPedidoCompletoHandler()
    return handler.handle(comando)
