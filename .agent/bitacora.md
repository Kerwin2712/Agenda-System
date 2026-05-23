# Bitácora de Desarrollo - "Agenda tu cita"

Este documento registra cronológicamente los cambios en el backend, el contexto de las decisiones tomadas y el estado de la integración con el frontend.

---

## [2026-05-23] - Inicialización del Proyecto

### Contexto Inicial
El proyecto "Agenda tu cita" es un sistema SaaS de agendamiento. El backend se desarrolla en Python utilizando **Flask**, **SQLAlchemy** (mapeando dinámicamente MySQL para desarrollo local y PostgreSQL para producción) y autenticación mediante **JWT**. El frontend será desarrollado de manera independiente usando React.

### Cambios Realizados
1. **Creación de la Carpeta del Agente:**
   - Creado `.agent/workflow.md` para hacer cumplir el flujo estricto del agente.
   - Creado `.agent/bitacora.md` (este archivo) para rastrear el progreso y las decisiones de diseño.
2. **Configuración del Entorno y Estructura Modular:**
   - Creado `requirements.txt` con todas las dependencias (`Flask`, `Flask-SQLAlchemy`, `Flask-JWT-Extended`, `Flask-Cors`, `python-dotenv`, `PyMySQL`, `psycopg2-binary==2.9.10` para compatibilidad con Python 3.13).
   - Creado `.env.example` y `.env` para la inyección segura de variables de entorno de base de datos y llaves JWT.
   - Creado `run.py` como punto de entrada de la aplicación.
3. **Core y Arquitectura de la Aplicación (`app/`):**
   - Creado `app/extensions.py` inicializando `db`, `jwt` y `cors` sin acoplamiento inmediato.
   - Creado `app/config.py` con una lógica robusta para seleccionar el string de conexión de base de datos (con fallback a SQLite local y corrección para PostgreSQL en producción).
   - Creado `app/__init__.py` con el *Application Factory* `create_app()`, manejadores de error globales en JSON y la autoinicialización de tablas de base de datos en entornos de desarrollo.
4. **Modelos de Datos (`app/models/`):**
   - Creado `app/models/user.py` definiendo el modelo `User` con campos indexados (`email`), timestamps de control y métodos seguros `set_password` / `check_password` basados en Werkzeug.
5. **Rutas y Controladores (`app/routes/`):**
   - Creado `app/routes/auth.py` implementando validaciones de entrada robustas (expresiones regulares para correos, contraseñas mínimas) y la lógica para el registro exitoso (código 201) y login con generación de tokens JWT (código 200).
   - Creado `app/routes/dashboard.py` implementando la ruta protegida `/status` (código 200) que requiere cabecera de autenticación válida para retornar los datos del usuario actual.
6. **Verificación y Pruebas:**
   - Creado `verify_api.py`, un script que usa el cliente de pruebas nativo de Flask (`app.test_client()`) en una base de datos SQLite en memoria para testear de manera automatizada y local todos los endpoints sin necesidad de iniciar servidores externos. Las pruebas pasaron con un **100% de éxito**.
7. **Documentación:**
   - Creado `docs/API_FRONTEND.md` detallando la URL base, el envío del token de autenticación en cabeceras y ejemplos JSON de petición/respuesta para todos los endpoints.

### Decisiones Técnicas
- **Hasheo de Contraseñas:** Se utiliza `werkzeug.security` para garantizar el almacenamiento seguro de contraseñas de manera eficiente y robusta sin dependencias binarias propensas a fallos en entornos Windows.
- **Base de Datos Dinámica:** La aplicación evalúa dinámicamente el URI de conexión de base de datos a través de `.env`, permitiendo cambiar sin cambios de código entre SQLite (desarrollo local rápido), MySQL (desarrollo avanzado) y PostgreSQL (producción).
- **Testeo Aislado:** Se optó por probar con `app.test_client()` implementando un `TestConfig` que fuerza el uso de SQLite `:memory:` desde la inicialización. Esto asegura pruebas 100% autónomas y repetibles libres de conflictos con datos persistidos previamente en entornos locales.
- **Compatibilidad con Python 3.13:** Ante fallos de compilación de `psycopg2-binary==2.9.9` en Python 3.13 sobre entornos Windows, se actualizó la dependencia a la versión `2.9.10` en `requirements.txt`. Esta versión provee ruedas precompiladas oficiales (pre-built wheels) para Python 3.13, solucionando los problemas de compilación C++ por completo.

### Impacto en el Frontend
- **Endpoints disponibles:** `/api/auth/register`, `/api/auth/login`, y `/api/dashboard/status`.
- Se requiere la cabecera `Authorization: Bearer <token>` para consumir el dashboard.
- Toda la especificación detallada está en `docs/API_FRONTEND.md`.

- Subida inicial del backend modular y su documentación técnica exitosamente completada en la rama `main` de GitHub.
- Creado y estructurado el archivo central `README.md` con la guía de inicio rápido (entorno virtual venv, instalación en Windows con Python 3.13, variables de entorno, y scripts de pruebas unitarias). Se mantuvo `requirements.txt` limpio para evitar errores de sintaxis en `pip`. Listo para que el desarrollador frontend y el equipo de backend trabajen en el proyecto.
- **Limpieza de la Raíz del Proyecto:** Trasladamos el script de verificación automatizado `verify_api.py` de la raíz del proyecto al nuevo directorio `tests/` (`tests/verify_api.py`). Esto mantiene la raíz del proyecto limpia y optimizada para producción/despliegue, dejando solo archivos esenciales de despliegue. Adaptamos dinámicamente el `sys.path` del script para garantizar que se ejecute sin problemas de importación.
