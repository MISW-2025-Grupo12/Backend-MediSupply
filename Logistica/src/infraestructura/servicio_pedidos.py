import random
import logging
import uuid

logger = logging.getLogger(__name__)

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
