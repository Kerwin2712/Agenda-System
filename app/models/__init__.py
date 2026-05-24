from app.models.user import User
from app.models.event_group import EventGroup
from app.models.event import Event, GroupAvailability
from app.models.appointment import Appointment

# Exportar todos los modelos para SQLAlchemy
__all__ = ['User', 'EventGroup', 'Event', 'GroupAvailability', 'Appointment']
