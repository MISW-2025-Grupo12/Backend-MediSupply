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
            logger.info(f"Consultando cliente en: {url}")
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                cliente = response.json()
                logger.info(f"Cliente {cliente_id} obtenido exitosamente: {cliente.get('nombre', 'N/A')}")
                return cliente
            elif response.status_code == 404:
                logger.warning(f"Cliente {cliente_id} no encontrado en servicio de Usuarios (404)")
                return None
            else:
                logger.error(f"Error obteniendo cliente {cliente_id}: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Error consultando servicio de usuarios para cliente {cliente_id}: {e}")
            return None

