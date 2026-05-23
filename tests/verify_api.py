import os
import sys
import json

# Limitar comentarios a frases en español cortas
# Agregar directorio padre al path para importar modulo app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from app.extensions import db
from app.models.user import User
from app.config import Config

# Script de pruebas del API usando Flask Test Client

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

def run_tests():
    # Inicializar aplicacion en modo test con base de datos en memoria
    app = create_app(TestConfig)
    
    client = app.test_client()
    
    print("=== INICIANDO PRUEBAS DE INTEGRACIÓN ===")
    
    with app.app_context():
        # Crear base de datos temporal
        db.create_all()
        
        # Test Data
        test_email = "test@ejemplo.com"
        test_pass = "password123"
        test_name = "Usuario de Pruebas"
        
        # 1. PRUEBA DE REGISTRO
        print("\n1. Probando Registro (/api/auth/register)...")
        payload = {
            "email": test_email,
            "password": test_pass,
            "name": test_name
        }
        res = client.post('/api/auth/register', 
                          data=json.dumps(payload), 
                          content_type='application/json')
        
        print(f"Estado recibido: {res.status_code}")
        print(f"Respuesta: {res.get_data(as_text=True)}")
        assert res.status_code == 201, "Error: El registro deberia ser exitoso (201)"
        
        # Probar registro duplicado
        print("\nProbando Registro Duplicado...")
        res_dup = client.post('/api/auth/register', 
                              data=json.dumps(payload), 
                              content_type='application/json')
        print(f"Estado recibido: {res_dup.status_code}")
        print(f"Respuesta: {res_dup.get_data(as_text=True)}")
        assert res_dup.status_code == 400, "Error: Deberia fallar por correo duplicado (400)"
        
        # 2. PRUEBA DE LOGIN
        print("\n2. Probando Login (/api/auth/login)...")
        login_payload = {
            "email": test_email,
            "password": test_pass
        }
        res_login = client.post('/api/auth/login', 
                                data=json.dumps(login_payload), 
                                content_type='application/json')
        
        print(f"Estado recibido: {res_login.status_code}")
        login_data = json.loads(res_login.get_data(as_text=True))
        print(f"Respuesta: {json.dumps(login_data, indent=2)}")
        assert res_login.status_code == 200, "Error: El login deberia ser exitoso (200)"
        
        # Extraer token JWT
        token = login_data.get("access_token")
        assert token is not None, "Error: No se recibio un token JWT"
        print(f"Token obtenido: {token[:30]}... (truncado)")
        
        # Probando login con contraseña errónea
        print("\nProbando Login con Contrasenia Incorrecta...")
        bad_login_payload = {
            "email": test_email,
            "password": "wrong_password"
        }
        res_bad_login = client.post('/api/auth/login', 
                                    data=json.dumps(bad_login_payload), 
                                    content_type='application/json')
        print(f"Estado recibido: {res_bad_login.status_code}")
        print(f"Respuesta: {res_bad_login.get_data(as_text=True)}")
        assert res_bad_login.status_code == 401, "Error: Deberia denegar acceso por contrasenia incorrecta (401)"
        
        # 3. PRUEBA DE ACCESO PROTEGIDO (DASHBOARD)
        print("\n3. Probando Endpoint Protegido Sin Token...")
        res_dash_no_token = client.get('/api/dashboard/status')
        print(f"Estado recibido (Sin Token): {res_dash_no_token.status_code}")
        assert res_dash_no_token.status_code == 401, "Error: Deberia denegar acceso sin token (401)"
        
        print("\nProbando Endpoint Protegido Con Token Valido...")
        headers = {
            "Authorization": f"Bearer {token}"
        }
        res_dash_token = client.get('/api/dashboard/status', headers=headers)
        print(f"Estado recibido: {res_dash_token.status_code}")
        dash_data = json.loads(res_dash_token.get_data(as_text=True))
        print(f"Respuesta: {json.dumps(dash_data, indent=2)}")
        assert res_dash_token.status_code == 200, "Error: El acceso con token deberia ser exitoso (200)"
        assert dash_data["user"]["email"] == test_email, "Error: El email retornado no coincide"
        
        print("\n=== ¡TODAS LAS PRUEBAS PASARON EXITOSAMENTE! ===")

if __name__ == '__main__':
    run_tests()
