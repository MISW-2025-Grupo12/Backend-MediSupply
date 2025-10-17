from dataclasses import dataclass
from operator import inv
from seedwork.aplicacion.consultas import Consulta, ejecutar_consulta
from infraestructura.repositorios import RepositorioBodegaSQLite
from infraestructura.servicio_productos import ServicioProductos
from datetime import date, datetime

@dataclass
class ObtenerTodosLosProductos(Consulta):
    pass

class ObtenerTodosLosProductosHandler:
    def __init__(self, repositorio_bodega=None, servicio_productos=None):
        self.repositorio_bodega = repositorio_bodega or RepositorioBodegaSQLite()
        self.servicio_productos = servicio_productos or ServicioProductos()
    
    def handle(self, consulta: ObtenerTodosLosProductos):
        # Obtener todos los inventarios de todas las bodegas
        inventarios = self.repositorio_bodega.obtener_todos_los_inventarios()

        # Mapa id->producto para sacar la categoría (defensivo)
        try:
            catalogo = self.servicio_productos.obtener_todos_productos() or []
            productos_por_id = {str(p.get('id')): p for p in catalogo}
        except Exception:
            productos_por_id = {}
        
        productos_agrupados = {}
        for inv in inventarios:
            pid = inv.producto_id
            pid_key = str(pid)

            if pid not in productos_agrupados:
                det = productos_por_id.get(pid_key)
                producto_nombre = det.get('nombre') if det else None
                categoria_id = (
                    det.get('categoria_id')
                    or (det.get('categoria', {}).get('id') if isinstance(det.get('categoria'), dict) else None)
                    if det else None
                )
                categoria_nombre = (
                    (det.get('categoria') if isinstance(det.get('categoria'), str) else None)
                    or det.get('categoria_nombre')
                    or (det.get('categoria', {}).get('nombre') if isinstance(det.get('categoria'), dict) else None)
                    if det else None
                )

                fecha_vencimiento = getattr(inv, 'fecha_vencimiento', None)
                if isinstance(fecha_vencimiento, (datetime, date)):
                    fecha_vencimiento = fecha_vencimiento.isoformat()

                requiere_cadena_frio = getattr(inv, 'requiere_cadena_frio', False)

                productos_agrupados[pid] = {
                    'id': str(pid),
                    'nombre': producto_nombre or 'Producto sin nombre',
                    'descripcion': det.get('descripcion', '') if det else '',
                    'precio': det.get('precio', 0) if det else 0,
                    'stock': 0,
                    'fecha_vencimiento': fecha_vencimiento,
                    'requiere_cadena_frio': requiere_cadena_frio,
                    'categoria': {
                        'id': str(categoria_id) if categoria_id else '1',
                        'nombre': categoria_nombre or 'Sin categoría',
                        'descripcion': det.get('categoria', {}).get('descripcion', '') if det else ''
                    },
                    'proveedor': {
                        'id': str(det.get('proveedor', {}).get('id', '1')) if det else '1',
                        'nombre': det.get('proveedor', {}).get('nombre', 'Proveedor genérico') if det else 'Proveedor genérico',
                        'email': det.get('proveedor', {}).get('email', '') if det else '',
                        'direccion': det.get('proveedor', {}).get('direccion', '') if det else ''
                    },
                    'ubicaciones': []
                }

            productos_agrupados[pid]['stock'] += inv.cantidad_disponible

            # Obtener información de la bodega
            bodega_nombre = "Sin asignar"
            if inv.bodega_id:
                bodega = self.repositorio_bodega.obtener_por_id(inv.bodega_id)
                if bodega:
                    bodega_nombre = bodega.nombre
            
            productos_agrupados[pid]['ubicaciones'].append({
                'id': str(inv.id),
                'bodega_id': str(inv.bodega_id) if inv.bodega_id else None,
                'nombre': bodega_nombre,
                'pasillo': inv.pasillo,
                'estante': inv.estante,
                'stock_disponible': inv.cantidad_disponible,
                'stock_reservado': inv.cantidad_reservada
            })

        return list(productos_agrupados.values())

@ejecutar_consulta.register
def _(consulta: ObtenerTodosLosProductos):
    handler = ObtenerTodosLosProductosHandler()
    return handler.handle(consulta)
