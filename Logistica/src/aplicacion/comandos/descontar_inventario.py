from dataclasses import dataclass
from seedwork.aplicacion.comandos import Comando
from seedwork.aplicacion.comandos import ejecutar_comando as comando
from infraestructura.repositorios import RepositorioInventarioSQLite
from aplicacion.dto import InventarioDTO
from dominio.objetos_valor import ProductoID, Cantidad
from dominio.entidades import Inventario
import logging

logger = logging.getLogger(__name__)

@dataclass
class DescontarInventario(Comando):
    items: list[dict]  # [{"producto_id": str, "cantidad": int}, ...]

class DescontarInventarioHandler:
    def __init__(self):
        self._repositorio: RepositorioInventarioSQLite = RepositorioInventarioSQLite()
    
    def handle(self, comando: DescontarInventario) -> dict:
        """Descuenta inventario reservado (sale del sistema definitivamente)"""
        try:
            # Validar que todos los productos tengan cantidad reservada suficiente
            for item in comando.items:
                producto_id = item.get('producto_id')
                cantidad_a_descontar = item.get('cantidad', 0)
                
                if not producto_id or cantidad_a_descontar <= 0:
                    return {
                        'success': False,
                        'error': f'Datos inválidos para producto {producto_id}'
                    }
                
                # Obtener TODOS los lotes de inventario del producto (retorna lista)
                lotes_inventario = self._repositorio.obtener_por_producto_id(producto_id)
                if not lotes_inventario:
                    return {
                        'success': False,
                        'error': f'Producto {producto_id} no encontrado en inventario'
                    }
                
                # Sumar cantidad reservada total de todos los lotes
                total_reservado = sum(lote.cantidad_reservada for lote in lotes_inventario)
                
                if total_reservado < cantidad_a_descontar:
                    return {
                        'success': False,
                        'error': f'Cantidad reservada insuficiente para producto {producto_id}. Reservada: {total_reservado}, A descontar: {cantidad_a_descontar}'
                    }
            
            # Si todas las validaciones pasan, proceder con el descuento
            for item in comando.items:
                producto_id = item.get('producto_id')
                cantidad_a_descontar = item.get('cantidad', 0)
                cantidad_restante = cantidad_a_descontar
                
                # Obtener TODOS los lotes de inventario del producto
                lotes_inventario = self._repositorio.obtener_por_producto_id(producto_id)
                
                # Descontar de los lotes con cantidad reservada (FIFO)
                # Actualización directa sin validaciones de dominio para fechas históricas
                from infraestructura.modelos import InventarioModel
                from config.db import db
                
                for lote_dto in lotes_inventario:
                    if cantidad_restante <= 0:
                        break
                    
                    if lote_dto.cantidad_reservada <= 0:
                        continue  # Este lote no tiene cantidad reservada
                    
                    # Calcular cuánto descontar de este lote
                    cantidad_de_este_lote = min(cantidad_restante, lote_dto.cantidad_reservada)
                    
                    # Validar que tenemos suficiente cantidad reservada
                    if cantidad_de_este_lote > lote_dto.cantidad_reservada:
                        logger.error(f"Cantidad insuficiente en lote para producto {producto_id}")
                        return {
                            'success': False,
                            'error': f'Error descontando inventario para producto {producto_id}'
                        }
                    
                    # Actualizar directamente en la BD sin pasar por validaciones de dominio
                    # (para soportar fechas de vencimiento históricas)
                    inventario_model = InventarioModel.query.filter_by(
                        producto_id=lote_dto.producto_id,
                        fecha_vencimiento=lote_dto.fecha_vencimiento,
                        bodega_id=lote_dto.bodega_id
                    ).first()
                    
                    if inventario_model:
                        # Descontar: reduce cantidad reservada (ya no está disponible ni reservada)
                        inventario_model.cantidad_reservada -= cantidad_de_este_lote
                        db.session.commit()
                        cantidad_restante -= cantidad_de_este_lote
                    else:
                        logger.error(f"Lote de inventario no encontrado para producto {producto_id}")
                        return {
                            'success': False,
                            'error': f'Lote de inventario no encontrado para producto {producto_id}'
                        }
            
            return {
                'success': True,
                'message': f'Inventario descontado exitosamente para {len(comando.items)} productos'
            }
            
        except Exception as e:
            logger.error(f"Error en descontar inventario: {e}")
            return {
                'success': False,
                'error': f'Error interno: {str(e)}'
            }

@comando.register(DescontarInventario)
def ejecutar_descontar_inventario(comando: DescontarInventario):
    handler = DescontarInventarioHandler()
    return handler.handle(comando)
