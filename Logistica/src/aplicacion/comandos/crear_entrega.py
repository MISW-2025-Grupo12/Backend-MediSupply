from dataclasses import dataclass
from seedwork.aplicacion.comandos import Comando
from seedwork.aplicacion.comandos import ejecutar_comando as comando
from infraestructura.repositorios import RepositorioEntregaSQLite
from infraestructura.servicio_usuarios import ServicioUsuarios
from aplicacion.dto import EntregaDTO
from aplicacion.utilidades.dias_habiles import calcular_dia_habil_siguiente
from datetime import datetime
import uuid
import logging

logger = logging.getLogger(__name__)

@dataclass
class CrearEntrega(Comando):
    pedido_id: str
    cliente_id: str
    vendedor_id: str
    items: list  # [{"producto_id": str, "cantidad": int}, ...]
    total: float

class CrearEntregaHandler:
    def __init__(self):
        self._repositorio: RepositorioEntregaSQLite = RepositorioEntregaSQLite()
        self._servicio_usuarios: ServicioUsuarios = ServicioUsuarios()
    
    def handle(self, comando: CrearEntrega) -> dict:
        """Crea una entrega cuando un pedido se confirma"""
        try:
            # Validar datos de entrada
            if not comando.pedido_id or not comando.cliente_id:
                return {
                    'success': False,
                    'error': 'pedido_id y cliente_id son obligatorios'
                }
            
            # Obtener dirección del cliente desde el servicio de Usuarios
            cliente = self._servicio_usuarios.obtener_cliente_por_id(comando.cliente_id)
            if not cliente:
                return {
                    'success': False,
                    'error': f'Cliente {comando.cliente_id} no encontrado en servicio de Usuarios'
                }
            
            direccion_cliente = cliente.get('direccion', '')
            if not direccion_cliente:
                return {
                    'success': False,
                    'error': f'Cliente {comando.cliente_id} no tiene dirección registrada'
                }
            
            # Calcular fecha de entrega (día hábil siguiente a la fecha actual)
            fecha_confirmacion = datetime.now()
            fecha_entrega = calcular_dia_habil_siguiente(fecha_confirmacion)
            
            # Construir objeto pedido completo desde el evento
            pedido_completo = {
                'id': comando.pedido_id,
                'cliente_id': comando.cliente_id,
                'vendedor_id': comando.vendedor_id,
                'items': comando.items,
                'total': comando.total,
                'estado': 'confirmado',
                'fecha_confirmacion': fecha_confirmacion.isoformat()
            }
            
            # Crear DTO de entrega
            entrega_dto = EntregaDTO(
                id=uuid.uuid4(),
                direccion=direccion_cliente,
                fecha_entrega=fecha_entrega,
                pedido=pedido_completo
            )
            
            # Guardar en repositorio
            self._repositorio.crear(entrega_dto)
            
            logger.info(f"Entrega creada exitosamente para pedido {comando.pedido_id} - Fecha entrega: {fecha_entrega}")
            
            return {
                'success': True,
                'message': f'Entrega creada exitosamente para pedido {comando.pedido_id}',
                'entrega_id': str(entrega_dto.id),
                'fecha_entrega': fecha_entrega.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error creando entrega para pedido {comando.pedido_id}: {e}")
            return {
                'success': False,
                'error': f'Error interno: {str(e)}'
            }

@comando.register(CrearEntrega)
def ejecutar_crear_entrega(comando: CrearEntrega):
    handler = CrearEntregaHandler()
    return handler.handle(comando)
