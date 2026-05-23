# Agenda tu cita - Backend SaaS 🚀

Backend para el sistema SaaS de agendamiento temporalmente llamado **"Agenda tu cita"**. Diseñado en Python con una arquitectura RESTful robusta, modular, escalable y totalmente desacoplada para integrarse fluidamente con un frontend en React.

---

## 🛠️ Stack Tecnológico

* **Framework:** Python con [Flask](https://flask.palletsprojects.com/).
* **ORM:** [SQLAlchemy](https://www.sqlalchemy.org/) para un mapeo relacional de base de datos robusto.
* **Base de Datos Dinámica:** Soporte nativo para **SQLite** (desarrollo rápido), **MySQL** (desarrollo local avanzado/producción) y **PostgreSQL** (producción en la nube) seleccionables mediante variables de entorno.
* **Autenticación:** Tokens de Acceso Seguro **JWT** (JSON Web Tokens) gestionados con `Flask-JWT-Extended`.
* **CORS:** Habilitado para permitir peticiones directas desde React en puertos locales de desarrollo.
* **Seguridad:** Hasheo criptográfico de contraseñas mediante `werkzeug.security`.

---

## 📐 Arquitectura del Proyecto

Para evitar archivos monolíticos de difícil mantenimiento, el proyecto implementa el patrón **Application Factory** y **Blueprints**:

* **Application Factory (`create_app()`):** Centraliza la creación y configuración de la aplicación de Flask, facilitando las pruebas unitarias y el intercambio dinámico de configuraciones.
* **Desacoplamiento de Extensiones:** Las instancias de SQLAlchemy (`db`), JWT y CORS se inicializan de forma aislada en `app/extensions.py` para prevenir problemas de importación circular.
* **Blueprints:** Las rutas de la aplicación están segmentadas por funcionalidad:
  * `auth_bp` (`/api/auth`): Registro, Login y generación de tokens de acceso JWT.
  * `dashboard_bp` (`/api/dashboard`): Rutas seguras y protegidas mediante tokens JWT.
* **Modelos de Datos:** La lógica relacional de base de datos se encapsula en objetos de SQLAlchemy dentro del paquete `app/models/`.

---

## 📁 Estructura del Repositorio

```text
Agenda-System/
├── .agent/
│   ├── workflow.md         # Reglas estrictas de flujo del agente de IA
│   └── bitacora.md         # Bitácora cronológica con los cambios del backend
├── app/
│   ├── __init__.py          # Fábrica de aplicaciones (create_app)
│   ├── config.py            # Carga y parseo seguro de variables de entorno
│   ├── extensions.py        # Instanciación limpia de DB, JWT y CORS
│   ├── models/
│   │   ├── __init__.py      # Exportación centralizada de modelos
│   │   └── user.py          # Modelo User con hasheo de contraseñas Werkzeug
│   └── routes/
│       ├── __init__.py      # Registro de Blueprints
│       ├── auth.py          # Endpoints de Registro y Login con validaciones
│       └── dashboard.py     # Endpoints del Dashboard (protegidos con JWT)
├── docs/
│   └── API_FRONTEND.md     # Guía técnica detallada para el desarrollador de React
├── tests/
│   └── verify_api.py       # Script autónomo de pruebas de integración local
├── .env.example            # Plantilla de variables de entorno del proyecto
├── .env                    # Configuración activa del entorno (ignorado en Git)
├── requirements.txt        # Dependencias del backend de Python
└── run.py                  # Servidor de desarrollo local de Flask
```

---

## ⚡ Guía de Inicio Rápido (Desarrollo en Windows)

Sigue estos pasos para clonar, instalar y arrancar el backend en tu máquina local de Windows utilizando **PowerShell** o **CMD**:

### 1. Requisitos Previos
* Asegúrate de tener instalado **Python 3.12** o **Python 3.13** en tu sistema.
* Te sugerimos usar un entorno virtual para mantener limpias tus dependencias.

### 2. Configurar el Entorno Virtual (`venv`)
Abre tu consola en la raíz del proyecto y ejecuta:

```powershell
# Crear el entorno virtual (llamado env)
python -m venv env

# Activar el entorno virtual en PowerShell:
.\env\Scripts\activate

# O activar en CMD:
.\env\Scripts\activate.bat
```

> [!NOTE]
> Sabrás que el entorno virtual está activo porque aparecerá `(env)` al inicio de tu prompt en la terminal.

### 3. Instalar Dependencias
Con el entorno virtual activo, instala las librerías necesarias ejecutando:

```powershell
pip install -r requirements.txt
```

*Nota: `psycopg2-binary==2.9.10` está configurado para evitar errores de compilación C++ nativos de Windows en entornos Python 3.13.*

### 4. Configurar Variables de Entorno (`.env`)
Genera tu archivo de entorno activo a partir de la plantilla provista:

```powershell
copy .env.example .env
```

Por defecto, la aplicación utilizará **SQLite local** (`sqlite:///agenda.db`) para que puedas iniciar y probar el backend de forma inmediata y automática sin tener que configurar ningún servidor de base de datos en tu máquina local.

Si deseas utilizar un servidor de **MySQL local**, descomenta la línea de MySQL en el archivo `.env` y actualiza tus credenciales:
```env
DATABASE_URL=mysql+pymysql://tu_usuario:tu_contraseña@localhost:3306/agenda_db
```

### 5. Iniciar el Servidor de Desarrollo
Para arrancar el servidor local de desarrollo de Flask en el puerto `5000`:

```powershell
python run.py
```

El servidor estará escuchando peticiones en `http://localhost:5000`. Las tablas de la base de datos se crearán automáticamente al arrancar la aplicación si aún no existen.

---

## 🧪 Ejecución de Pruebas de Integración Automatizadas

Hemos provisto un script autónomo de verificación que levanta un cliente de pruebas nativo sobre una base de datos temporal SQLite en memoria (`:memory:`), validando que los flujos de registro, login y protección de rutas JWT funcionen correctamente.

Para ejecutar las pruebas en tu entorno activo:

```powershell
python tests/verify_api.py
```

---

## 📖 Documentación de Integración con el Frontend (React)

Toda la documentación relacionada con la API para el desarrollador Frontend, incluyendo URLs base, cabeceras HTTP necesarias para adjuntar el JWT y payloads JSON exactos de petición y respuesta, se encuentra disponible en:
* 👉 **[API_FRONTEND.md](file:///C:/Users/EQUIPO%20DELL/Documents/GitHub/Agenda-System/docs/API_FRONTEND.md)**
