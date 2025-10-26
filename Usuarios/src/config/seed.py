"""
Seed data para el microservicio de Usuarios
Inserción directa en BD con control total sobre datos
"""
import logging
from flask import Flask
from datetime import datetime
import uuid
import bcrypt

logger = logging.getLogger(__name__)


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
        
        logger.info("Iniciando seed de datos de Usuarios...")
        try:
            _create_seed_data()
            logger.info("Seed de Usuarios completado exitosamente")
        except Exception as e:
            logger.error(f"Error durante seed de Usuarios: {e}")
            import traceback
            logger.error(traceback.format_exc())


def is_database_empty() -> bool:
    """Verifica si la base de datos está vacía"""
    from infraestructura.modelos import UsuarioModel
    
    try:
        count = UsuarioModel.query.count()
        return count == 0
    except Exception as e:
        logger.warning(f"Error verificando si BD está vacía: {e}")
        return False


def _create_seed_data():
    """Crea los datos iniciales de usuarios con inserción directa"""
    from infraestructura.modelos import (
        UsuarioModel, AdministradorModel, VendedorModel, 
        ClienteModel, ProveedorModel, RepartidorModel, TipoUsuario
    )
    from config.db import db
    
    # UUIDs consistentes para referencias externas (mismos en todos los servicios)
    ADMIN_ID = "450e8400-e29b-41d4-a716-446655440000"
    VENDEDOR_ID = "550e8400-e29b-41d4-a716-446655440001"
    CLIENTE_ID = "550e8400-e29b-41d4-a716-446655440002"
    PROVEEDOR_ID = "550e8400-e29b-41d4-a716-446655440003"
    REPARTIDOR_ID = "550e8400-e29b-41d4-a716-446655440004"
    
    # ==================== 1. ADMINISTRADOR ====================
    logger.info("Creando administrador...")
    
    # 1.1 Crear entidad administrador
    admin = AdministradorModel(
        id=ADMIN_ID,
        nombre="Administrador Sistema",
        email="admin@medisupply.com",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.session.add(admin)
    
    # 1.2 Crear usuario con password hasheado
    admin_password = bcrypt.hashpw('AdminPass2024'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    admin_usuario = UsuarioModel(
        id=str(uuid.uuid4()),
        email="admin@medisupply.com",
        password_hash=admin_password,
        tipo_usuario=TipoUsuario.ADMINISTRADOR.value,
        identificacion=None,  # Administrador no tiene identificación
        entidad_id=ADMIN_ID
    )
    db.session.add(admin_usuario)
    db.session.commit()
    logger.info("  Administrador creado")
    
    # ==================== 2. VENDEDOR ====================
    logger.info("Creando vendedor...")
    
    vendedor = VendedorModel(
        id=VENDEDOR_ID,
        nombre="Carlos Vendedor",
        email="vendedor@medisupply.com",
        identificacion="1234567890",
        telefono="3001234567",
        direccion="Calle 100 #15-20, Bogotá",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.session.add(vendedor)
    
    vendedor_password = bcrypt.hashpw('VendedorPass2024'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    vendedor_usuario = UsuarioModel(
        id=str(uuid.uuid4()),
        email="vendedor@medisupply.com",
        password_hash=vendedor_password,
        tipo_usuario=TipoUsuario.VENDEDOR.value,
        identificacion="1234567890",
        entidad_id=VENDEDOR_ID
    )
    db.session.add(vendedor_usuario)
    db.session.commit()
    logger.info("  Vendedor creado")
    
    # ==================== 3. CLIENTE ====================
    logger.info("Creando cliente...")
    
    cliente = ClienteModel(
        id=CLIENTE_ID,
        nombre="María Cliente",
        email="cliente@medisupply.com",
        identificacion="0987654321",
        telefono="3109876543",
        direccion="Carrera 7 #32-16, Bogotá",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.session.add(cliente)
    
    cliente_password = bcrypt.hashpw('ClientePass2024'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    cliente_usuario = UsuarioModel(
        id=str(uuid.uuid4()),
        email="cliente@medisupply.com",
        password_hash=cliente_password,
        tipo_usuario=TipoUsuario.CLIENTE.value,
        identificacion="0987654321",
        entidad_id=CLIENTE_ID
    )
    db.session.add(cliente_usuario)
    db.session.commit()
    logger.info("  Cliente creado")
    
    # ==================== 4. PROVEEDOR ====================
    logger.info("Creando proveedor...")
    
    proveedor = ProveedorModel(
        id=PROVEEDOR_ID,
        nombre="Distribuidora MediPro S.A.S",
        email="proveedor@medisupply.com",
        identificacion="9001234567",
        telefono="6013456789",
        direccion="Calle 26 #68-30, Bogotá",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.session.add(proveedor)
    
    proveedor_password = bcrypt.hashpw('ProveedorPass2024'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    proveedor_usuario = UsuarioModel(
        id=str(uuid.uuid4()),
        email="proveedor@medisupply.com",
        password_hash=proveedor_password,
        tipo_usuario=TipoUsuario.PROVEEDOR.value,
        identificacion="9001234567",
        entidad_id=PROVEEDOR_ID
    )
    db.session.add(proveedor_usuario)
    db.session.commit()
    logger.info("  Proveedor creado")
    
    # ==================== 5. REPARTIDOR ====================
    logger.info("Creando repartidor...")
    
    repartidor = RepartidorModel(
        id=REPARTIDOR_ID,
        nombre="Jorge Repartidor",
        email="repartidor@medisupply.com",
        identificacion="5556667778",
        telefono="3205556677",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.session.add(repartidor)
    
    repartidor_password = bcrypt.hashpw('RepartidorPass2024'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    repartidor_usuario = UsuarioModel(
        id=str(uuid.uuid4()),
        email="repartidor@medisupply.com",
        password_hash=repartidor_password,
        tipo_usuario=TipoUsuario.REPARTIDOR.value,
        identificacion="5556667778",
        entidad_id=REPARTIDOR_ID
    )
    db.session.add(repartidor_usuario)
    db.session.commit()
    logger.info("  Repartidor creado")
    
    logger.info("5 usuarios seed fueron creados exitosamente")

