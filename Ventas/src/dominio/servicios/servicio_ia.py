"""Interfaz abstracta para servicios de IA generativa"""
from abc import ABC, abstractmethod
from typing import Optional, Dict


class ServicioIA(ABC):
    """Interfaz abstracta para servicios de IA generativa
    
    Esta interfaz permite cambiar entre diferentes proveedores de IA
    (Vertex AI, OpenAI, Anthropic, etc.) sin modificar el código de negocio.
    """
    
    @property
    @abstractmethod
    def nombre_proveedor(self) -> str:
        """Nombre del proveedor (ej: 'vertex-ai', 'openai', 'anthropic')
        
        Returns:
            str: Nombre identificador del proveedor
        """
        pass
    
    @property
    @abstractmethod
    def modelo_actual(self) -> str:
        """Nombre del modelo actualmente configurado
        
        Returns:
            str: Nombre del modelo de IA
        """
        pass
    
    @abstractmethod
    def obtener_mime_type(self, formato: str) -> str:
        """Obtiene el MIME type basado en el formato del archivo
        
        Args:
            formato: Extensión del archivo (jpg, png, mp4, etc.)
        
        Returns:
            str: MIME type correspondiente
        """
        pass
    
    @abstractmethod
    def generar_sugerencias(
        self,
        datos_cliente: Dict,
        historial_pedidos: Dict,
        archivo_url: Optional[str] = None,
        mime_type: Optional[str] = None,
        comentarios_evidencia: Optional[str] = None
    ) -> str:
        """Genera sugerencias usando el servicio de IA
        
        Args:
            datos_cliente: Diccionario con datos del cliente (nombre, dirección, teléfono, etc.)
            historial_pedidos: Diccionario con resumen del historial de pedidos
            archivo_url: URL pública del archivo (imagen/video) - opcional
            mime_type: MIME type del archivo - opcional
            comentarios_evidencia: Comentarios asociados a la evidencia - opcional
        
        Returns:
            str: Texto con las sugerencias generadas
        """
        pass
