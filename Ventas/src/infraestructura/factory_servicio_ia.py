"""Factory para crear servicios de IA según configuración"""
import os
import logging
from typing import Optional
from dominio.servicios.servicio_ia import ServicioIA
from infraestructura.proveedores_ia.servicio_vertex_ai import ServicioVertexAI

logger = logging.getLogger(__name__)


def crear_servicio_ia(proveedor: Optional[str] = None) -> ServicioIA:
    """Factory para crear el servicio de IA según configuración
    
    El proveedor se determina por:
    1. Parámetro `proveedor` si se proporciona
    2. Variable de entorno `IA_PROVEEDOR`
    3. Por defecto: 'vertex-ai'
    
    Args:
        proveedor: Nombre del proveedor a usar (opcional)
    
    Returns:
        Instancia del servicio de IA configurado
    
    Raises:
        ValueError: Si el proveedor no está soportado
        RuntimeError: Si hay error al inicializar el servicio
    """
    proveedor_seleccionado = proveedor or os.getenv('IA_PROVEEDOR', 'vertex-ai').lower()
    
    logger.info(f"Creando servicio de IA con proveedor: {proveedor_seleccionado}")
    
    try:
        if proveedor_seleccionado == 'vertex-ai':
            return ServicioVertexAI()
        # Aquí se pueden agregar más proveedores:
        # elif proveedor_seleccionado == 'openai':
        #     return ServicioOpenAI()
        else:
            raise ValueError(
                f"Proveedor de IA no soportado: {proveedor_seleccionado}. "
                f"Proveedores disponibles: vertex-ai"
            )
    except Exception as e:
        logger.error(f"Error creando servicio de IA: {e}")
        raise RuntimeError(f"No se pudo inicializar el servicio de IA: {e}") from e

