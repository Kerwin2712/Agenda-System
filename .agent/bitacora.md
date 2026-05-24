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

## [2026-05-24] - Implementación de Soporte Técnico, Suspensión por Pagos y Contraseñas Temporales

### Contexto de Negocio
Para optimizar las tareas de administración, soporte y facturación SaaS de la plataforma, se introdujeron capacidades multi-rol agregando la figura de **Soporte Técnico** (`role = 'tecnico'`). Se habilitó la **suspensión y bloqueo de cuentas** en caso de mora en pagos (`is_blocked`) y una máquina de estados para **contraseñas temporales** (`password_status = 'on_change'`), garantizando que cuando soporte técnico cambie manualmente la clave de un usuario, este sea forzado a actualizarla obligatoriamente en su siguiente inicio de sesión.

### Cambios Realizados
1. **Modelo `User` Refactorizado:**
   - Adición del campo `role` (String, default `"admin"`) para habilitar roles en la plataforma.
   - Adición de la bandera `is_blocked` (Boolean, default `False`) que inhabilita el inicio de sesión del usuario en caso de suspensión por pagos o morosidad.
   - Adición de `password_status` (String, default `"active"`) para modelar estados `"active"` u `"on_change"`.
   - Modificación del método `.to_dict()` para incluir los nuevos campos en la serialización JSON.
2. **Refactorización de Autenticación y Flujo Forzoso:**
   - **Ruta `/login` en `app/routes/auth.py`**:
     - Retorna error `403 Forbidden` inmediatamente si el usuario se encuentra bloqueado (`is_blocked = True`).
     - Retorna el campo `"require_password_change": true` en el JSON de respuesta exitosa (200) si la clave es de estatus `"on_change"`, permitiendo al frontend bloquear la navegación general y forzar el redireccionamiento.
   - **Nueva Ruta `/reset-temp-password` (POST) en `app/routes/auth.py`**:
     - Protegido por JWT. Permite a los usuarios con estatus `"on_change"` actualizar su contraseña por una definitiva segura, reestableciendo su estatus a `"active"`.
3. **Módulo de Soporte Técnico:**
   - Creado [app/routes/technical.py](file:///c:/Users/EQUIPO%20DELL/Documents/GitHub/Agenda-System/app/routes/technical.py) con el Blueprint `technical_bp` y decorador personalizado `@tecnico_required` que valida estrictamente que la identidad del JWT corresponda a un usuario con privilegios de técnico.
   - Endpoints desarrollados:
     - `POST /api/technical/users`: Crear usuario (admin u otros).
     - `DELETE /api/technical/users/<id>`: Eliminar un usuario del sistema.
     - `POST /api/technical/users/<id>/block`: Bloquear usuario.
     - `POST /api/technical/users/<id>/unblock`: Desbloquear usuario.
     - `POST /api/technical/users/<id>/change-password`: Modificar la clave por una temporal forzando `"on_change"`.
   - Registrado el Blueprint en [app/\_\_init\_\_.py](file:///c:/Users/EQUIPO%20DELL/Documents/GitHub/Agenda-System/app/__init__.py) con el prefijo `/api/technical`.
4. **Documentación de la API:**
   - Actualizado [docs/API_FRONTEND.md](file:///c:/Users/EQUIPO%20DELL/Documents/GitHub/Agenda-System/docs/API_FRONTEND.md) documentando a detalle el flujo forzoso de contraseñas temporales y las firmas de endpoints de soporte técnico.

### Decisiones Técnicas
- **Login HTTP 200 con Bandera Especial para `on_change`:** Se prefirió retornar código de éxito 200 con el token JWT de acceso regular junto con la bandera `"require_password_change": true` en lugar de un código de error, facilitando al frontend almacenar el token del usuario en sesión y dirigirlo exclusivamente a la pantalla de restablecimiento de contraseña temporal.
- **Seguridad en Rutas de Soporte:** La protección se hace a través del decorador personalizado `@tecnico_required()` que consume la identidad del JWT y valida dinámicamente el campo `role` en la base de datos, garantizando que un token robado o ajeno de usuario `admin` no pueda consumir las rutas de administración técnica.
- **Regla Estricta de Parada**: Se detiene toda interacción con herramientas Git. El agente no realizará commits automáticos hasta recibir confirmación explícitamente.

## [2026-05-24] - Visualizador de Documentación Interactiva Premium y Diagramación ER en Local

### Contexto de Negocio
Para que el equipo de frontend, soporte y administradores cuente con una referencia dinámica y centralizada de la API y el modelo físico, se diseñó e implementó un visualizador web interactivo de documentación en local accesible directamente en la raíz del servidor backend (`http://localhost:5000/`).

### Cambios Realizados
1. **API de Documentación en Backend:**
   - Creado el módulo [app/routes/docs.py](file:///c:/Users/EQUIPO%20DELL/Documents/GitHub/Agenda-System/app/routes/docs.py) y Blueprint `docs_bp` registrado en la raíz `/` de Flask.
   - Endpoints JSON agregados:
     - `GET /api/docs/readme`: Lee y sirve el `README.md` del repositorio.
     - `GET /api/docs/api-frontend`: Sirve el `API_FRONTEND.md`.
     - `GET /api/docs/db-guide`: Sirve el `FRONTEND_DB_GUIDE.md`.
     - `GET /api/docs/dbml`: Sirve la especificación conceptual relacional `database.dbml`.
2. **Interfaz del Visualizador Web (`docs/index.html`):**
   - Desarrollada una consola premium con tema oscuro profundo, Glassmorphism, y tipografías Outfit/Inter.
   - **Manuales integrados:** Carga dinámica del `README.md` en el visor con botones interactivos para copiar bloques JSON en un clic.
   - **Diagramador ERD Interactivo:** Integración de **Mermaid.js** de forma local. Al seleccionarlo, se despliega un panel de pantalla dividida dual (Split Screen) tipo `dbdiagram.io`:
     - *Lado Izquierdo:* Código fuente físico de `database.dbml` con resaltado de sintaxis de PrismJS y copiado rápido.
     - *Lado Derecho:* Diagrama Entidad-Relación vectorial, nítido y auto-escalable con la estructura completa de tablas y relaciones de citas.
3. **Mantenimiento y Estándares de Estilo:**
   - Corregidas advertencias de compatibilidad CSS reordenando las propiedades `background-clip: text` y `-webkit-background-clip: text` en las clases `.logo-text` y `h1` de `docs/index.html` para solventar avisos del linter del editor.
   - Actualizado el `README.md` en su sección final agregando el manual interactivo de local y su enrutamiento.
   - Registro de la limpieza y sincronización final de todos los cambios con el repositorio remoto.

### Decisiones Técnicas
- **Mermaid.js vía Cliente:** Se optó por renderizar vectorialmente el diagrama ER en el navegador del usuario utilizando Mermaid.js a través de CDN, lo cual evita instalar costosas dependencias de compilación gráfica o backend monolítico en Python, garantizando excelente portabilidad en Windows y excelente fluidez en local.
- **División Dual (Split Screen):** Emular el flujo de dbdiagram.io permite que los desarrolladores puedan leer la definición exacta de tipos de datos a la izquierda mientras interactúan visualmente con el diagrama de relaciones a la derecha.
- **Limpieza Estricta de Warnings:** Ajuste del orden de propiedades CSS para satisfacer el linter estático del IDE y mantener un codebase libre de advertencias.


