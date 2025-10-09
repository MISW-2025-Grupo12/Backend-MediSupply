import os
import sys
import logging

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, jsonify
from flask_swagger import swagger
from flask_cors import CORS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app(configuracion=None):
    try:
        app = Flask(__name__, instance_relative_config=True)
        CORS(app)
        logger.info("Aplicación Flask creada")

        app.url_map.strict_slashes = False
        database_uri = os.getenv('SQLALCHEMY_DATABASE_URI', 'sqlite:///productos.db')
        app.config['SQLALCHEMY_DATABASE_URI'] = database_uri
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        
        from config.db import init_db
        init_db(app)
        logger.info("✅ Base de datos inicializada")
        
        from . import producto
        from . import categoria
        app.register_blueprint(producto.bp)
        app.register_blueprint(categoria.bp)

        @app.route("/spec")
        def spec():
            swag = swagger(app)
            swag['info']['version'] = "1.0"
            swag['info']['title'] = "Productos API"
            return jsonify(swag)

        @app.route("/health")
        def health():
            return {
                "status": "up",
                "mode": "simplified",
                "endpoints": [
                    "POST /api/productos/", 
                    "GET /api/productos/",
                    "POST /api/productos/categorias/",
                    "GET /api/productos/categorias/"
                ]
            }

        logger.info("✅ Aplicación Flask configurada correctamente")
        return app
        
    except Exception as e:
        logger.error(f"❌ Error creando la aplicación: {e}")
        raise

app = create_app()