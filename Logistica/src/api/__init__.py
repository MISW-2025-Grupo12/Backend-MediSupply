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

# Variable global para el consumidor PubSub (se inicializa después de crear la app Flask)
consumidor_pubsub = None

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
        from . import bodegas
        from . import rutas

        # Registrar Blueprints
        app.register_blueprint(entregas.bp)
        app.register_blueprint(inventario.bp)
        app.register_blueprint(bodegas.bp)
        app.register_blueprint(rutas.bp)
        
        # Importar consumidores de eventos
        print("🔔 Importando consumidores de eventos...")
        from aplicacion.eventos.consumidor_pedido_confirmado import manejador
        print("✅ ManejadorPedidoConfirmado importado")
        from aplicacion.eventos.consumidor_pedido_entregado import manejador as manejador_entregado
        print("✅ ManejadorPedidoEntregado importado")
        from aplicacion.eventos.consumidor_pedido_estado_actualizado import manejador as manejador_estado_actualizado
        print("✅ ManejadorPedidoEstadoActualizado importado")

        # Endpoint de verificación de estado
        @app.route("/")
        def root():
            return {
                "status": "up",
                "mode": "simplified",
                "service": "logistica",
                "endpoints": [
                    "GET /logistica/api/entregas/",
                    "GET /logistica/api/inventario/",
                    "GET /logistica/api/inventario/buscar",
                    "POST /logistica/api/inventario/reservar",
                    "POST /logistica/api/inventario/descontar",
                    "GET /logistica/api/inventario/producto/<id>",
                    "GET /logistica/api/inventario/stream",
                    "GET /logistica/api/inventario/stream/test",
                    "POST /logistica/api/entregas/creartemp",
                    "GET /logistica/api/bodegas/",
                    "POST /logistica/api/bodegas/inicializar",
                    "GET /logistica/api/bodegas/<id>/productos",
                    "GET /logistica/api/bodegas/producto/<id>/ubicaciones",
                    "POST /logistica/api/rutas/",
                    "GET /logistica/api/rutas/",
                    "GET /logistica/api/rutas/repartidor/<id>"
                ]
            }

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
                    "GET /logistica/api/inventario/stream",
                    "GET /logistica/api/inventario/stream/test",
                    "GET /logistica/api/bodegas/",
                    "POST /logistica/api/bodegas/inicializar",
                    "GET /logistica/api/bodegas/<id>/productos",
                    "GET /logistica/api/bodegas/producto/<id>/ubicaciones",
                    "POST /logistica/api/rutas/",
                    "GET /logistica/api/rutas/",
                    "GET /logistica/api/rutas/repartidor/<id>",
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

# Configurar consumidor PubSub DESPUÉS de crear la app Flask para tener contexto
try:
    from seedwork.infraestructura.consumidor_pubsub import ConsumidorPubSub
    
    logger.info("Configurando consumidor PubSub en api/__init__.py...")
    
    # Crear consumidor
    consumidor_pubsub = ConsumidorPubSub()
    
    # Suscribirse al topic de productos-stock-actualizado (para InventarioAsignado)
    consumidor_pubsub.suscribirse_a_topic('productos-stock-actualizado', 'logistica-inventario-subscription')
    logger.info("✅ Consumidor suscrito al topic productos-stock-actualizado")

    # Suscribirse al topic de pedidos-confirmados (para PedidoConfirmado - reserva + crear entrega)
    consumidor_pubsub.suscribirse_a_topic('pedidos-confirmados', 'logistica-pedidos-confirmados-subscription')
    logger.info("✅ Consumidor suscrito al topic pedidos-confirmados")
    
    # Pasar la app Flask al consumidor para tener contexto cuando procese eventos
    consumidor_pubsub.app = app
    logger.info("✅ Consumidor PubSub actualizado con contexto de Flask")
    
    # Función para iniciar el consumidor
    def iniciar_consumidor():
        try:
            logger.info("🎧 Iniciando escucha del consumidor PubSub...")
            logger.info(f"Suscripciones configuradas: {list(consumidor_pubsub._subscriptions.keys())}")
            consumidor_pubsub.iniciar_escucha()
        except Exception as e:
            logger.error(f"Error en consumidor: {e}")
            import traceback
            logger.error(traceback.format_exc())
    
    # Iniciar el hilo del consumidor
    logger.info("Creando hilo del consumidor...")
    thread = threading.Thread(target=iniciar_consumidor, daemon=True)
    thread.start()
    logger.info("✅ Hilo del consumidor creado y iniciado")
    
except Exception as e:
    logger.error(f"❌ Error configurando consumidor PubSub: {e}")
    import traceback
    logger.error(traceback.format_exc())