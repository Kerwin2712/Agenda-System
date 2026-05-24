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

- **Limpieza de la Raíz del Proyecto:** Trasladamos el script de verificación automatizado `verify_api.py` de la raíz del proyecto al nuevo directorio `tests/` (`tests/verify_api.py`). Esto mantiene la raíz del proyecto limpia y optimizada para producción/despliegue, dejando solo archivos esenciales de despliegue. Adaptamos dinámicamente el `sys.path` del script para garantizar que se ejecute sin problemas de importación.

## [2026-05-24] - Refactorización de Disponibilidad Grupal y Enrutamiento por Slugs

### Contexto de Negocio
Para resolver la problemática del solapamiento de agendas (overbooking) en un único profesional o recursos compartidos, se rediseñó la arquitectura de base de datos introduciendo **Grupos de Eventos** (`event_groups`). Asimismo, para facilitar la interacción y el marketing directo, se implementó un esquema de acceso público amigable basado en slugs (`public_slug` para administradores y `slug` para eventos) en lugar de exponer identificadores numéricos directos de base de datos.

### Cambios Realizados
1. **Refactorización de Modelos Relacionales:**
   - **`User`**: Adición del campo obligatorio y único `public_slug`. Implementación de una rutina automática en el constructor del modelo para autogenerar el slug a partir del email si no se proporciona explícitamente, garantizando compatibilidad con el endpoint de registro existente.
   - **`EventGroup`**: Modelo contenedor asociado al administrador que agrupa eventos que comparten la misma disponibilidad horaria.
   - **`GroupAvailability`**: Registra la disponibilidad horaria semanal recurrente asociada directamente al `EventGroup` (en lugar de a eventos individuales). Indexación en `(group_id, day_of_week)`.
   - **`Event`**: Incorporación de `slug`, `is_public` (default `True`), y `user_id` de forma complementaria para declarar la restricción de unicidad compuesta `UniqueConstraint('user_id', 'slug')`. Esto previene de forma estricta que un mismo administrador repita URLs públicas.
2. **Creación de la API Pública:**
   - Implementado el módulo `app/routes/public.py` y registrado el Blueprint `public_bp` con el prefijo `/api/public`.
   - Endpoints públicos libres de tokens JWT creados:
     - `GET /api/public/users/<public_slug>/events`: Directorio público que filtra estrictamente por eventos activos y públicos.
     - `GET /api/public/users/<public_slug>/events/<event_slug>`: Enlace directo que retorna los detalles del evento si está activo (ignora el flag `is_public` para permitir eventos privados con enlace directo).
3. **Actualización Documental:**
   - Editado `docs/API_FRONTEND.md` detallando las nuevas especificaciones JSON para la API pública.
   - Editada esta bitácora en cumplimiento estricto con las reglas de flujo de trabajo del agente.

### Decisiones Técnicas
- **Exclusividad compuesta `(user_id, slug)` en `Event`**: Se decidió mantener el `user_id` de forma redundante pero necesaria en la tabla `events` a fin de poder declarar un índice de unicidad que impida colisiones de URL a nivel del mismo administrador, sin forzar búsquedas recursivas complejas que penalicen el rendimiento de la base de datos.
- **Autogeneración de Slugs**: Para evitar que la adición del campo no nulo `public_slug` rompa los registros del frontend que no envíen dicho campo, el backend procesa automáticamente la parte local del correo electrónico de registro para crear un slug único e higienizado.
- **Regla Estricta de Parada**: Se detiene toda interacción con herramientas Git. El agente no realizará commits automáticos hasta recibir confirmación explícitamente.

