import requests
import os
import logging

logger = logging.getLogger(__name__)

class ServicioLogistica:
    def __init__(self):
        self.base_url = os.getenv('LOGISTICA_SERVICE_URL', 'http://localhost:5003')
    
    def buscar_productos(self, termino: str) -> list[dict]:
        """Buscar productos con inventario disponible"""
        try:
            url = f"{self.base_url}/api/inventario/buscar"
            params = {
                'q': termino,
                'limite': 50
            }
            response = requests.get(url, params=params, timeout=5)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Error buscando productos en Logística: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Error consultando servicio de Logística para búsqueda: {e}")
            return []
    
    def obtener_inventario_producto(self, producto_id: str) -> dict:
        """Obtener inventario de un producto específico"""
        try:
            url = f"{self.base_url}/api/inventario/producto/{producto_id}"
            logger.info(f"Consultando inventario en: {url}")
            response = requests.get(url, timeout=5)
            
            logger.info(f"Respuesta del servicio de Logística: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"Datos de inventario recibidos: {data}")
                return data
            elif response.status_code == 404:
                logger.info(f"Producto {producto_id} no encontrado en inventario")
                return None
            else:
                logger.error(f"Error obteniendo inventario del producto {producto_id}: {response.status_code}")
                logger.error(f"Respuesta: {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error consultando servicio de Logística para producto {producto_id}: {e}")
            return None
    
    def reservar_inventario(self, items: list[dict]) -> dict:
        """Reservar inventario para un pedido"""
        try:
            url = f"{self.base_url}/api/inventario/reservar"
            data = {
                'items': items
            }
            response = requests.post(url, json=data, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Error reservando inventario: {response.status_code}")
                return {
                    'success': False,
                    'error': f'Error reservando inventario: {response.status_code}'
                }
                
        except Exception as e:
            logger.error(f"Error reservando inventario: {e}")
            return {
                'success': False,
                'error': f'Error interno: {str(e)}'
            }
