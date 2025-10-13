#!/usr/bin/env python3
"""
Punto de entrada principal para el microservicio de Logisitica
"""

import os
import sys
import logging

# Agregar el directorio src al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from api import create_app
# Configurar sistema de eventos
from seedwork.infraestructura.pubsub import PublicadorPubSub
from seedwork.dominio.eventos import despachador_eventos
# Importar consumidores de eventos
from aplicacion.eventos.consumidor_inventario_asignado import ManejadorInventarioAsignado

# Registrar publicador PubSub
publicador_pubsub = PublicadorPubSub()
despachador_eventos.registrar_publicador(publicador_pubsub)
print(" PublicadorPubSub registrado en Logística")

# Configurar consumidor PubSub
from seedwork.infraestructura.consumidor_pubsub import ConsumidorPubSub
import threading

consumidor_pubsub = ConsumidorPubSub()
# Suscribirse al topic de productos-stock-actualizado
consumidor_pubsub.suscribirse_a_topic('productos-stock-actualizado', 'logistica-inventario-subscription')
print(" ConsumidorPubSub configurado en Logística")

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Función para iniciar el consumidor
def iniciar_consumidor():
    try:
        logger.info("🎧 Iniciando consumidor PubSub...")
        logger.info(f" Suscripciones configuradas: {list(consumidor_pubsub._subscriptions.keys())}")
        consumidor_pubsub.iniciar_escucha()
        logger.info(" Consumidor PubSub iniciado exitosamente")
    except Exception as e:
        logger.error(f" Error iniciando consumidor: {e}")
        import traceback
        logger.error(f" Traceback: {traceback.format_exc()}")

print(" ConsumidorPubSub configurado en Logística")

# Iniciar el hilo del consumidor AQUÍ, antes de importar api
logger.info("Creando hilo del consumidor...")
logger.info(f" Suscripciones configuradas: {list(consumidor_pubsub._subscriptions.keys())}")
thread = threading.Thread(target=iniciar_consumidor, daemon=True)
thread.start()
logger.info("Hilo del consumidor creado y iniciado")

print("DEBUG: A punto de definir main()")

def main():
    """Función principal para ejecutar el microservicio"""
    try:
        # Crear la aplicación Flask
        app = create_app()

        # Obtener puerto de variable de entorno o usar 5003 por defecto
        port = int(os.getenv('PORT', 5003))
        host = os.getenv('HOST', '0.0.0.0')

        logger.info(f"Iniciando microservicio de Logistica en {host}:{port}")

        # Ejecutar la aplicación
        app.run(
            host=host,
            port=port,
            debug=False  # En producción debe ser False
        )

    except Exception as e:
        logger.error(f"Error iniciando el microservicio: {e}")
        sys.exit(1)

print("DEBUG: A punto de verificar __name__")
print(f"DEBUG: __name__ = {__name__}")

if __name__ == '__main__':
    print("DEBUG: Llamando a main()")
    main()
else:
    print(f"DEBUG: NO llamando a main(), __name__ = {__name__}")