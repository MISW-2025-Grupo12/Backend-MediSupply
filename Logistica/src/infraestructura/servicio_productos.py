import requests
import os
import logging

logger = logging.getLogger(__name__)

class ServicioProductos:
    def __init__(self):
        self.base_url = os.getenv('PRODUCTOS_SERVICE_URL', 'http://localhost:5000/productos/api')
    
    def obtener_producto_por_id(self, producto_id: str) -> dict:
        """Obtener producto por ID desde el servicio de Productos"""
        try:
            url = f"{self.base_url}/productos/{producto_id}"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                return None
            else:
                logger.error(f"Error obteniendo producto {producto_id}: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error consultando servicio de productos para producto {producto_id}: {e}")
            return None
    
    def buscar_productos(self, termino: str, limite: int = 50) -> list[dict]:
        """Buscar productos por término de búsqueda"""
        try:
            url = f"{self.base_url}/productos"
            params = {
                'q': termino,
                'limite': limite
            }
            response = requests.get(url, params=params, timeout=5)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Error buscando productos: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Error consultando servicio de productos para búsqueda: {e}")
            return []
    
    def obtener_todos_productos(self) -> list[dict]:
        """Obtener todos los productos"""
        try:
            url = f"{self.base_url}/productos"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Error obteniendo todos los productos: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Error consultando servicio de productos: {e}")
            return []
