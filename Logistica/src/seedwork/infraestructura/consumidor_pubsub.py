"""
Consumidor de eventos para Google Cloud Pub/Sub
"""

import json
import logging
import threading
import time
import os
from typing import Dict, Any
from google.cloud import pubsub_v1
from google.auth.exceptions import DefaultCredentialsError
from seedwork.dominio.eventos import EventoDominio, despachador_eventos
from seedwork.aplicacion.eventos import ejecutar_evento

logger = logging.getLogger(__name__)

class ConsumidorPubSub:
    """Consumidor de eventos que recibe mensajes de Google Cloud Pub/Sub"""
    
    def __init__(self, project_id: str = None, emulator_host: str = None, app=None):
                
        self.project_id = project_id or os.getenv('GCP_PROJECT_ID', 'medisupply-project')
        self.use_emulator = os.getenv('USE_PUBSUB_EMULATOR', 'false').lower() == 'true'
        self.emulator_host = emulator_host or os.getenv('PUBSUB_EMULATOR_HOST', 'localhost:8085')
        
        self.app = app
        self._subscriber = None
        self._subscriptions = {}
        self._initialize_subscriber()
    
    def _initialize_subscriber(self):
        """Inicializa el cliente de Pub/Sub"""
        try:
            if self.use_emulator:
                # Configurar para usar el emulador
                os.environ['PUBSUB_EMULATOR_HOST'] = self.emulator_host
                logger.info(f"Consumidor Pub/Sub inicializado con emulador en {self.emulator_host}")
            else:
                # Configurar para usar GCP
                self._setup_gcp_authentication()
                logger.info(f"Consumidor Pub/Sub inicializado para GCP proyecto: {self.project_id}")
            
            self._subscriber = pubsub_v1.SubscriberClient()
            
        except Exception as e:
            logger.warning(f"No se pudo inicializar consumidor Pub/Sub: {e}")
            self._subscriber = None
    
    def _setup_gcp_authentication(self):
        """Configura la autenticación para GCP"""
        # Verificar si ya hay credenciales configuradas
        if os.getenv('GOOGLE_APPLICATION_CREDENTIALS'):
            logger.info("Usando credenciales desde GOOGLE_APPLICATION_CREDENTIALS")
            return
        
        service_account_key = os.getenv('GCP_SERVICE_ACCOUNT_KEY')
        if service_account_key:
            try:
                import json
                import tempfile
                
                json.loads(service_account_key)
                
                with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                    f.write(service_account_key)
                    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = f.name
                    logger.info("Credenciales de GCP configuradas desde variable de entorno")
                    
            except json.JSONDecodeError:
                logger.warning("GCP_SERVICE_ACCOUNT_KEY no es un JSON válido")
            except Exception as e:
                logger.warning(f"Error configurando credenciales de GCP: {e}")
        else:
            # Usar Application Default Credentials (ADC)
            logger.info("Usando Application Default Credentials (ADC) para GCP")
    
    def crear_suscripciones(self):
        """Crea las suscripciones necesarias para escuchar eventos"""
        if not self._subscriber:
            logger.warning("No se puede crear suscripciones: cliente no inicializado")
            return
        
        # Topics de escucha
        topics_a_escuchar = [
            'pedidos-creados',
            'inventarioasignado'
        ]
        
        for topic_name in topics_a_escuchar:
            try:
                self._crear_suscripcion(topic_name)
            except Exception as e:
                logger.warning(f"Error creando suscripción para {topic_name}: {e}")
    
    def suscribirse_a_topic(self, topic_name: str, subscription_name: str):
        """Crea una suscripción a un topic y comienza a escuchar mensajes"""
        if not self._subscriber:
            logger.error("Consumidor Pub/Sub no inicializado, no se puede suscribir.")
            return

        topic_path = self._subscriber.topic_path(self.project_id, topic_name)
        subscription_path = self._subscriber.subscription_path(self.project_id, subscription_name)

        # Validar que el topic existe
        try:
            from google.cloud import pubsub_v1
            publisher = pubsub_v1.PublisherClient()
            publisher.create_topic(request={"name": topic_path})
            logger.info(f"Topic '{topic_name}' creado exitosamente.")
        except Exception as e:
            if "already exists" in str(e).lower() or "409" in str(e):
                logger.info(f"Topic '{topic_name}' ya existe.")
            else:
                logger.warning(f"Error creando topic '{topic_name}': {e}")

        try:
            # Intentar obtener la suscripción para ver si ya existe
            self._subscriber.get_subscription(request={"subscription": subscription_path})
            logger.info(f"Suscripción '{subscription_name}' al topic '{topic_name}' ya existe.")
        except Exception:
            # Si no existe, crearla
            self._subscriber.create_subscription(
                request={"name": subscription_path, "topic": topic_path}
            )
            logger.info(f"Suscripción '{subscription_name}' al topic '{topic_name}' creada.")

        # Guardar referencia para poder iniciar escucha
        self._subscriptions[topic_name] = subscription_path
        logger.info(f"Escuchando mensajes en la suscripción: {subscription_path}")

    def _crear_suscripcion(self, topic_name: str):
        """Crea una suscripción para un topic específico"""
        if not self._subscriber:
            return
        
        topic_path = self._subscriber.topic_path(self.project_id, topic_name)
        subscription_path = self._subscriber.subscription_path(
            self.project_id, f"{topic_name}-productos-sub"
        )
        
        try:
            # Crear la suscripción
            self._subscriber.create_subscription(
                request={"name": subscription_path, "topic": topic_path}
            )
            logger.info(f"✅ Suscripción creada: {subscription_path}")
            
            # Guardar referencia para poder iniciar escucha
            self._subscriptions[topic_name] = subscription_path
            
        except Exception as e:
            if "already exists" in str(e):
                logger.info(f"ℹ️ Suscripción ya existe: {subscription_path}")
                self._subscriptions[topic_name] = subscription_path
            else:
                logger.error(f"❌ Error creando suscripción {topic_name}: {e}")
    
    def iniciar_escucha(self):
        """Inicia la escucha de eventos en background"""
        if not self._subscriber:
            logger.warning("No se puede iniciar escucha: cliente no inicializado")
            return
        
        for topic_name, subscription_path in self._subscriptions.items():
            try:
                # Crear hilo para escuchar cada suscripción
                thread = threading.Thread(
                    target=self._escuchar_suscripcion,
                    args=(subscription_path, topic_name),
                    daemon=True
                )
                thread.start()
                logger.info(f"🎧 Iniciada escucha para {topic_name}")
                
            except Exception as e:
                logger.error(f"❌ Error iniciando escucha para {topic_name}: {e}")
    
    def _escuchar_suscripcion(self, subscription_path: str, topic_name: str):
        """Escucha mensajes de una suscripción específica"""
        try:
            def callback(message):
                try:
                    # Decodificar el mensaje
                    data = json.loads(message.data.decode('utf-8'))
                    
                    logger.info(f"📨 Recibido evento {data.get('tipo_evento')} desde {topic_name}")
                    
                    # Crear evento de dominio desde los datos
                    evento = self._crear_evento_desde_datos(data)
                    
                    if evento:
                        # Procesar el evento usando el sistema local con contexto de Flask
                        logger.info(f"🔄 Procesando evento {evento.__class__.__name__}")
                        
                        # Usar el contexto de la aplicación Flask si está disponible
                        if self.app:
                            with self.app.app_context():
                                from seedwork.dominio.eventos import despachador_eventos
                                
                                despachador_eventos.publicar_evento(evento, publicar_externamente=False)
                                
                                # Notificar clientes SSE si es un evento de inventario
                                if evento.__class__.__name__ in ['InventarioAsignado', 'InventarioReservado', 'InventarioDescontado']:
                                    self._notificar_sse_inventario(evento)
                        else:
                            from seedwork.dominio.eventos import despachador_eventos
                            
                            despachador_eventos.publicar_evento(evento, publicar_externamente=False)
                            
                            # Notificar clientes SSE si es un evento de inventario
                            if evento.__class__.__name__ in ['InventarioAsignado', 'InventarioReservado', 'InventarioDescontado']:
                                self._notificar_sse_inventario(evento)
                        
                        logger.info(f"✅ Evento {evento.__class__.__name__} procesado exitosamente")
                    
                    # Confirmar que el mensaje fue procesado
                    message.ack()
                    
                except Exception as e:
                    logger.error(f"❌ Error procesando mensaje: {e}")
                    message.nack()
            
            # Usar subscribe() con la API correcta
            streaming_pull_future = self._subscriber.subscribe(
                subscription_path,
                callback=callback,
                flow_control=pubsub_v1.types.FlowControl(max_messages=10)
            )
            
            logger.info(f"✅ Escucha activa para {topic_name}")
            
            # Mantener el hilo vivo
            streaming_pull_future.result()
                
        except Exception as e:
            logger.error(f"❌ Error en escucha de {topic_name}: {e}")
    
    def _crear_evento_desde_datos(self, data: Dict[str, Any]) -> EventoDominio:
        """Crea un evento de dominio desde los datos del mensaje"""
        try:
            tipo_evento = data.get('tipo_evento')
            
            if tipo_evento == 'PedidoCreado':
                # Importar el evento PedidoCreado local
                from dominio.eventos_externos import PedidoCreado, EstadoPedido
                from datetime import datetime
                import uuid
                
                datos_evento = data.get('datos', {})
                
                # Crear el evento PedidoCreado
                evento = PedidoCreado(
                    pedido_id=uuid.UUID(datos_evento.get('pedido_id')),
                    cliente_id=uuid.UUID(datos_evento.get('cliente_id')),
                    fecha_pedido=datetime.fromisoformat(datos_evento.get('fecha_pedido')) if datos_evento.get('fecha_pedido') else datetime.now(),
                    estado=EstadoPedido(datos_evento.get('estado')),
                    items_info=datos_evento.get('items_info', []),
                    total=float(datos_evento.get('total', 0))
                )
                
                return evento

            elif tipo_evento == 'PedidoConfirmado':
                # Importar evento PedidoConfirmado local
                from dominio.eventos import PedidoConfirmado

                datos_evento = data.get('datos', {})

                # Crear instancia del evento PedidoConfirmado
                evento = PedidoConfirmado(
                    pedido_id=datos_evento.get('pedido_id', ''),
                    cliente_id=datos_evento.get('cliente_id', ''),
                    vendedor_id=datos_evento.get('vendedor_id', ''),
                    items=datos_evento.get('items', []),
                    total=float(datos_evento.get('total', 0))
                )

                return evento

            elif tipo_evento == 'InventarioAsignado':
                # Importar el evento InventarioAsignado
                from dominio.eventos import InventarioAsignado
                import uuid
                
                datos_evento = data.get('datos', {})
                
                # Crear el evento InventarioAsignado
                evento = InventarioAsignado(
                    producto_id=uuid.UUID(datos_evento.get('producto_id')),
                    stock=int(datos_evento.get('stock', 0)),
                    fecha_vencimiento=datos_evento.get('fecha_vencimiento', '')
                )
                
                return evento
            
            else:
                logger.warning(f"⚠️ Tipo de evento no reconocido: {tipo_evento}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error creando evento desde datos: {e}")
            return None
    
    def _notificar_sse_inventario(self, evento: EventoDominio):
        """Notifica a clientes SSE sobre cambios de inventario"""
        try:
            from infraestructura.sse_manager import sse_client_manager
            from infraestructura.repositorios import RepositorioInventarioSQLite
            
            producto_id = None
            if hasattr(evento, 'producto_id'):
                producto_id = str(evento.producto_id)
            
            if producto_id:
                # Obtener cantidad disponible actualizada del repositorio
                repo_inventario = RepositorioInventarioSQLite()
                lotes_inventario = repo_inventario.obtener_por_producto_id(producto_id)
                
                if lotes_inventario:
                    cantidad_disponible_total = sum(lote.cantidad_disponible for lote in lotes_inventario)
                    
                    # Notificar clientes SSE
                    sse_client_manager.notificar_todos('update', {
                        'producto_id': producto_id,
                        'cantidad_disponible': cantidad_disponible_total
                    })
                    logger.info(f"Clientes SSE notificados desde consumidor Pub/Sub para producto {producto_id} (cantidad disponible: {cantidad_disponible_total})")
        except Exception as e:
            logger.error(f"Error notificando clientes SSE desde consumidor Pub/Sub: {e}")