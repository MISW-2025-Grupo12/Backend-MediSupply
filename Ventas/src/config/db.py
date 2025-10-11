from flask_sqlalchemy import SQLAlchemy
from flask import Flask
import os

db = SQLAlchemy()

def init_db(app: Flask):
    database_uri = os.getenv('SQLALCHEMY_DATABASE_URI', 'postgresql://postgres:postgres@ventas-db:5432/ventas')
    app.config['SQLALCHEMY_DATABASE_URI'] = database_uri
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    
    with app.app_context():
        db.create_all()
