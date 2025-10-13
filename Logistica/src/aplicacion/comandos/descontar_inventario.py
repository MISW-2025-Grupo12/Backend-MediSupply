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
                
                # Obtener inventario actual
                inventario_dto = self._repositorio.obtener_por_producto_id(producto_id)
                if not inventario_dto:
                    return {
                        'success': False,
                        'error': f'Producto {producto_id} no encontrado en inventario'
                    }
                
                if inventario_dto.cantidad_reservada < cantidad_a_descontar:
                    return {
                        'success': False,
                        'error': f'Cantidad reservada insuficiente para producto {producto_id}. Reservada: {inventario_dto.cantidad_reservada}, A descontar: {cantidad_a_descontar}'
                    }
            
            # Si todas las validaciones pasan, proceder con el descuento
            for item in comando.items:
                producto_id = item.get('producto_id')
                cantidad_a_descontar = item.get('cantidad', 0)
                
                # Obtener inventario actual
                inventario_dto = self._repositorio.obtener_por_producto_id(producto_id)
                
                # Crear entidad de dominio
                inventario = Inventario(
                    id=inventario_dto.producto_id,
                    producto_id=ProductoID(inventario_dto.producto_id),
                    cantidad_disponible=Cantidad(inventario_dto.cantidad_disponible),
                    cantidad_reservada=Cantidad(inventario_dto.cantidad_reservada)
                )
                
                # Descontar cantidad (sale del sistema)
                if not inventario.descontar_cantidad(cantidad_a_descontar):
                    # Si falla, hacer rollback de los anteriores
                    logger.error(f"Error descontando cantidad para producto {producto_id}")
                    return {
                        'success': False,
                        'error': f'Error descontando inventario para producto {producto_id}'
                    }
                
                # Actualizar en base de datos
                nuevo_inventario_dto = InventarioDTO(
                    producto_id=inventario.producto_id.valor,
                    cantidad_disponible=inventario.cantidad_disponible.valor,
                    cantidad_reservada=inventario.cantidad_reservada.valor
                )
                
                self._repositorio.crear_o_actualizar(nuevo_inventario_dto)
            
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
