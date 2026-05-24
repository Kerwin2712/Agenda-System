from datetime import datetime
from app.extensions import db

class EventGroup(db.Model):
    # Comentarios cortos en español
    # Nombre de la tabla de grupos de eventos
    __tablename__ = 'event_groups'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    name = db.Column(db.String(100), nullable=False) # Nombre del grupo de eventos (ej. Consultorio A)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacion bidireccional con User
    user = db.relationship('User', backref=db.backref('event_groups', lazy=True, cascade="all, delete-orphan"))

    def to_dict(self):
        # Serializar grupo a diccionario
        return {
            "id": self.id,
            "user_id": self.user_id,
            "name": self.name,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
