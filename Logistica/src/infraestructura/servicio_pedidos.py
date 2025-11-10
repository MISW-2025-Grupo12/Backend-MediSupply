import logging
import os
import random
import uuid
import requests

logger = logging.getLogger(__name__)


class ServicioPedidos:
    def __init__(self):
        self.base_url = os.getenv('VENTAS_SERVICE_URL', 'http://ventas:5002/ventas/api')

    def obtener_pedido_por_id(self, pedido_id: str) -> dict | None:
        try:
            url = f"{self.base_url}/pedidos/{pedido_id}"
            response = requests.get(url, timeout=5)

            if response.status_code == 200:
                return response.json()
            if response.status_code == 404:
                logger.warning(f"Pedido {pedido_id} no encontrado en Ventas")
                return None

            logger.error(f"Error obteniendo pedido {pedido_id} en Ventas: {response.status_code}")
            return None
        except Exception as error:
            logger.error(f"Error consultando Ventas para pedido {pedido_id}: {error}")
            return None


def obtener_pedido_random():
    """Genera un pedido simulado (mock) para las pruebas locales."""
    try:
        pedido_id = str(uuid.uuid4())
        productos = [
            {
                "nombre": "Paracetamol",
                "cantidad": random.randint(1, 4),
                "precio_unitario": 8000,
                "subtotal": 8000 * random.randint(1, 4),
                "avatar": "https://via.placeholder.com/64?text=P1"
            },
            {
                "nombre": "Ibuprofeno",
                "cantidad": random.randint(1, 3),
                "precio_unitario": 10000,
                "subtotal": 10000 * random.randint(1, 3),
                "avatar": "https://via.placeholder.com/64?text=P2"
            }
        ]

        pedido = {
            "id": pedido_id,
            "cliente": {
                "nombre": "Cliente Mock",
                "telefono": "3000000000",
                "direccion": "Calle 45 # 12-34",
                "avatar": "https://via.placeholder.com/64?text=C"
            },
            "productos": productos
        }

        logger.info(f"✅ Pedido mock generado: {pedido_id}")
        return pedido

    except Exception as e:
        logger.error(f"Error generando pedido mock: {e}")
        return None
