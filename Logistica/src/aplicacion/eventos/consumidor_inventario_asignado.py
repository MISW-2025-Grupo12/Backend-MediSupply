from seedwork.dominio.eventos import ManejadorEvento
from infraestructura.repositorios import RepositorioInventarioSQLite, RepositorioBodegaSQLite
from aplicacion.dto import InventarioDTO
from seedwork.aplicacion.comandos import ejecutar_comando
from aplicacion.comandos.inicializar_bodegas import InicializarBodegas
from datetime import datetime
import logging
import random

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
            
            # Obtener bodegas disponibles
            from api import app as flask_app
            with flask_app.app_context():
                try:
                    repo_bodega = RepositorioBodegaSQLite()
                    bodegas = repo_bodega.obtener_todas()
                    
                    if not bodegas:
                        logger.warning("No hay bodegas creadas, inicializando...")
                        ejecutar_comando(InicializarBodegas())
                        bodegas = repo_bodega.obtener_todas()
                    
                    # Seleccionar bodega aleatoria
                    bodega_seleccionada = random.choice(bodegas)
                    
                    # Generar pasillo y estante aleatorios
                    pasillo = random.choice(['A', 'B', 'C', 'D', 'E'])
                    estante = str(random.randint(1, 20))
                    
                    logger.info(f"Asignando producto {evento.producto_id} a {bodega_seleccionada.nombre} - Pasillo {pasillo} - Estante {estante}")
                    
                except Exception as bodega_error:
                    logger.error(f"Error obteniendo bodegas: {bodega_error}")
                    # Usar valores por defecto si hay error
                    bodega_seleccionada = None
                    pasillo = 'A'
                    estante = '1'
            
            # Crear DTO de inventario con ubicación
            inventario_dto = InventarioDTO(
                producto_id=str(evento.producto_id),
                cantidad_disponible=evento.stock,
                cantidad_reservada=0,
                fecha_vencimiento=fecha_vencimiento or datetime.now(),
                bodega_id=bodega_seleccionada.id if bodega_seleccionada else None,
                pasillo=pasillo,
                estante=estante
            )
            
            # Guardar en repositorio con contexto de aplicación
            with flask_app.app_context():
                try:
                    repo_inventario = RepositorioInventarioSQLite()
                    
                    # Buscar todos los lotes existentes del producto
                    lotes_existentes = repo_inventario.obtener_por_producto_id(str(evento.producto_id))
                    lote_existente = None
                    
                    # Buscar lote con la misma fecha de vencimiento (comparando solo la fecha, no la hora)
                    fecha_vencimiento_date = inventario_dto.fecha_vencimiento.date() if hasattr(inventario_dto.fecha_vencimiento, 'date') else inventario_dto.fecha_vencimiento
                    
                    for lote in lotes_existentes:
                        lote_fecha_date = lote.fecha_vencimiento.date() if hasattr(lote.fecha_vencimiento, 'date') else lote.fecha_vencimiento
                        if lote_fecha_date == fecha_vencimiento_date:
                            lote_existente = lote
                            logger.info(f"✅ Encontrado lote existente para producto {evento.producto_id} con fecha {fecha_vencimiento_date}")
                            break
                    
                    # Preparar valores para el DTO (que es inmutable)
                    cantidad_anterior = 0
                    cantidad_nueva = evento.stock
                    cantidad_total = cantidad_nueva
                    fecha_vencimiento_final = inventario_dto.fecha_vencimiento
                    bodega_id_final = inventario_dto.bodega_id
                    pasillo_final = inventario_dto.pasillo
                    estante_final = inventario_dto.estante
                    cantidad_reservada_final = 0
                    lote_id_final = None
                    
                    if lote_existente:
                        # Actualizar lote existente sumando las cantidades
                        cantidad_anterior = lote_existente.cantidad_disponible
                        cantidad_total = cantidad_anterior + cantidad_nueva
                        cantidad_reservada_final = lote_existente.cantidad_reservada
                        fecha_vencimiento_final = lote_existente.fecha_vencimiento
                        bodega_id_final = lote_existente.bodega_id
                        pasillo_final = lote_existente.pasillo
                        estante_final = lote_existente.estante
                        lote_id_final = lote_existente.id
                        
                        logger.info(f"📦 Actualizando lote existente {lote_id_final} para producto {evento.producto_id}: {cantidad_anterior} + {cantidad_nueva} = {cantidad_total}")
                    else:
                        # Si no hay lote con la misma fecha, buscar el lote más reciente del producto
                        if lotes_existentes:
                            # Ordenar por fecha de vencimiento (más reciente primero)
                            lotes_ordenados = sorted(lotes_existentes, key=lambda x: x.fecha_vencimiento, reverse=True)
                            lote_mas_reciente = lotes_ordenados[0]
                            
                            # Sumar al lote más reciente
                            cantidad_anterior = lote_mas_reciente.cantidad_disponible
                            cantidad_total = cantidad_anterior + cantidad_nueva
                            cantidad_reservada_final = lote_mas_reciente.cantidad_reservada
                            fecha_vencimiento_final = lote_mas_reciente.fecha_vencimiento
                            bodega_id_final = lote_mas_reciente.bodega_id
                            pasillo_final = lote_mas_reciente.pasillo
                            estante_final = lote_mas_reciente.estante
                            lote_id_final = lote_mas_reciente.id
                            
                            logger.info(f"📦 No se encontró lote con fecha {fecha_vencimiento_date}, sumando al lote más reciente {lote_id_final}: {cantidad_anterior} + {cantidad_nueva} = {cantidad_total}")
                        else:
                            logger.info(f"✨ Creando nuevo lote para producto {evento.producto_id} con fecha {fecha_vencimiento_final}")
                    
                    # Crear nuevo DTO con los valores actualizados (el DTO es inmutable)
                    inventario_dto_actualizado = InventarioDTO(
                        id=lote_id_final or inventario_dto.id,
                        producto_id=str(evento.producto_id),
                        cantidad_disponible=cantidad_total,
                        cantidad_reservada=cantidad_reservada_final,
                        fecha_vencimiento=fecha_vencimiento_final,
                        bodega_id=bodega_id_final,
                        pasillo=pasillo_final,
                        estante=estante_final,
                        requiere_cadena_frio=inventario_dto.requiere_cadena_frio
                    )
                    
                    # Usar crear_o_actualizar para evitar duplicados
                    repo_inventario.crear_o_actualizar(inventario_dto_actualizado)
                    logger.info(f"✅ Inventario actualizado exitosamente para producto {evento.producto_id}. Stock total: {cantidad_total} (anterior: {cantidad_anterior}, nuevo: {cantidad_nueva})")
                except Exception as db_error:
                    logger.error(f"❌ Error guardando en base de datos: {db_error}", exc_info=True)
                    raise
            
        except Exception as e:
            logger.error(f"Error manejando evento InventarioAsignado: {e}")

# Registrar el manejador
from seedwork.dominio.eventos import despachador_eventos
manejador = ManejadorInventarioAsignado()
despachador_eventos.registrar_manejador('InventarioAsignado', manejador)
print("ManejadorInventarioAsignado registrado correctamente")
