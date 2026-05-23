import os
from datetime import timedelta

class Config:
    # Limitar comentarios a frases en español cortas
    # Claves secretas de Flask y JWT
    SECRET_KEY = os.environ.get('SECRET_KEY', 'fallback-secret-key-1298403912')
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'fallback-jwt-secret-key-9283749823')
    
    # Tiempo de expiracion del token JWT
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=1)
    
    # Manejo robusto de la URL de base de datos
    db_url = os.environ.get('DATABASE_URL')
    
    if db_url:
        # Corregir postgres:// obsoleto a postgresql://
        if db_url.startswith('postgres://'):
            db_url = db_url.replace('postgres://', 'postgresql://', 1)
    else:
        # Fallback seguro a SQLite local si no hay configuracion
        db_url = 'sqlite:///agenda_fallback.db'
        
    SQLALCHEMY_DATABASE_URI = db_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False
