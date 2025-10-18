import requests
import os
import logging

logger = logging.getLogger(__name__)

class ServicioUsuarios:
    def __init__(self):
        self.base_url = os.getenv('USUARIOS_SERVICE_URL', 'http://localhost:5001/usuarios/api')
    
    def obtener_vendedor_por_id(self, vendedor_id: str) -> dict:
        """Obtener vendedor por ID desde el servicio de Usuarios"""
        try:
            url = f"{self.base_url}/vendedores/{vendedor_id}"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 404:
                return None
            else:
                logger.error(f"Error obteniendo vendedor {vendedor_id}: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error consultando servicio de usuarios para vendedor {vendedor_id}: {e}")
            return None
    
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
    
    def obtener_vendedores(self) -> list[dict]:
        """Obtener todos los vendedores desde el servicio de Usuarios"""
        try:
            url = f"{self.base_url}/vendedores/"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Error obteniendo vendedores: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Error consultando servicio de usuarios para vendedores: {e}")
            return []
    
    def obtener_clientes(self) -> list[dict]:
        """Obtener todos los clientes desde el servicio de Usuarios"""
        try:
            url = f"{self.base_url}/clientes/"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Error obteniendo clientes: {response.status_code}")
                return []
                
        except Exception as e:
            logger.error(f"Error consultando servicio de usuarios para clientes: {e}")
            return []
