"""
Seed data para el microservicio de Productos
Inserción directa en BD con control total sobre datos
"""
import logging
from flask import Flask
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)

# UUIDs consistentes para productos (usados en otros servicios)
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
        
        logger.info("Iniciando seed de datos de Productos...")
        try:
            _create_seed_data()
            logger.info("Seed de Productos completado exitosamente")
        except Exception as e:
            logger.error(f"Error durante seed de Productos: {e}")
            import traceback
            logger.error(traceback.format_exc())


def is_database_empty() -> bool:
    """Verifica si la base de datos está vacía"""
    from infraestructura.modelos import CategoriaModel
    
    try:
        count = CategoriaModel.query.count()
        return count == 0
    except Exception as e:
        logger.warning(f"Error verificando si BD está vacía: {e}")
        return False


def _create_seed_data():
    """Crea los datos iniciales de categorías y productos con inserción directa"""
    from infraestructura.modelos import CategoriaModel, ProductoModel
    from config.db import db
    
    # UUID de proveedor (referencia externa)
    PROVEEDOR_ID = "550e8400-e29b-41d4-a716-446655440003"
    
    # ==================== 1. CREAR CATEGORÍAS PRIMERO ====================
    logger.info("Creando categorías...")
    
    categorias_data = [
        {
            "nombre": "Equipos Médicos",
            "descripcion": "Equipos y dispositivos médicos para diagnóstico y monitoreo"
        },
        {
            "nombre": "Instrumental Quirúrgico",
            "descripcion": "Instrumentos y herramientas para procedimientos quirúrgicos"
        },
        {
            "nombre": "Consumibles",
            "descripcion": "Productos de uso único y consumibles médicos"
        }
    ]
    
    categorias_ids = {}
    for cat_data in categorias_data:
        categoria = CategoriaModel(
            id=str(uuid.uuid4()),
            nombre=cat_data["nombre"],
            descripcion=cat_data["descripcion"],
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.session.add(categoria)
        categorias_ids[cat_data["nombre"]] = categoria.id
        logger.info(f"  Categoría '{cat_data['nombre']}' creada")
    
    db.session.commit()
    
    # ==================== 2. CREAR PRODUCTOS (referencian categorías) ====================
    logger.info("Creando productos...")
    
    productos_data = [
        # Equipos Médicos
        {
            "nombre": "Tensiómetro Digital",
            "descripcion": "Tensiómetro digital automático con pantalla LCD, medición precisa de presión arterial",
            "precio": 89000.0,
            "categoria": "Equipos Médicos",
            "stock_inicial": 50
        },
        {
            "nombre": "Estetoscopio",
            "descripcion": "Estetoscopio profesional de doble campana, acabado cromado",
            "precio": 125000.0,
            "categoria": "Equipos Médicos",
            "stock_inicial": 50
        },
        {
            "nombre": "Termómetro Infrarrojo",
            "descripcion": "Termómetro infrarrojo sin contacto, lectura rápida en 1 segundo",
            "precio": 75000.0,
            "categoria": "Equipos Médicos",
            "stock_inicial": 50
        },
        # Instrumental Quirúrgico
        {
            "nombre": "Bisturí",
            "descripcion": "Bisturí quirúrgico de acero inoxidable con hoja intercambiable",
            "precio": 45000.0,
            "categoria": "Instrumental Quirúrgico",
            "stock_inicial": 50
        },
        {
            "nombre": "Pinzas Quirúrgicas",
            "descripcion": "Pinzas de presión quirúrgicas, acero inoxidable, 14cm",
            "precio": 38000.0,
            "categoria": "Instrumental Quirúrgico",
            "stock_inicial": 50
        },
        {
            "nombre": "Tijeras Médicas",
            "descripcion": "Tijeras médicas de precisión, punta roma, 15cm",
            "precio": 42000.0,
            "categoria": "Instrumental Quirúrgico",
            "stock_inicial": 50
        },
        # Consumibles
        {
            "nombre": "Guantes de Látex",
            "descripcion": "Guantes de látex desechables, caja x100 unidades, talla M",
            "precio": 28000.0,
            "categoria": "Consumibles",
            "stock_inicial": 50
        },
        {
            "nombre": "Jeringas Desechables",
            "descripcion": "Jeringas desechables 10ml con aguja, caja x100 unidades",
            "precio": 35000.0,
            "categoria": "Consumibles",
            "stock_inicial": 50
        },
        {
            "nombre": "Gasas Estériles",
            "descripcion": "Gasas estériles 10x10cm, caja x100 unidades",
            "precio": 22000.0,
            "categoria": "Consumibles",
            "stock_inicial": 50
        },
        {
            "nombre": "Alcohol en Gel",
            "descripcion": "Alcohol en gel antibacterial, frasco 500ml",
            "precio": 18000.0,
            "categoria": "Consumibles",
            "stock_inicial": 50
        }
    ]
    
    for prod_data in productos_data:
        categoria_id = categorias_ids[prod_data["categoria"]]
        producto_id = PRODUCTO_IDS[prod_data["nombre"]]
        
        producto = ProductoModel(
            id=producto_id,  # UUID consistente
            nombre=prod_data["nombre"],
            descripcion=prod_data["descripcion"],
            precio=prod_data["precio"],
            categoria=prod_data["categoria"],  # Nombre de la categoría
            categoria_id=categoria_id,
            proveedor_id=PROVEEDOR_ID,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.session.add(producto)
        logger.info(f"  Producto '{prod_data['nombre']}' creado - ${prod_data['precio']:,.0f} COP")
    
    db.session.commit()
    
    logger.info(f"3 categorías y 10 productos seed fueron creados exitosamente")

