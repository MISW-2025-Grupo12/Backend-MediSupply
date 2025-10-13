from flask_sqlalchemy import SQLAlchemy
from flask import Flask
import os

db = SQLAlchemy()

def init_test_db(app: Flask):
    """Configuración de base de datos para pruebas usando SQLite en memoria"""
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['TESTING'] = True
    db.init_app(app)
    
    # Crear tablas si no existen
    with app.app_context():
        db.create_all()
