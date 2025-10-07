#!/usr/bin/env python3
"""
Punto de entrada principal para el microservicio de Productos
"""

import sys
import os

# Agregar el directorio src al path de Python
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def main():
    """Función principal para ejecutar el microservicio"""
    try:
        print("Iniciando microservicio de Productos...")
        
        # Importar y crear la aplicación
        from api import create_app
        app = create_app()
        
        print("Aplicación Flask creada correctamente")
        print("Servidor iniciado en http://localhost:5000")
        print("Presiona Ctrl+C para detener el servidor")
        print("\n" + "="*50)
        
        # Ejecutar la aplicación
        app.run(debug=True, host='127.0.0.1', port=5000)
        
    except ImportError as e:
        print(f"Error de importación: {e}")
        sys.exit(1)
        
    except Exception as e:
        print(f"Error iniciando la aplicación: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
