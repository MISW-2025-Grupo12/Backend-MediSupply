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
        
        # Detectar si estamos en modo de pruebas
        is_testing = os.getenv('TESTING') == 'True' or 'pytest' in sys.modules
        
        if is_testing:
            # Usar SQLite para pruebas
            import tempfile
            db_fd, db_path = tempfile.mkstemp()
            database_uri = f'sqlite:///{db_path}'
            app.config['TESTING'] = True
            logger.info("Modo de pruebas detectado - usando SQLite")
        else:
            # Usar PostgreSQL para producción
            database_uri = os.getenv('SQLALCHEMY_DATABASE_URI', 'postgresql://usuarios_user:usuarios_pass@usuarios-db:5432/usuarios_db')
            logger.info("Modo de producción - usando PostgreSQL")
        
        app.config['SQLALCHEMY_DATABASE_URI'] = database_uri
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        
        from config.db import init_db
        init_db(app)
        logger.info("Base de datos inicializada")
        
        from . import proveedor
        from . import vendedor
        from . import cliente
        app.register_blueprint(proveedor.bp)
        app.register_blueprint(vendedor.bp)
        app.register_blueprint(cliente.bp)
        
        @app.route("/")
        def root():
            return {
                "status": "up",
                "mode": "simplified",
                "service": "usuarios",
                "endpoints": [
                    "POST /api/proveedores/", 
                    "GET /api/proveedores/",
                    "POST /api/vendedores/", 
                    "GET /api/vendedores/",
                    "GET /api/vendedores/<id>",
                    "POST /api/clientes/", 
                    "GET /api/clientes/",
                    "GET /api/clientes/<id>"
                ]
            }

        @app.route("/health")
        def health():
            return {
                "status": "up",
                "service": "usuarios",
                "mode": "simplified"
            }

        @app.route("/usuarios/health")
        def usuarios_health():
            return {
                "status": "up",
                "service": "usuarios",
                "version": "1.0.0",
                "mode": "simplified",
                "endpoints": [
                    "POST /usuarios/api/proveedores/", 
                    "GET /usuarios/api/proveedores/",
                    "POST /usuarios/api/vendedores/", 
                    "GET /usuarios/api/vendedores/",
                    "GET /usuarios/api/vendedores/<id>",
                    "POST /usuarios/api/clientes/", 
                    "GET /usuarios/api/clientes/",
                    "GET /usuarios/api/clientes/<id>"
                ]
            }
        
        logger.info("Aplicación Flask configurada correctamente")
        return app
    except Exception as e:
        logger.error(f"Error creando la aplicación: {e}")
        raise

app = create_app()
