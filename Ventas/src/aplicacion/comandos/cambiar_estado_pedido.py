from dataclasses import dataclass
from seedwork.aplicacion.comandos import Comando
from seedwork.aplicacion.comandos import ejecutar_comando as comando
from infraestructura.repositorios import RepositorioPedidoSQLite
from seedwork.dominio.eventos import despachador_eventos
import logging
from infraestructura.servicio_logistica import ServicioLogistica


logger = logging.getLogger(__name__)

@dataclass
class CambiarEstadoPedido(Comando):
    pedido_id: str
    nuevo_estado: str
    usuario_id: str
    tipo_usuario: str

class CambiarEstadoPedidoHandler:
    def __init__(self):
        self._repositorio: RepositorioPedidoSQLite = RepositorioPedidoSQLite()
        self._servicio_logistica = ServicioLogistica()
    
    def handle(self, comando: CambiarEstadoPedido) -> dict:
        """Cambia el estado de un pedido con validaciones básicas"""
        try:
            # Validar datos de entrada
            if not comando.pedido_id or not comando.nuevo_estado:
                return {
                    'success': False,
                    'error': 'pedido_id y nuevo_estado son obligatorios'
                }
            
            # Validar que el nuevo estado sea válido
            estados_validos = ['en_transito', 'entregado']
            if comando.nuevo_estado not in estados_validos:
                return {
                    'success': False,
                    'error': f'Estado inválido. Estados permitidos: {", ".join(estados_validos)}'
                }
            
            # Obtener pedido existente
            pedido = self._repositorio.obtener_por_id(comando.pedido_id)
            if not pedido:
                return {
                    'success': False,
                    'error': 'Pedido no encontrado'
                }
            
            # Guardar estado anterior
            estado_anterior = pedido.estado.estado
            
            # Validar transición de estado
            transicion_valida, error_transicion = self._validar_transicion_estado(
                pedido.estado.estado, 
                comando.nuevo_estado, 
                comando.tipo_usuario
            )
            
            if not transicion_valida:
                return {
                    'success': False,
                    'error': error_transicion
                }
            
            # Realizar cambio de estado
            resultado_cambio = self._cambiar_estado_pedido(pedido, comando.nuevo_estado)
            
            if not resultado_cambio['success']:
                return resultado_cambio
            
            # Actualizar en repositorio
            pedido_actualizado = self._repositorio.actualizar(pedido)
            
            # Disparar evento si el pedido se marcó como entregado
            if comando.nuevo_estado == 'entregado':
                evento_entrega = pedido_actualizado.disparar_evento_entrega()
                despachador_eventos.publicar_evento(evento_entrega)
            
            return {
                'success': True,
                'message': f'Estado del pedido actualizado a {comando.nuevo_estado}',
                'pedido_id': str(pedido_actualizado.id),
                'estado_anterior': estado_anterior,
                'estado_nuevo': comando.nuevo_estado,
                'vendedor_id': pedido_actualizado.vendedor_id,
                'cliente_id': pedido_actualizado.cliente_id,
                'total': pedido_actualizado.total.valor
            }
            
        except Exception as e:
            logger.error(f"Error cambiando estado del pedido: {e}")
            return {
                'success': False,
                'error': f'Error interno: {str(e)}'
            }
    
    def _validar_transicion_estado(self, estado_actual: str, estado_nuevo: str, tipo_usuario: str) -> tuple[bool, str]:
        """Valida si la transición de estado es permitida"""
        
        # Definir transiciones permitidas
        transiciones_permitidas = {
            'confirmado': ['en_transito'],
            'en_transito': ['entregado']
        }
        
        # Verificar si la transición está permitida
        if estado_actual not in transiciones_permitidas:
            return False, f'No se puede cambiar estado desde {estado_actual}'
        
        if estado_nuevo not in transiciones_permitidas[estado_actual]:
            return False, f'No se puede cambiar de {estado_actual} a {estado_nuevo}'
        
        # Validar permisos por tipo de usuario
        permisos_por_estado = {
            'en_transito': ['VENDEDOR', 'REPARTIDOR', 'ADMINISTRADOR'],
            'entregado': ['VENDEDOR', 'REPARTIDOR', 'ADMINISTRADOR']
        }
        
        if estado_nuevo not in permisos_por_estado:
            return False, f'Estado {estado_nuevo} no tiene permisos definidos'
        
        if tipo_usuario not in permisos_por_estado[estado_nuevo]:
            return False, f'Usuario tipo {tipo_usuario} no tiene permisos para cambiar a {estado_nuevo}'
        
        return True, None
    
    def _cambiar_estado_pedido(self, pedido, nuevo_estado: str) -> dict:
        """Cambia el estado del pedido usando los métodos de la entidad"""
        
        if nuevo_estado == 'en_transito':
            if pedido.marcar_en_transito():
                return {'success': True}
            else:
                return {'success': False, 'error': 'No se pudo marcar el pedido como en tránsito'}
        
        elif nuevo_estado == 'entregado':
            # Construir items a partir del pedido (mismo estilo que confirmación)
            items = [{'producto_id': it.producto_id, 'cantidad': it.cantidad.valor} for it in pedido.items]

            # 1) Entrega de inventario en Logística (descontar desde reserva)
            r = self._servicio_logistica.consumir_reserva(items)
            if not r.get('success', False):
                return {'success': False, 'error': f"No se pudo consumir la reserva: {r.get('error', 'error desconocido')}"}

            # 2) Si Logística OK → ahora sí marcamos el pedido como entregado
            if pedido.marcar_entregado():
                actualizado = self._repositorio.actualizar(pedido)
                return {'success': True, 'pedido_id': str(actualizado.id), 'estado': actualizado.estado.estado}

            return {'success': False, 'error': 'No se pudo marcar el pedido como entregado'}


@comando.register(CambiarEstadoPedido)
def ejecutar_cambiar_estado_pedido(comando: CambiarEstadoPedido):
    handler = CambiarEstadoPedidoHandler()
    return handler.handle(comando)
