from seedwork.dominio.eventos import ManejadorEvento
from infraestructura.repositorios import RepositorioInventarioSQLite
from aplicacion.dto import InventarioDTO
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class ManejadorInventarioAsignado(ManejadorEvento):
    def manejar(self, evento):
        """Maneja el evento InventarioAsignado para crear inventario en Logística"""
        try:
            logger.info(f"Recibido evento InventarioAsignado para producto {evento.producto_id}")
            
            # Convertir fecha_vencimiento de string a datetime
            fecha_vencimiento = None
            if evento.fecha_vencimiento:
                try:
                    # Parsear fecha ISO
                    fecha_vencimiento = datetime.fromisoformat(evento.fecha_vencimiento.replace('Z', '+00:00'))
                    # Remover zona horaria para compatibilidad
                    if fecha_vencimiento.tzinfo is not None:
                        fecha_vencimiento = fecha_vencimiento.replace(tzinfo=None)
                except ValueError:
                    logger.error(f"Formato de fecha inválido: {evento.fecha_vencimiento}")
                    return
            
            # Crear DTO de inventario
            inventario_dto = InventarioDTO(
                producto_id=str(evento.producto_id),
                cantidad_disponible=evento.stock,
                cantidad_reservada=0,
                fecha_vencimiento=fecha_vencimiento or datetime.now()
            )
            
            # Guardar en repositorio con contexto de aplicación
            from api import create_app
            app = create_app()
            with app.app_context():
                try:
                    repo_inventario = RepositorioInventarioSQLite()
                    
                    # Buscar si ya existe un lote con la misma fecha de vencimiento
                    lotes_existentes = repo_inventario.obtener_por_producto_id(str(evento.producto_id))
                    lote_existente = None
                    
                    for lote in lotes_existentes:
                        if lote.fecha_vencimiento == inventario_dto.fecha_vencimiento:
                            lote_existente = lote
                            break
                    
                    if lote_existente:
                        # Actualizar lote existente sumando las cantidades
                        inventario_dto.cantidad_disponible += lote_existente.cantidad_disponible
                        inventario_dto.cantidad_reservada += lote_existente.cantidad_reservada
                        logger.info(f"Actualizando lote existente para producto {evento.producto_id} con fecha {inventario_dto.fecha_vencimiento}")
                    else:
                        logger.info(f"Creando nuevo lote para producto {evento.producto_id} con fecha {inventario_dto.fecha_vencimiento}")
                    
                    # Usar crear_o_actualizar para evitar duplicados
                    repo_inventario.crear_o_actualizar(inventario_dto)
                    logger.info(f"Inventario procesado exitosamente para producto {evento.producto_id} con stock {evento.stock}")
                except Exception as db_error:
                    logger.error(f"Error guardando en base de datos: {db_error}")
                    raise
            
        except Exception as e:
            logger.error(f"Error manejando evento InventarioAsignado: {e}")

# Registrar el manejador
from seedwork.dominio.eventos import despachador_eventos
manejador = ManejadorInventarioAsignado()
despachador_eventos.registrar_manejador('InventarioAsignado', manejador)
print("ManejadorInventarioAsignado registrado correctamente")
