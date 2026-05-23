import os
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

# Limitar comentarios a frases en español cortas
# Importar la fabrica de la aplicacion
from app import create_app

app = create_app()

if __name__ == '__main__':
    # Arrancar en modo debug si FLASK_DEBUG es True
    is_debug = os.environ.get('FLASK_DEBUG', 'False').lower() in ('true', '1', 't')
    port = int(os.environ.get('PORT', 5000))
    
    # Iniciar servidor local
    app.run(host='0.0.0.0', port=port, debug=is_debug)
