import os
import sys
import logging

# Agregar el directorio src al path de Python para que las importaciones funcionen
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, jsonify

# Configurar logging para pruebas
logging.basicConfig(level=logging.WARNING)  # Reducir logs en pruebas

def create_test_app():
    """Crear aplicación Flask para pruebas sin consumidor PubSub"""
    try:
        # Crear la aplicación Flask
        app = Flask(__name__, instance_relative_config=True)

        # Configurar Flask para no redirigir automáticamente URLs sin barra final
        app.url_map.strict_slashes = False

        # Configurar base de datos de prueba (SQLite en memoria)
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        app.config['TESTING'] = True

        # Inicializar base de datos de prueba
        from config.test_db import init_test_db
        init_test_db(app)

        # Importar Blueprints del servicio
        from . import entregas
        from . import inventario

        # Registrar Blueprints
        app.register_blueprint(entregas.bp)
        app.register_blueprint(inventario.bp)

        # Endpoint de verificación de estado
        @app.route("/health")
        def health():
            return {
                "status": "up",
                "service": "logistica",
                "endpoints": [
                    "GET /entregas-programadas",
                    "GET /api/inventario",
                    "GET /api/inventario/buscar",
                    "POST /api/inventario/reservar",
                    "POST /api/inventario/descontar",
                    "GET /api/inventario/producto/<id>",
                    "GET /spec",
                    "GET /health"
                ]
            }, 200

        return app

    except Exception as e:
        raise Exception(f"Error creando aplicación de prueba: {e}")
