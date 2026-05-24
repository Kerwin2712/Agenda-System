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
    public_slug = db.Column(db.String(80), unique=True, nullable=False, index=True)
    role = db.Column(db.String(20), default="admin", nullable=False) # admin, tecnico, etc.
    is_blocked = db.Column(db.Boolean, default=False, nullable=False) # Suspension por pagos
    password_status = db.Column(db.String(20), default="active", nullable=False) # active, on_change
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __init__(self, **kwargs):
        # Inicializar y autogenerar public_slug si no existe
        super(User, self).__init__(**kwargs)
        if not self.public_slug and self.email:
            username = self.email.split('@')[0]
            import re
            self.public_slug = re.sub(r'[^a-zA-Z0-9-]', '', username).lower()
            
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
            "public_slug": self.public_slug,
            "role": self.role,
            "is_blocked": self.is_blocked,
            "password_status": self.password_status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
