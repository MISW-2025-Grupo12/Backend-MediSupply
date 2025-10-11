from dataclasses import dataclass
from seedwork.aplicacion.consultas import Consulta
from seedwork.aplicacion.consultas import ejecutar_consulta as consulta
from infraestructura.repositorios import RepositorioInventarioSQLite
from infraestructura.servicio_productos import ServicioProductos
import logging

logger = logging.getLogger(__name__)

@dataclass
class BuscarProductosConInventario(Consulta):
    termino: str
    limite: int = 50

class BuscarProductosConInventarioHandler:
    def __init__(self):
        self._repositorio: RepositorioInventarioSQLite = RepositorioInventarioSQLite()
        self._servicio_productos: ServicioProductos = ServicioProductos()
    
    def handle(self, consulta: BuscarProductosConInventario) -> list[dict]:
        """Busca productos en el catálogo y combina con inventario disponible"""
        try:
            # Validar término de búsqueda
            if not consulta.termino or len(consulta.termino.strip()) == 0:
                return []
            
            if len(consulta.termino) > 100:
                logger.warning(f"Término de búsqueda muy largo: {len(consulta.termino)} caracteres")
                consulta.termino = consulta.termino[:100]
            
            # Buscar productos en el catálogo
            productos = self._servicio_productos.buscar_productos(
                termino=consulta.termino.strip(),
                limite=consulta.limite
            )
            
            if not productos:
                return []
            
            # Obtener inventario de todos los productos encontrados
            inventario_por_producto = {}
            for producto in productos:
                producto_id = producto.get('id')
                if producto_id:
                    lotes_inventario = self._repositorio.obtener_por_producto_id(producto_id)
                    inventario_por_producto[producto_id] = lotes_inventario
            
            # Combinar datos del catálogo con inventario
            productos_con_inventario = []
            for producto in productos:
                producto_id = producto.get('id')
                lotes_inventario = inventario_por_producto.get(producto_id, [])
                
                # Calcular total disponible y reservado de todos los lotes
                total_disponible = sum(lote.cantidad_disponible for lote in lotes_inventario)
                total_reservado = sum(lote.cantidad_reservada for lote in lotes_inventario)
                
                # Solo incluir productos que tengan inventario registrado
                if lotes_inventario:
                    producto_con_inventario = {
                        'id': producto.get('id'),
                        'nombre': producto.get('nombre', ''),
                        'descripcion': producto.get('descripcion', ''),
                        'precio': producto.get('precio', 0.0),
                        'categoria': producto.get('categoria', ''),
                        'cantidad_disponible': total_disponible,
                        'cantidad_reservada': total_reservado,
                        'lotes': [
                            {
                                'fecha_vencimiento': lote.fecha_vencimiento.isoformat(),
                                'cantidad_disponible': lote.cantidad_disponible,
                                'cantidad_reservada': lote.cantidad_reservada
                            } for lote in lotes_inventario
                        ]
                    }
                    productos_con_inventario.append(producto_con_inventario)
            
            return productos_con_inventario
            
        except Exception as e:
            logger.error(f"Error en buscar productos con inventario: {e}")
            return []

@consulta.register(BuscarProductosConInventario)
def ejecutar_buscar_productos_con_inventario(consulta: BuscarProductosConInventario):
    handler = BuscarProductosConInventarioHandler()
    return handler.handle(consulta)
