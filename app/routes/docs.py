import os
from flask import Blueprint, jsonify, Response

# Blueprint para servir la documentacion interactiva local
docs_bp = Blueprint('docs', __name__)

@docs_bp.route('/', methods=['GET'])
def render_docs():
    # Comentarios cortos en español
    # Ruta raiz que sirve el index.html de documentacion
    try:
        # Ruta absoluta hacia el index.html en /docs
        docs_path = os.path.join(os.getcwd(), 'docs', 'index.html')
        
        if not os.path.exists(docs_path):
            return jsonify({"error": "El archivo index.html de documentacion no existe"}), 404
            
        with open(docs_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        return Response(content, mimetype='text/html'), 200
    except Exception as e:
        return jsonify({"error": f"Fallo al abrir visualizador de documentacion: {str(e)}"}), 500

@docs_bp.route('/api/docs/api-frontend', methods=['GET'])
def get_api_frontend_docs():
    # Retorna el Markdown de integracion frontend
    try:
        filepath = os.path.join(os.getcwd(), 'docs', 'API_FRONTEND.md')
        
        if not os.path.exists(filepath):
            return jsonify({"error": "El archivo API_FRONTEND.md no existe"}), 404
            
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
        return jsonify({"markdown": content}), 200
    except Exception as e:
        return jsonify({"error": f"Error al leer documentacion de API: {str(e)}"}), 500

@docs_bp.route('/api/docs/db-guide', methods=['GET'])
def get_db_guide_docs():
    # Retorna el Markdown de guia de base de datos
    try:
        filepath = os.path.join(os.getcwd(), 'docs', 'FRONTEND_DB_GUIDE.md')
        
        if not os.path.exists(filepath):
            return jsonify({"error": "El archivo FRONTEND_DB_GUIDE.md no existe"}), 404
            
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
        return jsonify({"markdown": content}), 200
    except Exception as e:
        return jsonify({"error": f"Error al leer documentacion de Base de Datos: {str(e)}"}), 500

@docs_bp.route('/api/docs/readme', methods=['GET'])
def get_readme_docs():
    # Retorna el Markdown del README.md en la raiz
    try:
        filepath = os.path.join(os.getcwd(), 'README.md')
        
        if not os.path.exists(filepath):
            return jsonify({"error": "El archivo README.md no existe"}), 404
            
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
        return jsonify({"markdown": content}), 200
    except Exception as e:
        return jsonify({"error": f"Error al leer el archivo README.md: {str(e)}"}), 500

@docs_bp.route('/api/docs/dbml', methods=['GET'])
def get_dbml_docs():
    # Retorna el contenido del archivo DBML conceptual
    try:
        filepath = os.path.join(os.getcwd(), 'docs', 'database.dbml')
        
        if not os.path.exists(filepath):
            return jsonify({"error": "El archivo database.dbml no existe"}), 404
            
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
        return jsonify({"dbml": content}), 200
    except Exception as e:
        return jsonify({"error": f"Error al leer la especificacion DBML: {str(e)}"}), 500
