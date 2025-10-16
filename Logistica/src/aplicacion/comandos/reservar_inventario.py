from dataclasses import dataclass
from seedwork.aplicacion.comandos import Comando
from seedwork.aplicacion.comandos import ejecutar_comando as comando
from seedwork.dominio.eventos import EventoDominio
from infraestructura.repositorios import RepositorioInventarioSQLite
from aplicacion.dto import InventarioDTO
from dominio.objetos_valor import ProductoID, Cantidad
from dominio.entidades import Inventario
import logging

logger = logging.getLogger(__name__)

@dataclass
class ReservarInventario(Comando):
    items: list[dict]  # [{"producto_id": str, "cantidad": int}, ...]

class ReservarInventarioHandler:
    def __init__(self):
        self._repositorio: RepositorioInventarioSQLite = RepositorioInventarioSQLite()
    
    def handle(self, comando: ReservarInventario) -> dict:
        """Reserva inventario para múltiples productos de forma transaccional"""
        try:
            # Validar que todos los productos tengan stock suficiente
            for item in comando.items:
                producto_id = item.get('producto_id')
                cantidad_solicitada = item.get('cantidad', 0)
                
                if not producto_id or cantidad_solicitada <= 0:
                    return {
                        'success': False,
                        'error': f'❌ Datos inválidos para producto {producto_id}: ID del producto o cantidad inválida'
                    }
                
                # Obtener inventario actual (puede haber múltiples lotes)
                inventarios_dto = self._repositorio.obtener_por_producto_id(producto_id)
                if not inventarios_dto:
                    return {
                        'success': False,
                        'error': f'❌ Producto {producto_id} no encontrado en inventario: El producto no existe o no está disponible para la venta'
                    }
                
                # Sumar las cantidades disponibles de todos los lotes
                total_disponible = sum(inv.cantidad_disponible for inv in inventarios_dto)
                
                if total_disponible < cantidad_solicitada:
                    return {
                        'success': False,
                        'error': f'⚠️ Stock insuficiente para producto {producto_id}: Disponible: {total_disponible} unidades, Solicitado: {cantidad_solicitada} unidades'
                    }
            
            # Si todas las validaciones pasan, proceder con la reserva
            for item in comando.items:
                producto_id = item.get('producto_id')
                cantidad_solicitada = item.get('cantidad', 0)
                
                # Obtener inventario actual (múltiples lotes)
                inventarios_dto = self._repositorio.obtener_por_producto_id(producto_id)
                
                # Reservar de los lotes ordenados por fecha de vencimiento (FIFO)
                inventarios_dto_ordenados = sorted(inventarios_dto, key=lambda x: x.fecha_vencimiento)
                
                cantidad_restante = cantidad_solicitada
                for inventario_dto in inventarios_dto_ordenados:
                    if cantidad_restante <= 0:
                        break
                    
                    # Crear entidad de dominio
                    from dominio.objetos_valor import FechaVencimiento
                    inventario = Inventario(
                        id=inventario_dto.producto_id,
                        producto_id=ProductoID(inventario_dto.producto_id),
                        cantidad_disponible=Cantidad(inventario_dto.cantidad_disponible),
                        cantidad_reservada=Cantidad(inventario_dto.cantidad_reservada),
                        fecha_vencimiento=FechaVencimiento(inventario_dto.fecha_vencimiento)
                    )
                    
                    # Calcular cuánto reservar de este lote
                    cantidad_a_reservar_de_este_lote = min(cantidad_restante, inventario_dto.cantidad_disponible)
                    
                    if cantidad_a_reservar_de_este_lote > 0:
                        # Reservar cantidad
                        if not inventario.reservar_cantidad(cantidad_a_reservar_de_este_lote):
                            logger.error(f"Error reservando cantidad para producto {producto_id}")
                            return {
                                'success': False,
                                'error': f'Error reservando inventario para producto {producto_id}'
                            }
                        
                        # Actualizar en base de datos
                        nuevo_inventario_dto = InventarioDTO(
                            producto_id=inventario.producto_id.valor,
                            cantidad_disponible=inventario.cantidad_disponible.valor,
                            cantidad_reservada=inventario.cantidad_reservada.valor,
                            fecha_vencimiento=inventario_dto.fecha_vencimiento
                        )
                        
                        self._repositorio.crear_o_actualizar(nuevo_inventario_dto)
                        
                        cantidad_restante -= cantidad_a_reservar_de_este_lote
            
            return {
                'success': True,
                'message': f'Inventario reservado exitosamente para {len(comando.items)} productos'
            }
            
        except ValueError as e:
            # Error específico de validación (fecha de vencimiento, etc.)
            logger.error(f"Error en reservar inventario: {e}")
            return {
                'success': False,
                'error': str(e)
            }
        except Exception as e:
            logger.error(f"Error en reservar inventario: {e}")
            return {
                'success': False,
                'error': f'Error interno: {str(e)}'
            }

@comando.register(ReservarInventario)
def ejecutar_reservar_inventario(comando: ReservarInventario):
    handler = ReservarInventarioHandler()
    return handler.handle(comando)
