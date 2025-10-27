from flask_sqlalchemy import SQLAlchemy
from flask import Flask
import os

db = SQLAlchemy()

def init_db(app: Flask):
    # Usar la URI de conexión configurada en la aplicación
    if 'SQLALCHEMY_DATABASE_URI' not in app.config:
        # Configurar PostgreSQL para producción
        db_host = os.getenv('DB_HOST', 'productos-db')
        db_port = os.getenv('DB_PORT', '5432')
        db_name = os.getenv('DB_NAME', 'productos_db')
        db_user = os.getenv('DB_USER', 'productos_user')
        db_password = os.getenv('DB_PASSWORD', 'productos_pass')
        
        app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'
    
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    
    # Crear tablas si no existen
    with app.app_context():
        db.create_all()
        
        # Ejecutar seed data
        from config.seed import seed_data
        seed_data(app)
    