"""
Servicio de validación para pedidos usando reglas de negocio
"""
from typing import List, Dict, Tuple, Optional
from dominio.reglas import (
    PedidoDebeTenerVendedor,
    PedidoDebeTenerCliente,
    PedidoDebeTenerItems,
    ItemsDebenSerLista,
    ItemDebeSerDiccionario,
    ItemPedidoDebeTenerProductoId,
    ItemPedidoDebeTenerCantidadPositiva,
    PedidoDebeEstarEnEstadoBorrador
)
from seedwork.dominio.reglas import ReglaNegocio
import logging

logger = logging.getLogger(__name__)

class ValidadorPedidos:
    """Servicio para validar pedidos usando reglas de negocio"""
    
    @staticmethod
    def validar_datos_basicos_pedido(vendedor_id: str, cliente_id: str) -> Tuple[bool, Optional[str]]:
        """Valida los datos básicos de un pedido"""
        reglas = [
            PedidoDebeTenerVendedor(vendedor_id),
            PedidoDebeTenerCliente(cliente_id)
        ]
        
        for regla in reglas:
            if not regla.es_valido():
                return False, f"Error de validación: {regla.__class__.__name__}"
        
        return True, None
    
    @staticmethod
    def validar_estructura_items(items_data: any) -> Tuple[bool, Optional[str], List[Dict]]:
        """Valida la estructura de los items del pedido"""
        # Validar que items sea una lista
        if not ItemsDebenSerLista(items_data).es_valido():
            return False, "items debe ser una lista con al menos un item", []
        
        # Validar que la lista no esté vacía
        if not PedidoDebeTenerItems(items_data).es_valido():
            return False, "El pedido debe tener al menos un item", []
        
        items_validados = []
        
        # Validar cada item
        for i, item_data in enumerate(items_data):
            # Validar que sea un diccionario
            if not ItemDebeSerDiccionario(item_data).es_valido():
                return False, f"Item {i+1} debe ser un objeto JSON", []
            
            # Extraer datos del item
            producto_id = item_data.get('producto_id', '').strip() if isinstance(item_data.get('producto_id'), str) else ''
            cantidad = item_data.get('cantidad', 0)
            
            # Validar producto_id
            if not ItemPedidoDebeTenerProductoId(producto_id).es_valido():
                return False, f"Item {i+1}: producto_id es obligatorio", []
            
            # Validar cantidad
            if not ItemPedidoDebeTenerCantidadPositiva(cantidad).es_valido():
                return False, f"Item {i+1}: cantidad debe ser mayor a 0", []
            
            items_validados.append({
                'producto_id': producto_id,
                'cantidad': cantidad
            })
        
        return True, None, items_validados
    
    @staticmethod
    def validar_estado_pedido(estado: str) -> Tuple[bool, Optional[str]]:
        """Valida el estado de un pedido"""
        if not PedidoDebeEstarEnEstadoBorrador(estado).es_valido():
            return False, "Solo se pueden modificar pedidos en estado borrador"
        
        return True, None
    
    @staticmethod
    def validar_pedido_completo(vendedor_id: str, cliente_id: str, items_data: any) -> Tuple[bool, Optional[str], List[Dict]]:
        """Validación completa de un pedido"""
        # Validar datos básicos
        es_valido, error = ValidadorPedidos.validar_datos_basicos_pedido(vendedor_id, cliente_id)
        if not es_valido:
            return False, error, []
        
        # Validar estructura de items
        es_valido, error, items_validados = ValidadorPedidos.validar_estructura_items(items_data)
        if not es_valido:
            return False, error, []
        
        return True, None, items_validados

class ValidadorItemsPedido:
    """Servicio específico para validar items de pedido"""
    
    @staticmethod
    def validar_item_individual(item_data: Dict, indice: int) -> Tuple[bool, Optional[str]]:
        """Valida un item individual del pedido"""
        if not isinstance(item_data, dict):
            return False, f"Item {indice+1} debe ser un objeto JSON"
        
        producto_id = item_data.get('producto_id', '').strip() if isinstance(item_data.get('producto_id'), str) else ''
        cantidad = item_data.get('cantidad', 0)
        
        # Validar producto_id
        if not ItemPedidoDebeTenerProductoId(producto_id).es_valido():
            return False, f"Item {indice+1}: producto_id es obligatorio"
        
        # Validar cantidad
        if not ItemPedidoDebeTenerCantidadPositiva(cantidad).es_valido():
            return False, f"Item {indice+1}: cantidad debe ser mayor a 0"
        
        return True, None
    
    @staticmethod
    def validar_lista_items(items_data: List[Dict]) -> Tuple[bool, Optional[str], List[Dict]]:
        """Valida una lista completa de items"""
        if not isinstance(items_data, list):
            return False, "items debe ser una lista", []
        
        if len(items_data) == 0:
            return False, "El pedido debe tener al menos un item", []
        
        items_validados = []
        
        for i, item_data in enumerate(items_data):
            es_valido, error = ValidadorItemsPedido.validar_item_individual(item_data, i)
            if not es_valido:
                return False, error, []
            
            items_validados.append({
                'producto_id': item_data.get('producto_id', '').strip(),
                'cantidad': item_data.get('cantidad', 0)
            })
        
        return True, None, items_validados