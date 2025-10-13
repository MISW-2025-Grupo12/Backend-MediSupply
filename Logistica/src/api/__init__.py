import os
import sys
import logging
import threading

# Agregar el directorio src al path de Python para que las importaciones funcionen
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, jsonify
from flask_swagger import swagger

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Iniciar consumidor PubSub ANTES de crear Flask
print("DEBUG: Antes del try del consumidor")
try:
    print("DEBUG: Dentro del try del consumidor")
    from seedwork.infraestructura.consumidor_pubsub import ConsumidorPubSub
    from seedwork.dominio.eventos import despachador_eventos
    print("DEBUG: Imports exitosos")
    
    logger.info("Iniciando configuración de consumidor PubSub en api/__init__.py...")
    
    # Crear consumidor
    consumidor_pubsub = ConsumidorPubSub()
    
    # Suscribirse al topic de productos-stock-actualizado
    consumidor_pubsub.suscribirse_a_topic('productos-stock-actualizado', 'logistica-inventario-subscription')
    logger.info("Consumidor suscrito al topic productos-stock-actualizado")
    
    # Función para iniciar el consumidor
    def iniciar_consumidor():
        try:
            logger.info("Iniciando escucha del consumidor PubSub...")
            logger.info(f"Suscripciones: {list(consumidor_pubsub._subscriptions.keys())}")
            consumidor_pubsub.iniciar_escucha()
        except Exception as e:
            logger.error(f"Error en consumidor: {e}")
            import traceback
            logger.error(traceback.format_exc())
    
    # Iniciar el hilo del consumidor
    logger.info("Creando hilo del consumidor...")
    thread = threading.Thread(target=iniciar_consumidor, daemon=True)
    thread.start()
    logger.info("Hilo del consumidor creado y iniciado")
    
except Exception as e:
    logger.error(f"Error configurando consumidor PubSub: {e}")
    import traceback
    logger.error(traceback.format_exc())

def create_app(configuracion=None):
    try:
        # Crear la aplicación Flask
        app = Flask(__name__, instance_relative_config=True)
        logger.info("🚀 Aplicación Flask creada")

        # Configurar Flask para no redirigir automáticamente URLs sin barra final
        app.url_map.strict_slashes = False

        # Configurar base de datos (PostgreSQL en Docker, SQLite en desarrollo/pruebas)
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
            database_uri = os.getenv('SQLALCHEMY_DATABASE_URI', 'postgresql://logistica_user:logistica_pass@logistica-db:5432/logistica_db')
            logger.info("Modo de producción - usando PostgreSQL")
        
        app.config['SQLALCHEMY_DATABASE_URI'] = database_uri
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

        # Inicializar base de datos
        from config.db import init_db
        init_db(app)
        logger.info("✅ Base de datos inicializada")

        # Importar Blueprints del servicio
        from . import entregas
        from . import inventario

        # Registrar Blueprints
        app.register_blueprint(entregas.bp)
        app.register_blueprint(inventario.bp)
        
        # Importar consumidores de eventos
        from aplicacion.eventos.consumidor_pedido_confirmado import manejador

        # Endpoint de verificación de estado
        @app.route("/")
        def root():
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

        @app.route("/health")
        def health():
            return {
                "status": "up",
                "service": "logistica",
                "mode": "simplified"
            }

        @app.route("/logistica/health")
        def logistica_health():
            return {
                "status": "up",
                "service": "logistica",
                "version": "1.0.0",
                "mode": "simplified",
                "endpoints": [
                    "GET /logistica/api/entregas-programadas",
                    "GET /logistica/api/inventario",
                    "GET /logistica/api/inventario/buscar",
                    "POST /logistica/api/inventario/reservar",
                    "POST /logistica/api/inventario/descontar",
                    "GET /logistica/api/inventario/producto/<id>",
                    "GET /logistica/spec",
                    "GET /logistica/health"
                ]
            }

        logger.info("✅ Aplicación Flask de Logística configurada correctamente")
        return app

    except Exception as e:
        logger.error(f"❌ Error creando la aplicación de Logística: {e}")
        raise

# Instancia global usada por Flask
app = create_app()