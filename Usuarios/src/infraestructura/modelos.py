from config.db import db
import uuid
from datetime import datetime

class ProveedorModel(db.Model):
    __tablename__ = 'proveedores'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    nombre = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    direccion = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
