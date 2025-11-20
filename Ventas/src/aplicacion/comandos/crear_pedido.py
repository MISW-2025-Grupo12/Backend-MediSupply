from dataclasses import dataclass
from seedwork.aplicacion.comandos import Comando
from seedwork.aplicacion.comandos import ejecutar_comando as comando
from infraestructura.repositorios import RepositorioPedidoSQLite
from infraestructura.servicio_usuarios import ServicioUsuarios
from dominio.entidades import Pedido
from dominio.objetos_valor import EstadoPedido, Precio
from seedwork.dominio.eventos import despachador_eventos
import logging
import uuid

logger = logging.getLogger(__name__)

@dataclass
class CrearPedido(Comando):
    vendedor_id: str
    cliente_id: str

class CrearPedidoHandler:
    def __init__(self):
        self._repositorio: RepositorioPedidoSQLite = RepositorioPedidoSQLite()
        self._servicio_usuarios: ServicioUsuarios = ServicioUsuarios()
    
    def handle(self, comando: CrearPedido) -> dict:
        """Crear un nuevo pedido en estado borrador"""
        try:
            # Validar datos de entrada
            if not comando.vendedor_id or not comando.cliente_id:
                return {
                    'success': False,
                    'error': 'vendedor_id y cliente_id son obligatorios'
                }
            
            # Validar existencia de vendedor
            vendedor = self._servicio_usuarios.obtener_vendedor_por_id(comando.vendedor_id)
            if not vendedor:
                return {
                    'success': False,
                    'error': f'Vendedor {comando.vendedor_id} no existe'
                }
            
            # Validar existencia de cliente
            cliente = self._servicio_usuarios.obtener_cliente_por_id(comando.cliente_id)
            if not cliente:
                return {
                    'success': False,
                    'error': f'Cliente {comando.cliente_id} no existe'
                }
            
            # Crear entidad de dominio
            pedido = Pedido(
                vendedor_id=comando.vendedor_id,
                cliente_id=comando.cliente_id,
                estado=EstadoPedido("borrador"),
                total=Precio(0.0)
            )
            
            # Guardar en repositorio
            pedido_creado = self._repositorio.crear(pedido)
            
            # Disparar evento de creación
            evento = pedido_creado.disparar_evento_creacion()
            despachador_eventos.publicar_evento(evento)
            
            # Obtener el ID del pedido usando el método obtener_id()
            pedido_id = str(pedido_creado.obtener_id())
                
            return {
                'success': True,
                'pedido_id': pedido_id,
                'vendedor_id': pedido_creado.vendedor_id,
                'cliente_id': pedido_creado.cliente_id,
                'estado': pedido_creado.estado.estado,
                'total': pedido_creado.total.valor,
                'items': []
            }
            
        except Exception as e:
            logger.error(f"Error creando pedido: {e}")
            return {
                'success': False,
                'error': f'Error interno: {str(e)}'
            }

@comando.register(CrearPedido)
def ejecutar_crear_pedido(comando: CrearPedido):
    handler = CrearPedidoHandler()
    return handler.handle(comando)
