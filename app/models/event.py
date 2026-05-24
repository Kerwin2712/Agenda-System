from datetime import datetime
from app.extensions import db

class Event(db.Model):
    # Comentarios cortos en español
    # Nombre de la tabla de eventos
    __tablename__ = 'events'
    
    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('event_groups.id', ondelete='CASCADE'), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=True)
    duration = db.Column(db.Integer, nullable=False) # Duracion en minutos
    buffer_time = db.Column(db.Integer, default=0, nullable=False) # Espera en minutos entre citas
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacion bidireccional con EventGroup
    group = db.relationship('EventGroup', backref=db.backref('events', lazy=True, cascade="all, delete-orphan"))

    def to_dict(self):
        # Serializar evento a diccionario
        return {
            "id": self.id,
            "group_id": self.group_id,
            "title": self.title,
            "description": self.description,
            "duration": self.duration,
            "buffer_time": self.buffer_time,
            "is_active": self.is_active,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

class GroupAvailability(db.Model):
    # Nombre de la tabla de disponibilidad grupal
    __tablename__ = 'group_availabilities'
    
    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('event_groups.id', ondelete='CASCADE'), nullable=False)
    day_of_week = db.Column(db.Integer, nullable=False) # 1=Lunes, 7=Domingo
    start_time = db.Column(db.Time, nullable=False) # Hora inicio
    end_time = db.Column(db.Time, nullable=False) # Hora fin
    
    # Relacion bidireccional con EventGroup
    group = db.relationship('EventGroup', backref=db.backref('availabilities', lazy=True, cascade="all, delete-orphan"))
    
    # Indexacion para acelerar busquedas de disponibilidad por grupo y dia
    __table_args__ = (
        db.Index('idx_group_day', 'group_id', 'day_of_week'),
    )

    def to_dict(self):
        # Serializar disponibilidad a diccionario
        return {
            "id": self.id,
            "group_id": self.group_id,
            "day_of_week": self.day_of_week,
            "start_time": self.start_time.strftime('%H:%M:%S') if self.start_time else None,
            "end_time": self.end_time.strftime('%H:%M:%S') if self.end_time else None
        }
