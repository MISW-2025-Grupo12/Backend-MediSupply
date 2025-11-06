import requests
import os
import logging

logger = logging.getLogger(__name__)

class ServicioUsuarios:
    def __init__(self):
        self.base_url = os.getenv('USUARIOS_SERVICE_URL', 'http://localhost:5001/usuarios/api')
    
    def obtener_cliente_por_id(self, cliente_id: str) -> dict:
        """Obtener cliente por ID desde el servicio de Usuarios"""
        try:
            url = f"{self.base_url}/clientes/{cliente_id}"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                return None
            else:
                logger.error(f"Error obteniendo cliente {cliente_id}: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error consultando servicio de usuarios para cliente {cliente_id}: {e}")
            return None

