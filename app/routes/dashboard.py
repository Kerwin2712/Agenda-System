from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.user import User

# Limitar comentarios a frases en español cortas
# Blueprint de dashboard
dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/status', methods=['GET'])
@jwt_required()
def status():
    # Obtener el ID del usuario del token
    current_user_id = get_jwt_identity()
    
    try:
        # Buscar usuario en base de datos
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({"error": "Usuario no encontrado en la sesion actual"}), 404
            
        # Retornar estatus del backend y datos de usuario
        return jsonify({
            "status": "online",
            "message": "Token de autenticacion verificado exitosamente",
            "user": user.to_dict()
        }), 200
        
    except Exception as e:
        # Captura de errores robusta
        return jsonify({"error": f"Fallo al recuperar informacion de la sesion: {str(e)}"}), 500
