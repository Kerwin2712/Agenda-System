from datetime import datetime
from app.extensions import db

class Appointment(db.Model):
    # Comentarios cortos en español
    # Nombre de la tabla de citas
    __tablename__ = 'appointments'
    
    id = db.Column(db.Integer, primary_key=True)
    event_id = db.Column(db.Integer, db.ForeignKey('events.id', ondelete='CASCADE'), nullable=False)
    client_name = db.Column(db.String(100), nullable=False)
    client_email = db.Column(db.String(120), nullable=False)
    client_phone = db.Column(db.String(20), nullable=False) # Para contacto directo del admin
    start_time = db.Column(db.DateTime, nullable=False) # Fecha y hora inicio
    end_time = db.Column(db.DateTime, nullable=False) # Fecha y hora fin (inicio + duracion)
    status = db.Column(db.String(20), default='pending', nullable=False) # pending, confirmed, cancelled
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relacion bidireccional con Event
    event = db.relationship('Event', backref=db.backref('appointments', lazy=True, cascade="all, delete-orphan"))
    
    # Indexacion para optimizar busquedas por evento y horarios agendados
    __table_args__ = (
        db.Index('idx_event_time', 'event_id', 'start_time'),
    )

    def to_dict(self):
        # Serializar cita a diccionario
        return {
            "id": self.id,
            "event_id": self.event_id,
            "client_name": self.client_name,
            "client_email": self.client_email,
            "client_phone": self.client_phone,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "status": self.status,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }
