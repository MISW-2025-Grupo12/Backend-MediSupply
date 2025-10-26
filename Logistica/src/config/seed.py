"""
Seed data para el microservicio de Logística
Inserción directa en BD con control total sobre datos
"""
import logging
from flask import Flask
from datetime import datetime, timedelta
import uuid
import json

logger = logging.getLogger(__name__)

# UUIDs consistentes para productos (deben coincidir con Productos)
PRODUCTO_IDS = {
    "Tensiómetro Digital": "650e8400-e29b-41d4-a716-446655440101",
    "Estetoscopio": "650e8400-e29b-41d4-a716-446655440102",
    "Termómetro Infrarrojo": "650e8400-e29b-41d4-a716-446655440103",
    "Bisturí": "650e8400-e29b-41d4-a716-446655440104",
    "Pinzas Quirúrgicas": "650e8400-e29b-41d4-a716-446655440105",
    "Tijeras Médicas": "650e8400-e29b-41d4-a716-446655440106",
    "Guantes de Látex": "650e8400-e29b-41d4-a716-446655440107",
    "Jeringas Desechables": "650e8400-e29b-41d4-a716-446655440108",
    "Gasas Estériles": "650e8400-e29b-41d4-a716-446655440109",
    "Alcohol en Gel": "650e8400-e29b-41d4-a716-446655440110"
}


def seed_data(app: Flask):
    """
    Ejecuta seeding si la BD está vacía y no está en modo testing
    """
    if app.config.get('TESTING'):
        logger.info("Modo testing detectado - omitiendo seed de datos")
        return
    
    with app.app_context():
        if not is_database_empty():
            logger.info("Base de datos ya contiene datos - omitiendo seed")
            return
        
        logger.info("Iniciando seed de datos de Logística...")
        try:
            _create_seed_data()
            logger.info("Seed de Logística completado exitosamente")
        except Exception as e:
            logger.error(f"Error durante seed de Logística: {e}")
            import traceback
            logger.error(traceback.format_exc())


def is_database_empty() -> bool:
    """Verifica si la base de datos está vacía"""
    from infraestructura.modelos import BodegaModel
    
    try:
        count = BodegaModel.query.count()
        return count == 0
    except Exception as e:
        logger.warning(f"Error verificando si BD está vacía: {e}")
        return False


def _create_seed_data():
    """Crea los datos iniciales de bodegas, inventario y entregas con inserción directa"""
    from infraestructura.modelos import BodegaModel, InventarioModel, EntregaModel
    from config.db import db
    
    # ==================== 1. CREAR BODEGAS PRIMERO ====================
    logger.info("Creando bodegas...")
    
    bodegas_data = [
        {
            "nombre": "Bodega Central Bogotá",
            "direccion": "Calle 100 #15-20, Bogotá"
        },
        {
            "nombre": "Bodega Norte Medellín",
            "direccion": "Carrera 43A #1-50, Medellín"
        },
        {
            "nombre": "Bodega Sur Cali",
            "direccion": "Avenida 5N #23-50, Cali"
        }
    ]
    
    bodegas_ids = []
    for bodega_data in bodegas_data:
        bodega = BodegaModel(
            id=str(uuid.uuid4()),
            nombre=bodega_data["nombre"],
            direccion=bodega_data["direccion"],
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.session.add(bodega)
        bodegas_ids.append(bodega.id)
        logger.info(f"  Bodega '{bodega_data['nombre']}' creada")
    
    db.session.commit()
    
    # ==================== 2. CREAR INVENTARIO (referencia bodegas y productos) ====================
    logger.info("Creando inventario...")
    
    productos_list = list(PRODUCTO_IDS.items())
    pasillos = ['A', 'B', 'C']
    estantes = ['1', '2', '3', '4']
    
    inventario_count = 0
    
    # Distribuir productos en las 3 bodegas
    for bodega_id in bodegas_ids:
        for producto_nombre, producto_id in productos_list:
            # Cada producto tiene 50 unidades por bodega
            inventario = InventarioModel(
                id=str(uuid.uuid4()),
                producto_id=producto_id,
                cantidad_disponible=50,
                cantidad_reservada=0,
                fecha_vencimiento=datetime.now() + timedelta(days=365),
                bodega_id=bodega_id,
                pasillo=pasillos[inventario_count % len(pasillos)],
                estante=estantes[inventario_count % len(estantes)],
                requiere_cadena_frio=False,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db.session.add(inventario)
            inventario_count += 1
    
    db.session.commit()
    logger.info(f"  {inventario_count} registros de inventario creados")
    logger.info(f"  Stock total: {inventario_count * 50} unidades distribuidas")
    
    # ==================== 3. CREAR ENTREGAS COMPLETADAS (históricas) ====================
    logger.info("Creando entregas históricas completadas...")
    
    # UUIDs de clientes (referencias externas)
    CLIENTE_ID = "550e8400-e29b-41d4-a716-446655440002"
    
    entregas_data = [
        {
            "direccion": "Carrera 7 #32-16, Bogotá",
            "dias_atras": 75,
            "items": [
                {"producto": "Tensiómetro Digital", "cantidad": 5},
                {"producto": "Estetoscopio", "cantidad": 3}
            ],
            "total": 820000.0
        },
        {
            "direccion": "Calle 100 #15-20, Bogotá",
            "dias_atras": 60,
            "items": [
                {"producto": "Termómetro Infrarrojo", "cantidad": 10}
            ],
            "total": 750000.0
        },
        {
            "direccion": "Avenida El Dorado #68-90, Bogotá",
            "dias_atras": 45,
            "items": [
                {"producto": "Bisturí", "cantidad": 8},
                {"producto": "Pinzas Quirúrgicas", "cantidad": 6}
            ],
            "total": 588000.0
        },
        {
            "direccion": "Carrera 43A #1-50, Medellín",
            "dias_atras": 30,
            "items": [
                {"producto": "Guantes de Látex", "cantidad": 20}
            ],
            "total": 560000.0
        },
        {
            "direccion": "Avenida 5N #23-50, Cali",
            "dias_atras": 15,
            "items": [
                {"producto": "Jeringas Desechables", "cantidad": 15},
                {"producto": "Gasas Estériles", "cantidad": 10}
            ],
            "total": 745000.0
        }
    ]
    
    entregas_count = 0
    for entrega_data in entregas_data:
        fecha_entrega = datetime.now() - timedelta(days=entrega_data["dias_atras"])
        
        # Construir pedido con items
        items_pedido = []
        for item in entrega_data["items"]:
            items_pedido.append({
                "producto_id": PRODUCTO_IDS[item["producto"]],
                "cantidad": item["cantidad"]
            })
        
        pedido_info = {
            "pedido_id": str(uuid.uuid4()),
            "cliente_id": CLIENTE_ID,
            "items": items_pedido,
            "total": entrega_data["total"]
        }
        
        entrega = EntregaModel(
            id=str(uuid.uuid4()),
            direccion=entrega_data["direccion"],
            fecha_entrega=fecha_entrega,
            pedido=json.dumps(pedido_info),
            created_at=fecha_entrega,
            updated_at=fecha_entrega
        )
        db.session.add(entrega)
        entregas_count += 1
        logger.info(f"  Entrega completada: {entrega_data['direccion'][:35]}... - hace {entrega_data['dias_atras']} días")
    
    db.session.commit()
    logger.info(f"  {entregas_count} entregas históricas creadas")
    
    logger.info(f"3 bodegas, {inventario_count} registros de inventario y {entregas_count} entregas seed fueron creados exitosamente")


