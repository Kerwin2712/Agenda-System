from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_cors import CORS

# Limitar comentarios a frases en español cortas
# Inicializar extensiones
db = SQLAlchemy()
jwt = JWTManager()
cors = CORS()
