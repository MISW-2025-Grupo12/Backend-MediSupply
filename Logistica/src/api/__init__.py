import os
import sys
import logging

# Agregar el directorio src al path de Python para que las importaciones funcionen
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, jsonify
from flask_swagger import swagger

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app(configuracion=None):
    try:
        # Crear la aplicación Flask
        app = Flask(__name__, instance_relative_config=True)
        logger.info("🚀 Aplicación Flask creada")

        # Configurar Flask para no redirigir automáticamente URLs sin barra final
        app.url_map.strict_slashes = False

        # Configurar base de datos (PostgreSQL en Docker, SQLite en desarrollo)
        database_uri = os.getenv('SQLALCHEMY_DATABASE_URI', 'sqlite:///logistica.db')
        app.config['SQLALCHEMY_DATABASE_URI'] = database_uri
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

        # Inicializar base de datos
        from config.db import init_db
        init_db(app)
        logger.info("✅ Base de datos inicializada")

        # Importar Blueprints del servicio
        #from api.entregas import bp as entrega_bp
        from . import entregas


        # Registrar Blueprints
        #app.register_blueprint(entrega_bp)
        app.register_blueprint(entregas.bp)

        # Endpoint de documentación Swagger
        @app.route("/spec")
        def spec():
            swag = swagger(app)
            swag['info']['version'] = "1.0"
            swag['info']['title'] = "Logística API"
            return jsonify(swag)

        # Endpoint de verificación de estado
        @app.route("/health")
        def health():
            return {
                "status": "up",
                "service": "logistica",
                "endpoints": [
                    "GET /entregas-programadas",
                    "GET /spec",
                    "GET /health"
                ]
            }, 200

        logger.info("✅ Aplicación Flask de Logística configurada correctamente")
        return app

    except Exception as e:
        logger.error(f"❌ Error creando la aplicación de Logística: {e}")
        raise

# Instancia global usada por Flask
app = create_app()