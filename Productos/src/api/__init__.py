import os
import sys
import logging

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, jsonify
from flask_swagger import swagger

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app(configuracion=None):
    try:
        app = Flask(__name__, instance_relative_config=True)
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
        
        # Iniciar JobsManager para procesar trabajos asíncronos
        from infraestructura.jobs_manager import get_jobs_manager
        jobs_manager = get_jobs_manager(app)
        # get_jobs_manager ya inicia el manager si se pasa app
        logger.info("✅ JobsManager iniciado para carga masiva")


        @app.route("/")
        def root():
            return {
                "status": "up",
                "mode": "simplified",
                "service": "productos",
                "endpoints": [
                    "POST /productos/api/productos/", 
                    "GET /productos/api/productos/",
                    "GET /productos/api/productos/<id>",
                    "POST /productos/api/categorias/",
                    "GET /productos/api/categorias/"
                ]
            }

        @app.route("/health")
        def health():
            return {
                "status": "up",
                "service": "productos",
                "mode": "simplified"
            }

        @app.route("/productos/health")
        def productos_health():
            return {
                "status": "up",
                "service": "productos",
                "version": "1.0.0",
                "mode": "simplified",
                "endpoints": [
                    "POST /productos/api/productos/", 
                    "GET /productos/api/productos/",
                    "GET /productos/api/productos/<id>",
                    "POST /productos/api/categorias/",
                    "GET /productos/api/categorias/"
                ]
            }

        logger.info("✅ Aplicación Flask configurada correctamente")
        return app
        
    except Exception as e:
        logger.error(f"❌ Error creando la aplicación: {e}")
        raise

app = create_app()