from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db

class User(db.Model):
    # Limitar comentarios a frases en español cortas
    # Nombre de la tabla en base de datos
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(80), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def set_password(self, password):
        # Hashear contrasenia con werkzeug
        if not password or len(password) < 6:
            raise ValueError("La contrasenia debe tener al menos 6 caracteres")
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        # Verificar contrasenia
        if not self.password_hash or not password:
            return False
        return check_password_hash(self.password_hash, password)
        
    def to_dict(self):
        # Serializar modelo a diccionario
        return {
            "id": self.id,
            "email": self.email,
            "name": self.name,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
