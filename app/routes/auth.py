import re
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token
from app.extensions import db
from app.models.user import User

# Limitar comentarios a frases en español cortas
# Blueprint de autenticacion
auth_bp = Blueprint('auth', __name__)

# Expresion regular basica para validar emails
EMAIL_REGEX = r'^[\w\.-]+@[\w\.-]+\.\w+$'

@auth_bp.route('/register', methods=['POST'])
def register():
    # Registrar nuevo usuario
    data = request.get_json() or {}
    
    email = data.get('email', '').strip()
    password = data.get('password', '')
    name = data.get('name', '').strip()
    
    # Validacion robusta de campos obligatorios
    if not email or not password:
        return jsonify({"error": "Email y contrasenia son requeridos"}), 400
        
    if not re.match(EMAIL_REGEX, email):
        return jsonify({"error": "Formato de email invalido"}), 400
        
    if len(password) < 6:
        return jsonify({"error": "La contrasenia debe tener al menos 6 caracteres"}), 400
        
    # Verificar si el email ya existe
    try:
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            return jsonify({"error": "El correo ya esta registrado"}), 400
            
        # Crear usuario y guardar en BD
        user = User(email=email, name=name if name else None)
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        return jsonify({
            "message": "Usuario registrado exitosamente",
            "user": user.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        # Manejo de error robusto
        return jsonify({"error": f"Fallo al registrar usuario: {str(e)}"}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    # Login de usuario existente
    data = request.get_json() or {}
    
    email = data.get('email', '').strip()
    password = data.get('password', '')
    
    # Validacion basica
    if not email or not password:
        return jsonify({"error": "Email y contrasenia son requeridos"}), 400
        
    try:
        user = User.query.filter_by(email=email).first()
        
        # Verificar contrasenia y credenciales
        if not user or not user.check_password(password):
            return jsonify({"error": "Credenciales invalidas"}), 401
            
        # Generar token JWT de acceso
        # Guardar el ID como identidad del token
        access_token = create_access_token(identity=str(user.id))
        
        return jsonify({
            "message": "Inicio de sesion exitoso",
            "access_token": access_token,
            "token_type": "Bearer",
            "user": user.to_dict()
        }), 200
        
    except Exception as e:
        # Manejo robusto de excepciones
        return jsonify({"error": f"Error al procesar inicio de sesion: {str(e)}"}), 500
