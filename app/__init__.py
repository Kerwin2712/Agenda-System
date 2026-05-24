from flask import Flask, jsonify
from app.config import Config
from app.extensions import db, jwt, cors

def create_app(config_class=Config):
    # Limitar comentarios a frases en español cortas
    # Crear instancia de la app Flask
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Inicializar extensiones
    # Permitir CORS para desarrollo con React
    cors.init_app(app, resources={r"/api/*": {"origins": "*"}})
    db.init_app(app)
    jwt.init_app(app)
    
    # Registrar blueprints
    from app.routes.auth import auth_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.public import public_bp
    
    app.register_blueprint(auth_bp, url_prefix='/api/auth')
    app.register_blueprint(dashboard_bp, url_prefix='/api/dashboard')
    app.register_blueprint(public_bp, url_prefix='/api/public')
    
    # Manejo de errores global en formato JSON
    @app.errorhandler(404)
    def not_found_error(error):
        return jsonify({"error": "Recurso no encontrado"}), 404
        
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({"error": "Error interno del servidor"}), 500
        
    # Inicializar base de datos de manera segura
    with app.app_context():
        try:
            db.create_all()
        except Exception as e:
            # Capturar fallos de conexion a BD de forma amigable
            app.logger.error(f"Error al crear tablas en base de datos: {e}")
            
    return app
