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
        
        # Pruebas
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
            database_uri = os.getenv('SQLALCHEMY_DATABASE_URI', 'postgresql://ventas_user:ventas_pass@ventas-db:5432/ventas_db')
            logger.info("Modo de producción - usando PostgreSQL")
        
        app.config['SQLALCHEMY_DATABASE_URI'] = database_uri
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        
        from config.db import init_db
        init_db(app)
        logger.info("✅ Base de datos inicializada")
        
        from . import visita
        from . import pedidos
        app.register_blueprint(visita.bp)
        app.register_blueprint(pedidos.bp)

        @app.route("/spec")
        def spec():
            swag = swagger(app)
            swag['info']['version'] = "1.0"
            swag['info']['title'] = "Ventas API"
            return jsonify(swag)

        @app.route("/health")
        def health():
            return {
                "status": "up",
                "mode": "simplified",
                "endpoints": [
                    "POST /api/visitas/", 
                    "GET /api/visitas/?estado=pendiente",
                    "GET /api/visitas/vendedor/<vendedor_id>?estado=pendiente",
                    "PUT /api/visitas/<visita_id>",
                    "POST /api/pedidos/",
                    "GET /api/pedidos/<pedido_id>",
                    "POST /api/pedidos/<pedido_id>/items",
                    "PUT /api/pedidos/<pedido_id>/items/<item_id>",
                    "DELETE /api/pedidos/<pedido_id>/items/<item_id>",
                    "POST /api/pedidos/<pedido_id>/confirmar",
                    "GET /api/pedidos/productos/buscar"
                ]
            }

        logger.info("✅ Aplicación Flask configurada correctamente")
        return app
        
    except Exception as e:
        logger.error(f"❌ Error creando la aplicación: {e}")
        raise

app = create_app()
