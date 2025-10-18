import requests
import logging
import os

logger = logging.getLogger(__name__)

class ServicioProductos:
    def __init__(self, base_url=None):
        # Usar variable de entorno o fallback a localhost
        self.base_url = base_url or os.getenv('PRODUCTOS_SERVICE_URL', 'http://localhost:5000/productos/api')
    
    def obtener_producto_por_id(self, producto_id: str) -> dict:
        """Obtiene un producto específico por ID"""
        try:
            response = requests.get(f"{self.base_url}/productos/{producto_id}")
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                logger.warning(f"Producto {producto_id} no encontrado")
                return None
            else:
                logger.error(f"Error consultando producto {producto_id}: {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"Error obteniendo producto {producto_id}: {e}")
            return None
    
    def validar_producto_existe(self, producto_id: str) -> bool:
        """Valida que un producto existe"""
        producto = self.obtener_producto_por_id(producto_id)
        return producto is not None
    
    def obtener_precio_producto(self, producto_id: str) -> float:
        """Obtiene el precio actual de un producto"""
        producto = self.obtener_producto_por_id(producto_id)
        if producto:
            return producto.get('precio', 0.0)
        return 0.0
