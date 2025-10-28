"""
Utilidades para paginación de resultados en APIs REST
"""
from typing import List, Dict, Any, TypeVar
from math import ceil

T = TypeVar('T')

def paginar_resultados(
    items: List[T], 
    page: int = 1, 
    page_size: int = 20,
    max_page_size: int = 100
) -> Dict[str, Any]:
    """
    Pagina una lista de items y retorna el resultado con metadatos de paginación.
    
    Args:
        items: Lista completa de items a paginar
        page: Número de página (empieza en 1)
        page_size: Cantidad de items por página
        max_page_size: Tamaño máximo permitido por página
        
    Returns:
        Diccionario con la estructura:
        {
            'items': [...],  # Items de la página actual
            'pagination': {
                'page': 1,
                'page_size': 20,
                'total_items': 100,
                'total_pages': 5,
                'has_next': True,
                'has_prev': False
            }
        }
    
    Examples:
        >>> items = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        >>> result = paginar_resultados(items, page=1, page_size=3)
        >>> result['items']
        [1, 2, 3]
        >>> result['pagination']['total_pages']
        4
    """
    # Validar y ajustar page
    if page < 1:
        page = 1
    
    # Validar y ajustar page_size
    if page_size < 1:
        page_size = 20
    if page_size > max_page_size:
        page_size = max_page_size
    
    # Calcular totales
    total_items = len(items)
    total_pages = ceil(total_items / page_size) if total_items > 0 else 1
    
    # Ajustar page si excede el total
    if page > total_pages:
        page = total_pages
    
    # Calcular índices
    start_index = (page - 1) * page_size
    end_index = start_index + page_size
    
    # Obtener items de la página actual
    paginated_items = items[start_index:end_index]
    
    return {
        'items': paginated_items,
        'pagination': {
            'page': page,
            'page_size': page_size,
            'total_items': total_items,
            'total_pages': total_pages,
            'has_next': page < total_pages,
            'has_prev': page > 1
        }
    }


def extraer_parametros_paginacion(request_args: dict) -> tuple[int, int]:
    """
    Extrae y valida los parámetros de paginación de los argumentos del request.
    
    Args:
        request_args: Diccionario con los argumentos del request (request.args)
        
    Returns:
        Tupla (page, page_size) con valores validados
        
    Examples:
        >>> from flask import request
        >>> page, page_size = extraer_parametros_paginacion(request.args)
    """
    try:
        page = int(request_args.get('page', 1))
    except (ValueError, TypeError):
        page = 1
    
    try:
        page_size = int(request_args.get('page_size', 20))
    except (ValueError, TypeError):
        page_size = 20
    
    return page, page_size

