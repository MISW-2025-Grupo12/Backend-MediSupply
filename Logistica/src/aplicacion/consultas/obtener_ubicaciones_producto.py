from dataclasses import dataclass
from seedwork.aplicacion.consultas import Consulta, ejecutar_consulta
from infraestructura.repositorios import RepositorioInventarioSQLite, RepositorioBodegaSQLite
from infraestructura.servicio_productos import ServicioProductos
import logging

logger = logging.getLogger(__name__)

@dataclass
class ObtenerUbicacionesProducto(Consulta):
    producto_id: str

class ObtenerUbicacionesProductoHandler:
    def __init__(self, repositorio_inventario=None, repositorio_bodega=None, servicio_productos=None):
        self.repositorio_inventario = repositorio_inventario or RepositorioInventarioSQLite()
        self.repositorio_bodega = repositorio_bodega or RepositorioBodegaSQLite()
        self.servicio_productos = servicio_productos or ServicioProductos()
    
    def handle(self, consulta: ObtenerUbicacionesProducto) -> dict:
        logger.info(f"Obteniendo ubicaciones del producto {consulta.producto_id} en todas las bodegas...")
        
        # Obtener todos los lotes de inventario del producto
        lotes_inventario = self.repositorio_inventario.obtener_por_producto_id(consulta.producto_id)
        
        if not lotes_inventario:
            return {
                'producto_id': consulta.producto_id,
                'ubicaciones': [],
                'total_bodegas': 0,
                'total_cantidad_disponible': 0,
                'total_cantidad_reservada': 0,
                'mensaje': 'Producto no encontrado en inventario'
            }
        
        # Agrupar por bodega
        ubicaciones_por_bodega = {}
        total_cantidad_disponible = 0
        total_cantidad_reservada = 0
        
        for lote in lotes_inventario:
            bodega_id = lote.bodega_id or 'sin_asignar'
            
            if bodega_id not in ubicaciones_por_bodega:
                ubicaciones_por_bodega[bodega_id] = {
                    'bodega_id': lote.bodega_id,
                    'bodega_nombre': 'Sin asignar' if not lote.bodega_id else None,
                    'bodega_direccion': None,
                    'total_cantidad_disponible': 0,
                    'total_cantidad_reservada': 0,
                    'ubicaciones_fisicas': []
                }
            
            # Sumar cantidades
            ubicaciones_por_bodega[bodega_id]['total_cantidad_disponible'] += lote.cantidad_disponible
            ubicaciones_por_bodega[bodega_id]['total_cantidad_reservada'] += lote.cantidad_reservada
            
            # Agregar ubicación física
            bodega_nombre = ubicaciones_por_bodega[bodega_id]['bodega_nombre']
            ubicacion_fisica = {
                'pasillo': lote.pasillo,
                'estante': lote.estante,
                'cantidad_disponible': lote.cantidad_disponible,
                'cantidad_reservada': lote.cantidad_reservada,
                'fecha_vencimiento': lote.fecha_vencimiento.isoformat(),
                'ubicacion_descripcion': f"{bodega_nombre} - Pasillo {lote.pasillo} - Estante {lote.estante}" if lote.bodega_id else "Sin ubicación asignada"
            }
            ubicaciones_por_bodega[bodega_id]['ubicaciones_fisicas'].append(ubicacion_fisica)
            
            # Sumar totales generales
            total_cantidad_disponible += lote.cantidad_disponible
            total_cantidad_reservada += lote.cantidad_reservada
        
        # Obtener información de bodegas ANTES de crear ubicaciones físicas
        for bodega_id, ubicacion in ubicaciones_por_bodega.items():
            if bodega_id != 'sin_asignar' and ubicacion['bodega_id']:
                bodega = self.repositorio_bodega.obtener_por_id(bodega_id)
                if bodega:
                    ubicacion['bodega_nombre'] = bodega.nombre
                    ubicacion['bodega_direccion'] = bodega.direccion
        
        # Ahora actualizar las ubicaciones físicas con el nombre correcto de la bodega
        for bodega_id, ubicacion in ubicaciones_por_bodega.items():
            for ubicacion_fisica in ubicacion['ubicaciones_fisicas']:
                if ubicacion['bodega_nombre'] and ubicacion['bodega_nombre'] != 'Sin asignar':
                    ubicacion_fisica['ubicacion_descripcion'] = f"{ubicacion['bodega_nombre']} - Pasillo {ubicacion_fisica['pasillo']} - Estante {ubicacion_fisica['estante']}"
        
        # Convertir a lista
        ubicaciones = list(ubicaciones_por_bodega.values())
        
        logger.info(f"Producto {consulta.producto_id} encontrado en {len(ubicaciones)} bodegas")
        
        # Consultar detalles del producto en el microservicio de productos
        try:
            det = self.servicio_productos.obtener_producto_por_id(consulta.producto_id) or {}
        except Exception:
            det = {}

        # Extraer campos del producto
        producto_nombre = det.get('nombre', 'Producto sin nombre')
        descripcion = det.get('descripcion', '')
        precio = det.get('precio', 0)
        categoria = det.get('categoria', {}) if isinstance(det.get('categoria'), dict) else {}
        proveedor = det.get('proveedor', {}) if isinstance(det.get('proveedor'), dict) else {}

        # Armar estructura homóloga al endpoint /bodegas/productos
        producto = {
            'id': str(consulta.producto_id),
            'nombre': producto_nombre,
            'descripcion': descripcion,
            'precio': precio,
            'stock': total_cantidad_disponible,
            'fecha_vencimiento': None,
            'requiere_cadena_frio': any(
                getattr(l, 'requiere_cadena_frio', False) for l in lotes_inventario
            ),
            'categoria': {
                'id': str(categoria.get('id', '1')),
                'nombre': categoria.get('nombre', 'Sin categoría'),
                'descripcion': categoria.get('descripcion', '')
            },
            'proveedor': {
                'id': str(proveedor.get('id', '1')),
                'nombre': proveedor.get('nombre', 'Proveedor genérico'),
                'email': proveedor.get('email', ''),
                'direccion': proveedor.get('direccion', '')
            },
            'ubicaciones': []
        }

        # Transformar tus ubicaciones existentes al nuevo formato
        for u in ubicaciones:
            for uf in u['ubicaciones_fisicas']:
                producto['ubicaciones'].append({
                    'id': f"{u['bodega_id'] or 'sin_asignar'}-{uf['pasillo']}-{uf['estante']}",
                    'nombre': u['bodega_nombre'] or 'Sin asignar',
                    'pasillo': uf['pasillo'],
                    'estante': uf['estante'],
                    'stock_disponible': uf['cantidad_disponible'],
                    'stock_reservado': uf['cantidad_reservada']
                })

        logger.info(f"✅ Producto {consulta.producto_id} homologado con {len(producto['ubicaciones'])} ubicaciones")

        return producto


@ejecutar_consulta.register(ObtenerUbicacionesProducto)
def ejecutar_obtener_ubicaciones_producto(consulta: ObtenerUbicacionesProducto):
    handler = ObtenerUbicacionesProductoHandler()
    return handler.handle(consulta)
