"""
Manager de clientes SSE para gestionar conexiones activas
"""
import threading
import queue
import logging
from typing import Set, Dict, Any
import json

logger = logging.getLogger(__name__)

class SSEClientManager:
    """Manager thread-safe para gestionar clientes SSE conectados"""
    
    def __init__(self):
        self._clients: Set[queue.Queue] = set()
        self._lock = threading.Lock()
    
    def agregar_cliente(self, client_queue: queue.Queue) -> None:
        """Agrega un cliente SSE a la lista de clientes conectados"""
        with self._lock:
            self._clients.add(client_queue)
            logger.info(f"Cliente SSE agregado. Total clientes: {len(self._clients)}")
    
    def remover_cliente(self, client_queue: queue.Queue) -> None:
        """Remueve un cliente SSE de la lista"""
        with self._lock:
            if client_queue in self._clients:
                self._clients.remove(client_queue)
                logger.info(f"Cliente SSE removido. Total clientes: {len(self._clients)}")
    
    def notificar_todos(self, event_type: str, data: Dict[str, Any]) -> None:
        """Notifica a todos los clientes SSE conectados con un evento"""
        message = f"event: {event_type}\ndata: {json.dumps(data)}\n\n"
        
        with self._lock:
            disconnected_clients = set()
            
            for client_queue in self._clients:
                try:
                    client_queue.put_nowait(message)
                except queue.Full:
                    logger.warning("Cola de cliente SSE llena, cliente desconectado")
                    disconnected_clients.add(client_queue)
                except Exception as e:
                    logger.error(f"Error enviando mensaje a cliente SSE: {e}")
                    disconnected_clients.add(client_queue)
            
            # Remover clientes desconectados
            for client_queue in disconnected_clients:
                self._clients.discard(client_queue)
        
        if len(self._clients) > 0:
            logger.debug(f"Notificados {len(self._clients)} clientes SSE con evento {event_type}")
    
    def obtener_cantidad_clientes(self) -> int:
        """Retorna la cantidad de clientes SSE conectados"""
        with self._lock:
            return len(self._clients)
    
    def obtener_clientes(self) -> Set[queue.Queue]:
        """Retorna una copia del conjunto de clientes conectados (para debugging)"""
        with self._lock:
            return self._clients.copy()

# Instancia global del manager
sse_client_manager = SSEClientManager()

