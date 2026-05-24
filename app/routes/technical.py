import re
from functools import wraps
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.extensions import db
from app.models.user import User

# Blueprint de Soporte Tecnico
technical_bp = Blueprint('technical', __name__)

EMAIL_REGEX = r'^[\w\.-]+@[\w\.-]+\.\w+$'

def tecnico_required():
    # Decorador personalizado para requerir rol de tecnico
    def decorator(fn):
        @wraps(fn)
        @jwt_required()
        def wrapper(*args, **kwargs):
            try:
                current_user_id = get_jwt_identity()
                user = User.query.get(int(current_user_id))
                
                if not user or user.role != 'tecnico':
                    return jsonify({"error": "Acceso denegado. Se requieren privilegios de soporte tecnico."}), 403
                    
                return fn(*args, **kwargs)
            except Exception as e:
                return jsonify({"error": f"Error de autenticacion: {str(e)}"}), 401
        return wrapper
    return decorator

@technical_bp.route('/users', methods=['POST'])
@tecnico_required()
def create_user_by_tech():
    # Tecnico puede crear un nuevo administrador o usuario
    data = request.get_json() or {}
    email = data.get('email', '').strip()
    password = data.get('password', '')
    name = data.get('name', '').strip()
    role = data.get('role', 'admin').strip()
    
    if not email or not password:
        return jsonify({"error": "Email y contrasenia son requeridos"}), 400
        
    if not re.match(EMAIL_REGEX, email):
        return jsonify({"error": "Formato de email invalido"}), 400
        
    if len(password) < 6:
        return jsonify({"error": "La contrasenia debe tener al menos 6 caracteres"}), 400
        
    try:
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return jsonify({"error": "El correo ya esta registrado"}), 400
            
        user = User(email=email, name=name if name else None, role=role)
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        return jsonify({
            "message": "Usuario creado exitosamente por soporte tecnico",
            "user": user.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Fallo al crear usuario: {str(e)}"}), 500

@technical_bp.route('/users/<int:user_id>', methods=['DELETE'])
@tecnico_required()
def delete_user_by_tech(user_id):
    # Tecnico puede eliminar un usuario
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": "Usuario no encontrado"}), 404
            
        db.session.delete(user)
        db.session.commit()
        
        return jsonify({"message": "Usuario eliminado exitosamente"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Fallo al eliminar usuario: {str(e)}"}), 500

@technical_bp.route('/users/<int:user_id>/block', methods=['POST'])
@tecnico_required()
def block_user(user_id):
    # Tecnico puede bloquear a un usuario (ej. por pagos)
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": "Usuario no encontrado"}), 404
            
        user.is_blocked = True
        db.session.commit()
        
        return jsonify({
            "message": "Usuario bloqueado y suspendido exitosamente",
            "user": user.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Fallo al bloquear usuario: {str(e)}"}), 500

@technical_bp.route('/users/<int:user_id>/unblock', methods=['POST'])
@tecnico_required()
def unblock_user(user_id):
    # Tecnico puede desbloquear a un usuario
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": "Usuario no encontrado"}), 404
            
        user.is_blocked = False
        db.session.commit()
        
        return jsonify({
            "message": "Usuario desbloqueado y reactivado exitosamente",
            "user": user.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Fallo al desbloquear usuario: {str(e)}"}), 500

@technical_bp.route('/users/<int:user_id>/change-password', methods=['POST'])
@tecnico_required()
def change_password_by_tech(user_id):
    # Tecnico puede cambiar contrasenia manualmente y forzar a on_change
    data = request.get_json() or {}
    new_password = data.get('new_password', '')
    
    if not new_password or len(new_password) < 6:
        return jsonify({"error": "La nueva contrasenia debe tener al menos 6 caracteres"}), 400
        
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": "Usuario no encontrado"}), 404
            
        # Hashear nueva contraseña y forzar on_change
        user.set_password(new_password)
        user.password_status = 'on_change'
        
        db.session.commit()
        
        return jsonify({
            "message": "Contrasenia modificada exitosamente. Se requerira cambio obligatorio en el proximo login.",
            "user": user.to_dict()
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Fallo al cambiar contrasenia del usuario: {str(e)}"}), 500
