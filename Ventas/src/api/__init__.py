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
        
        from . import pedidos
        from . import visita
        from . import informes
        app.register_blueprint(pedidos.bp)
        app.register_blueprint(visita.bp)
        app.register_blueprint(informes.bp)


        @app.route("/")
        def root():
            return {
                "status": "up",
                "mode": "simplified",
                "service": "ventas",
                "endpoints": [
                    "POST /ventas/api/visitas/", 
                    "GET /ventas/api/visitas/?estado=pendiente&fecha_inicio=2025-10-13&fecha_fin=2025-10-17&vendedor_id=<id>&page=1&page_size=20",
                    "GET /ventas/api/visitas/vendedor/<vendedor_id>?estado=pendiente&fecha_inicio=2025-10-13&fecha_fin=2025-10-17&page=1&page_size=20",
                    "PUT /ventas/api/visitas/<visita_id>",
                    "POST /ventas/api/pedidos/",
                    "GET /ventas/api/pedidos/?vendedor_id=<id>&cliente_id=<id>&estado=<estado>&page=1&page_size=20",
                    "GET /ventas/api/pedidos/<pedido_id>",
                    "POST /ventas/api/pedidos/<pedido_id>/items",
                    "PUT /ventas/api/pedidos/<pedido_id>/items/<item_id>",
                    "DELETE /ventas/api/pedidos/<pedido_id>/items/<item_id>",
                    "POST /ventas/api/pedidos/<pedido_id>/confirmar",
                    "POST /ventas/api/pedidos/completo",
                    "GET /ventas/api/pedidos/productos/buscar"
                ],
                "pagination": {
                    "default_page": 1,
                    "default_page_size": 20,
                    "max_page_size": 100,
                    "info": "Todos los endpoints GET que retornan listas soportan paginación con parámetros 'page' y 'page_size'"
                }
            }

        @app.route("/health")
        def health():
            return {
                "status": "up",
                "service": "ventas",
                "mode": "simplified"
            }

        @app.route("/ventas/health")
        def ventas_health():
            return {
                "status": "up",
                "service": "ventas",
                "version": "1.0.0",
                "mode": "simplified",
                "endpoints": [
                    "POST /ventas/api/visitas/", 
                    "GET /ventas/api/visitas/?estado=pendiente&fecha_inicio=2025-10-13&fecha_fin=2025-10-17&vendedor_id=<id>",
                    "GET /ventas/api/visitas/vendedor/<vendedor_id>?estado=pendiente&fecha_inicio=2025-10-13&fecha_fin=2025-10-17",
                    "PUT /ventas/api/visitas/<visita_id>",
                    "POST /ventas/api/pedidos/",
                    "GET /ventas/api/pedidos/<pedido_id>",
                    "POST /ventas/api/pedidos/<pedido_id>/items",
                    "PUT /ventas/api/pedidos/<pedido_id>/items/<item_id>",
                    "DELETE /ventas/api/pedidos/<pedido_id>/items/<item_id>",
                    "POST /ventas/api/pedidos/<pedido_id>/confirmar",
                    "POST /ventas/api/pedidos/completo",
                    "GET /ventas/api/pedidos/productos/buscar",
                    "GET /ventas/api/informes/ventas?vendedor_id=<id>&fecha_inicio=2025-10-13&fecha_fin=2025-10-17",

                ]
            }

        logger.info("✅ Aplicación Flask configurada correctamente")
        return app
        
    except Exception as e:
        logger.error(f"❌ Error creando la aplicación: {e}")
        raise

app = create_app()
