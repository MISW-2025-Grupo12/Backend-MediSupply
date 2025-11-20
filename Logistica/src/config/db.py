from flask_sqlalchemy import SQLAlchemy
from flask import Flask
import os

db = SQLAlchemy()

def init_db(app: Flask):
    if 'SQLALCHEMY_DATABASE_URI' not in app.config:
        # Configurar PostgreSQL para producción
        db_host = os.getenv('DB_HOST', 'logistica-db')
        db_port = os.getenv('DB_PORT', '5432')
        db_name = os.getenv('DB_NAME', 'logistica_db')
        db_user = os.getenv('DB_USER', 'logistica_user')
        db_password = os.getenv('DB_PASSWORD', 'logistica_pass')
        
        app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'
    
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_size': 5,           # Número de conexiones a mantener en el pool
        'max_overflow': 10,        # Máximo de conexiones adicionales
        'pool_pre_ping': True,     # Verificar conexiones antes de usarlas
        'pool_recycle': 3600,      # Reciclar conexiones después de 1 hora
        'pool_timeout': 20         # Timeout para obtener conexión del pool
    }
    db.init_app(app)
    
    # Crear tablas si no existen
    with app.app_context():
        db.create_all()
        
        # Ejecutar seed data
        from config.seed import seed_data
        seed_data(app)
    