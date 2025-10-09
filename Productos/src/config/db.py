from flask_sqlalchemy import SQLAlchemy
from flask import Flask
import os

db = SQLAlchemy()

def init_db(app: Flask):
    # Configurar SQLite para desarrollo local
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///productos.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    
    # Crear tablas si no existen
    with app.app_context():
        db.create_all()
    