import requests
import logging
import os
import re

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
    
    def obtener_proveedor_por_nombre(self, nombre: str) -> dict:
        """Obtiene un proveedor por nombre (comparación normalizada)"""
        try:
            nombre_normalizado = self._normalizar_nombre(nombre)
            
            # Obtener todos los proveedores (puede requerir múltiples requests si hay paginación)
            page = 1
            page_size = 100  # Tamaño de página razonable
            
            while True:
                response = requests.get(f"{self.base_url}/proveedores", params={'page': page, 'page_size': page_size})
                if response.status_code != 200:
                    logger.error(f"Error consultando proveedores: {response.status_code}")
                    return None
                
                proveedores_data = response.json()
                # Si la respuesta tiene paginación, obtener los datos
                if isinstance(proveedores_data, dict) and 'items' in proveedores_data:
                    # Formato paginado: {'items': [...], 'pagination': {...}}
                    proveedores = proveedores_data['items']
                    pagination = proveedores_data.get('pagination', {})
                    total_pages = pagination.get('total_pages', 1)
                elif isinstance(proveedores_data, dict) and 'data' in proveedores_data:
                    # Formato alternativo con 'data'
                    proveedores = proveedores_data['data']
                    total_pages = proveedores_data.get('total_pages', 1)
                elif isinstance(proveedores_data, list):
                    # Formato simple de lista
                    proveedores = proveedores_data
                    total_pages = 1
                else:
                    logger.error(f"Formato de respuesta inesperado: {type(proveedores_data)}. Contenido: {proveedores_data}")
                    return None
                
                # Buscar proveedor por nombre normalizado en esta página
                for proveedor in proveedores:
                    if self._normalizar_nombre(proveedor.get('nombre', '')) == nombre_normalizado:
                        return proveedor
                
                # Si no se encontró y hay más páginas, continuar
                if page >= total_pages:
                    break
                page += 1
            
            return None
        except Exception as e:
            logger.error(f"Error obteniendo proveedor por nombre {nombre}: {e}")
            return None
    
    def validar_proveedor_existe(self, proveedor_id: str) -> bool:
        """Valida que un proveedor existe"""
        proveedor = self.obtener_proveedor_por_id(proveedor_id)
        return proveedor is not None
    
    def obtener_proveedor(self, proveedor_id: str) -> dict:
        """Obtiene los datos de un proveedor específico"""
        return self.obtener_proveedor_por_id(proveedor_id)
    
    def _normalizar_nombre(self, nombre: str) -> str:
        """Normaliza un nombre para comparación: lowercase, sin espacios y sin puntuación"""
        if not nombre:
            return ""
        nombre_normalizado = nombre.lower().strip()
        nombre_normalizado = re.sub(r'\s+', '', nombre_normalizado)
        nombre_normalizado = re.sub(r'[.,;:!?\-_()\[\]{}]', '', nombre_normalizado)
        return nombre_normalizado
