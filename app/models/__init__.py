from app.models.user import User
from app.models.event import Event, EventAvailability
from app.models.appointment import Appointment

# Exportar todos los modelos para SQLAlchemy
__all__ = ['User', 'Event', 'EventAvailability', 'Appointment']
