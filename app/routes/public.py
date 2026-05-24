from flask import Blueprint, jsonify
from app.models.user import User
from app.models.event import Event

# Blueprint publico que no requiere JWT
public_bp = Blueprint('public', __name__)

@public_bp.route('/users/<public_slug>/events', methods=['GET'])
def get_public_events(public_slug):
    # Comentarios cortos en español
    # Buscar el usuario por public_slug
    user = User.query.filter_by(public_slug=public_slug).first()
    if not user:
        return jsonify({"error": "Usuario no encontrado"}), 404
        
    # Filtrar eventos que esten activos y sean publicos
    events = Event.query.filter_by(
        user_id=user.id,
        is_active=True,
        is_public=True
    ).all()
    
    return jsonify([event.to_dict() for event in events]), 200

@public_bp.route('/users/<public_slug>/events/<event_slug>', methods=['GET'])
def get_public_event_detail(public_slug, event_slug):
    # Buscar el usuario por public_slug
    user = User.query.filter_by(public_slug=public_slug).first()
    if not user:
        return jsonify({"error": "Usuario no encontrado"}), 404
        
    # Buscar evento activo por slug e ignorar is_public
    event = Event.query.filter_by(
        user_id=user.id,
        slug=event_slug,
        is_active=True
    ).first()
    
    if not event:
        return jsonify({"error": "Evento no encontrado o inactivo"}), 404
        
    return jsonify(event.to_dict()), 200
