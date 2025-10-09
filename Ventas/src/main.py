#!/usr/bin/env python3
"""
Punto de entrada principal para el microservicio de Ventas
"""

import os
import sys
import logging

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from api import create_app
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def main():
    """Función principal para ejecutar el microservicio"""
    try:
        app = create_app()
        
        port = int(os.getenv('PORT', 5002))
        host = os.getenv('HOST', '0.0.0.0')
        
        logger.info(f"Iniciando microservicio de Ventas en {host}:{port}")
        
        app.run(
            host=host,
            port=port,
            debug=False
        )
        
    except Exception as e:
        logger.error(f"Error iniciando el microservicio: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
