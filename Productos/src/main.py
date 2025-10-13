#!/usr/bin/env python3
"""
Punto de entrada principal para el microservicio de Productos
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

# Registrar publicador PubSub
publicador_pubsub = PublicadorPubSub()
despachador_eventos.registrar_publicador(publicador_pubsub)
print("✅ PublicadorPubSub registrado en Productos")

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def main():
    """Función principal para ejecutar el microservicio"""
    try:
        # Crear la aplicación Flask
        app = create_app()
        
        # Obtener puerto de variable de entorno o usar 5000 por defecto
        port = int(os.getenv('PORT', 5000))
        host = os.getenv('HOST', '0.0.0.0')
        
        logger.info(f"Iniciando microservicio de Productos en {host}:{port}")
        
        # Ejecutar la aplicación
        app.run(
            host=host,
            port=port,
            debug=False  # En producción debe ser False
        )
        
    except Exception as e:
        logger.error(f"Error iniciando el microservicio: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
