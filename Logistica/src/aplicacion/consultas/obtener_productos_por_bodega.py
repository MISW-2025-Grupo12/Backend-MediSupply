from dataclasses import dataclass
from seedwork.aplicacion.consultas import Consulta, ejecutar_consulta
from infraestructura.repositorios import RepositorioBodegaSQLite

@dataclass
class ObtenerProductosPorBodega(Consulta):
    bodega_id: str

class ObtenerProductosPorBodegaHandler:
    def __init__(self, repositorio_bodega=None):
        self.repositorio_bodega = repositorio_bodega or RepositorioBodegaSQLite()
    
    def handle(self, consulta: ObtenerProductosPorBodega):
        inventarios = self.repositorio_bodega.obtener_inventario_por_bodega(consulta.bodega_id)
        
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
                'pasillo': inv.pasillo,
                'estante': inv.estante,
                'cantidad_disponible': inv.cantidad_disponible,
                'cantidad_reservada': inv.cantidad_reservada
            })
        
        return list(productos_agrupados.values())

@ejecutar_consulta.register
def _(consulta: ObtenerProductosPorBodega):
    handler = ObtenerProductosPorBodegaHandler()
    return handler.handle(consulta)
