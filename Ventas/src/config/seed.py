"""
Seed data para el microservicio de Ventas
Inserción directa en BD con control total sobre datos históricos
"""
import logging
from flask import Flask
from datetime import datetime, timedelta, time
import uuid

logger = logging.getLogger(__name__)

# UUIDs consistentes (deben coincidir con otros servicios)
VENDEDOR_ID = "550e8400-e29b-41d4-a716-446655440001"
CLIENTE_ID = "550e8400-e29b-41d4-a716-446655440002"

PRODUCTO_IDS = {
    "Tensiómetro Digital": "650e8400-e29b-41d4-a716-446655440101",
    "Estetoscopio": "650e8400-e29b-41d4-a716-446655440102",
    "Termómetro Infrarrojo": "650e8400-e29b-41d4-a716-446655440103",
    "Bisturí": "650e8400-e29b-41d4-a716-446655440104",
    "Pinzas Quirúrgicas": "650e8400-e29b-41d4-a716-446655440105",
    "Guantes de Látex": "650e8400-e29b-41d4-a716-446655440107",
    "Jeringas Desechables": "650e8400-e29b-41d4-a716-446655440108"
}

PRECIOS = {
    "Tensiómetro Digital": 89000.0,
    "Estetoscopio": 125000.0,
    "Termómetro Infrarrojo": 75000.0,
    "Bisturí": 45000.0,
    "Pinzas Quirúrgicas": 38000.0,
    "Guantes de Látex": 28000.0,
    "Jeringas Desechables": 35000.0
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
        
        logger.info("Iniciando seed de datos de Ventas...")
        try:
            _create_seed_data()
            logger.info("Seed de Ventas completado exitosamente")
        except Exception as e:
            logger.error(f"Error durante seed de Ventas: {e}")
            import traceback
            logger.error(traceback.format_exc())


def is_database_empty() -> bool:
    """Verifica si la base de datos está vacía"""
    from infraestructura.modelos import VisitaModel
    
    try:
        count = VisitaModel.query.count()
        return count == 0
    except Exception as e:
        logger.warning(f"Error verificando si BD está vacía: {e}")
        return False


def _create_seed_data():
    """Crea los datos iniciales de visitas, pedidos e items con inserción directa"""
    from infraestructura.modelos import VisitaModel, PedidoModel, ItemPedidoModel
    from config.db import db
    
    # ==================== 1. CREAR VISITAS ====================
    logger.info("Creando visitas históricas...")
    
    visitas_data = [
        # 6 REALIZADAS (hace 90-15 días)
        {
            "estado": "realizada",
            "dias_atras": 90,
            "descripcion": "Presentación de catálogo completo de equipos médicos",
            "novedades": "Cliente muy interesado en equipos de diagnóstico",
            "pedido_generado": True
        },
        {
            "estado": "realizada",
            "dias_atras": 75,
            "descripcion": "Seguimiento y toma de pedido de equipos",
            "novedades": "Pedido confirmado de tensiómetros y estetoscopios",
            "pedido_generado": True
        },
        {
            "estado": "realizada",
            "dias_atras": 60,
            "descripcion": "Entrega de muestras de productos",
            "novedades": "Cliente satisfecho con la calidad",
            "pedido_generado": False
        },
        {
            "estado": "realizada",
            "dias_atras": 45,
            "descripcion": "Renovación de pedido mensual",
            "novedades": "Pedido de instrumental quirúrgico",
            "pedido_generado": True
        },
        {
            "estado": "realizada",
            "dias_atras": 30,
            "descripcion": "Visita de seguimiento post-venta",
            "novedades": "Cliente solicita más guantes y jeringas",
            "pedido_generado": True
        },
        {
            "estado": "realizada",
            "dias_atras": 15,
            "descripcion": "Presentación de nuevos productos",
            "novedades": "Cliente interesado en termómetros infrarrojos",
            "pedido_generado": True
        },
        # 2 PENDIENTES (próximos 7-14 días)
        {
            "estado": "pendiente",
            "dias_futuro": 7,
            "descripcion": "Visita programada para renovación de stock",
            "novedades": None,
            "pedido_generado": False
        },
        {
            "estado": "pendiente",
            "dias_futuro": 14,
            "descripcion": "Presentación de equipos de última generación",
            "novedades": None,
            "pedido_generado": False
        },
        # 2 CANCELADAS (hace 60-30 días)
        {
            "estado": "cancelada",
            "dias_atras": 55,
            "descripcion": "Visita cancelada por el cliente",
            "novedades": "Cliente requiere reprogramación",
            "pedido_generado": False
        },
        {
            "estado": "cancelada",
            "dias_atras": 35,
            "descripcion": "Visita cancelada por fuerza mayor",
            "novedades": "Reagendar próxima semana",
            "pedido_generado": False
        }
    ]
    
    for visita_data in visitas_data:
        if "dias_atras" in visita_data:
            fecha_programada = datetime.now() - timedelta(days=visita_data["dias_atras"])
            fecha_realizada = fecha_programada.date() if visita_data["estado"] in ["realizada", "cancelada"] else None
            hora_realizada = time(10, 30) if visita_data["estado"] == "realizada" else None
            created_at = fecha_programada
        else:  # dias_futuro
            fecha_programada = datetime.now() + timedelta(days=visita_data["dias_futuro"])
            fecha_realizada = None
            hora_realizada = None
            created_at = datetime.now()
        
        visita = VisitaModel(
            id=str(uuid.uuid4()),
            vendedor_id=VENDEDOR_ID,
            cliente_id=CLIENTE_ID,
            fecha_programada=fecha_programada,
            direccion="Carrera 7 #32-16, Bogotá D.C.",
            telefono="3109876543",
            estado=visita_data["estado"],
            descripcion=visita_data["descripcion"],
            fecha_realizada=fecha_realizada,
            hora_realizada=hora_realizada,
            novedades=visita_data["novedades"],
            pedido_generado=visita_data["pedido_generado"],
            created_at=created_at,
            updated_at=created_at
        )
        db.session.add(visita)
    
    db.session.commit()
    logger.info(f"  {len(visitas_data)} visitas creadas (6 realizadas, 2 pendientes, 2 canceladas)")
    
    # ==================== 2. CREAR PEDIDOS ====================
    logger.info("Creando pedidos históricos...")
    
    pedidos_data = [
        # 3 ENTREGADOS (hace 80-20 días)
        {
            "estado": "entregado",
            "dias_atras": 80,
            "items": [
                {"producto": "Tensiómetro Digital", "cantidad": 5},
                {"producto": "Estetoscopio", "cantidad": 3}
            ]
        },
        {
            "estado": "entregado",
            "dias_atras": 50,
            "items": [
                {"producto": "Termómetro Infrarrojo", "cantidad": 10}
            ]
        },
        {
            "estado": "entregado",
            "dias_atras": 20,
            "items": [
                {"producto": "Bisturí", "cantidad": 8},
                {"producto": "Pinzas Quirúrgicas", "cantidad": 6}
            ]
        },
        # 2 CONFIRMADOS (hace 10-5 días)
        {
            "estado": "confirmado",
            "dias_atras": 10,
            "items": [
                {"producto": "Guantes de Látex", "cantidad": 20}
            ]
        },
        {
            "estado": "confirmado",
            "dias_atras": 5,
            "items": [
                {"producto": "Jeringas Desechables", "cantidad": 15},
                {"producto": "Tensiómetro Digital", "cantidad": 3}
            ]
        },
        # 2 BORRADOR (actuales)
        {
            "estado": "borrador",
            "dias_atras": 0,
            "items": [
                {"producto": "Estetoscopio", "cantidad": 2}
            ]
        },
        {
            "estado": "borrador",
            "dias_atras": 0,
            "items": [
                {"producto": "Termómetro Infrarrojo", "cantidad": 5},
                {"producto": "Guantes de Látex", "cantidad": 10}
            ]
        },
        # 1 CANCELADO (hace 45 días)
        {
            "estado": "cancelado",
            "dias_atras": 45,
            "items": [
                {"producto": "Bisturí", "cantidad": 15}
            ]
        }
    ]
    
    pedidos_count = 0
    items_count = 0
    total_global = 0.0
    
    for pedido_data in pedidos_data:
        fecha_pedido = datetime.now() - timedelta(days=pedido_data["dias_atras"]) if pedido_data["dias_atras"] > 0 else datetime.now()
        
        # Calcular total del pedido
        total_pedido = 0.0
        for item in pedido_data["items"]:
            producto_nombre = item["producto"]
            cantidad = item["cantidad"]
            precio = PRECIOS[producto_nombre]
            total_pedido += cantidad * precio
        
        # Crear pedido
        pedido_id = str(uuid.uuid4())
        pedido = PedidoModel(
            id=pedido_id,
            vendedor_id=VENDEDOR_ID,
            cliente_id=CLIENTE_ID,
            estado=pedido_data["estado"],
            total=total_pedido,
            created_at=fecha_pedido,
            updated_at=fecha_pedido
        )
        db.session.add(pedido)
        db.session.commit()  # Commit pedido antes de items (FK constraint)
        
        pedidos_count += 1
        total_global += total_pedido
        
        # Crear items del pedido
        for item_data in pedido_data["items"]:
            producto_nombre = item_data["producto"]
            cantidad = item_data["cantidad"]
            precio_unitario = PRECIOS[producto_nombre]
            subtotal = cantidad * precio_unitario
            
            item = ItemPedidoModel(
                id=str(uuid.uuid4()),
                pedido_id=pedido_id,
                producto_id=PRODUCTO_IDS[producto_nombre],
                nombre_producto=producto_nombre,
                cantidad=cantidad,
                precio_unitario=precio_unitario,
                subtotal=subtotal,
                created_at=fecha_pedido,
                updated_at=fecha_pedido
            )
            db.session.add(item)
            items_count += 1
        
        db.session.commit()  # Commit items
        
        logger.info(f"  Pedido {pedido_data['estado']}: ${total_pedido:,.0f} COP - {len(pedido_data['items'])} items")
    
    logger.info(f"  {pedidos_count} pedidos creados con {items_count} items - Total: ${total_global:,.0f} COP")
    logger.info(f"    (3 entregados, 2 confirmados, 2 borrador, 1 cancelado)")
    
    logger.info(f"10 visitas y 8 pedidos históricos seed fueron creados exitosamente")


