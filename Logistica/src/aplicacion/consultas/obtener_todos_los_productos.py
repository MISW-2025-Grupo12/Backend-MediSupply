from dataclasses import dataclass
from seedwork.aplicacion.consultas import Consulta, ejecutar_consulta
from infraestructura.repositorios import RepositorioBodegaSQLite

@dataclass
class ObtenerTodosLosProductos(Consulta):
    pass

class ObtenerTodosLosProductosHandler:
    def __init__(self, repositorio_bodega=None):
        self.repositorio_bodega = repositorio_bodega or RepositorioBodegaSQLite()
    
    def handle(self, consulta: ObtenerTodosLosProductos):
        # Obtener todos los inventarios de todas las bodegas
        inventarios = self.repositorio_bodega.obtener_todos_los_inventarios()
        
        productos_agrupados = {}
        for inv in inventarios:
            pid = inv.producto_id
            if pid not in productos_agrupados:
                productos_agrupados[pid] = {
                    'producto_id': pid,
                    'cantidad_total': 0,
                    'ubicaciones': []
                }
            
            productos_agrupados[pid]['cantidad_total'] += inv.cantidad_disponible + inv.cantidad_reservada
            productos_agrupados[pid]['ubicaciones'].append({
                'bodega_id': inv.bodega_id,
                'pasillo': inv.pasillo,
                'estante': inv.estante,
                'cantidad_disponible': inv.cantidad_disponible,
                'cantidad_reservada': inv.cantidad_reservada
            })
        
        return list(productos_agrupados.values())

@ejecutar_consulta.register
def _(consulta: ObtenerTodosLosProductos):
    handler = ObtenerTodosLosProductosHandler()
    return handler.handle(consulta)
