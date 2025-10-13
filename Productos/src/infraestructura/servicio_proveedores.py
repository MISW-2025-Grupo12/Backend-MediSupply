import requests
import logging
import os

logger = logging.getLogger(__name__)

class ServicioProveedores:
    def __init__(self, base_url=None):
        # Usar variable de entorno o fallback a localhost
        self.base_url = base_url or os.getenv('USUARIOS_SERVICE_URL', 'http://localhost:5001/usuarios/api')
    
    def obtener_proveedor_por_id(self, proveedor_id: str) -> dict:
        """Obtiene un proveedor específico por ID"""
        try:
            response = requests.get(f"{self.base_url}/proveedores/{proveedor_id}")
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                return None
            else:
                logger.error(f"Error consultando proveedor {proveedor_id}: {response.status_code}")
                return None
        except Exception as e:
            logger.error(f"Error obteniendo proveedor {proveedor_id}: {e}")
            return None
    
    def validar_proveedor_existe(self, proveedor_id: str) -> bool:
        """Valida que un proveedor existe"""
        proveedor = self.obtener_proveedor_por_id(proveedor_id)
        return proveedor is not None
    
    def obtener_proveedor(self, proveedor_id: str) -> dict:
        """Obtiene los datos de un proveedor específico"""
        return self.obtener_proveedor_por_id(proveedor_id)
