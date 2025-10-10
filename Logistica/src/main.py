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

if __name__ == '__main__':
    main()