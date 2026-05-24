# Documentación de API para Frontend (React) - "Agenda tu cita"

Esta documentación detalla los endpoints de la API, las estructuras JSON requeridas, los formatos de respuesta y los flujos de autenticación mediante JWT para integrarse fluidamente con el frontend de React.

## 🚀 Información General

* **URL Base de Desarrollo Local:** `http://localhost:5000`
* **Prefijo General:** `/api`
* **Formato de Comunicación:** `application/json` (Todas las peticiones que envían un cuerpo de datos deben incluir la cabecera `Content-Type: application/json`).

---

## 🔒 Flujo de Autenticación JWT

Esta API utiliza **JSON Web Tokens (JWT)** para proteger los recursos. 

1. El frontend realiza una solicitud de inicio de sesión (`POST /api/auth/login`) con las credenciales del usuario.
2. Si las credenciales son válidas, la API responde con un `access_token` en formato JWT.
3. Para cualquier solicitud posterior a rutas protegidas, el frontend debe incluir este token en las cabeceras HTTP:

```http
Authorization: Bearer <tu_access_token_aqui>
```

> [!WARNING]
> Si el token expira (duración por defecto: 24 horas) o falta en la petición, la API retornará un código de respuesta HTTP `401 Unauthorized` o `422 Unprocessable Entity`.

---

## 📂 Endpoints de la API

### 1. Registro de Usuario
Permite a una nueva cuenta registrarse en el sistema.

* **Ruta:** `/api/auth/register`
* **Método:** `POST`
* **Cuerpo de la Petición (Request Body):**
```json
{
  "email": "usuario@ejemplo.com",
  "password": "mi_contraseña_segura",
  "name": "Juan Pérez"
}
```

* **Respuestas del Servidor:**

#### 🔴 Código `400 Bad Request` (Datos Inválidos o Faltantes)
Ocurre si no se envía el email o la contraseña, si el email no es válido o si la contraseña tiene menos de 6 caracteres.
```json
{
  "error": "Email y contrasenia son requeridos"
}
```
*O si el correo ya existe:*
```json
{
  "error": "El correo ya esta registrado"
}
```

#### 🟢 Código `201 Created` (Registro Exitoso)
```json
{
  "message": "Usuario registrado exitosamente",
  "user": {
    "id": 1,
    "email": "usuario@ejemplo.com",
    "name": "Juan Pérez",
    "created_at": "2026-05-23T18:18:16.123456",
    "updated_at": "2026-05-23T18:18:16.123456"
  }
}
```

---

### 2. Inicio de Sesión (Login)
Autentica al usuario y provee el token JWT.

* **Ruta:** `/api/auth/login`
* **Método:** `POST`
* **Cuerpo de la Petición (Request Body):**
```json
{
  "email": "usuario@ejemplo.com",
  "password": "mi_contraseña_segura"
}
```

* **Respuestas del Servidor:**

#### 🔴 Código `400 Bad Request` (Faltan Parámetros)
```json
{
  "error": "Email y contrasenia son requeridos"
}
```

#### 🔴 Código `401 Unauthorized` (Credenciales Incorrectas)
Ocurre si el correo no está registrado o la contraseña es inválida.
```json
{
  "error": "Credenciales invalidas"
}
```

#### 🟢 Código `200 OK` (Autenticación Exitosa)
Retorna el token JWT que el frontend debe guardar (ej. en localStorage, cookies seguras o estado global) y la información del usuario logueado.
```json
{
  "message": "Inicio de sesion exitoso",
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc3...",
  "token_type": "Bearer",
  "user": {
    "id": 1,
    "email": "usuario@ejemplo.com",
    "name": "Juan Pérez",
    "created_at": "2026-05-23T18:18:16.123456",
    "updated_at": "2026-05-23T18:18:16.123456"
  }
}
```

---

### 3. Estatus de Dashboard (Ruta Protegida)
Verifica que la sesión siga activa y recupera el perfil del usuario autenticado.

* **Ruta:** `/api/dashboard/status`
* **Método:** `GET`
* **Cabeceras Requeridas (Headers):**
  * `Authorization: Bearer <token>`

* **Respuestas del Servidor:**

#### 🔴 Código `401 Unauthorized` (Token Faltante, Expirado o Inválido)
Retornado automáticamente por la librería de JWT si la cabecera `Authorization` no está presente o no es válida.
```json
{
  "msg": "Missing Authorization Header"
}
```
*O si el token expiró:*
```json
{
  "msg": "Token has expired"
}
```

#### 🔴 Código `404 Not Found` (Usuario ya no existe)
Ocurre si el token es válido pero el usuario asociado a dicho token fue eliminado de la base de datos.
```json
{
  "error": "Usuario no encontrado en la sesion actual"
}
```

#### 🟢 Código `200 OK` (Acceso Permitido)
```json
{
  "status": "online",
  "message": "Token de autenticacion verificado exitosamente",
  "user": {
    "id": 1,
    "email": "usuario@ejemplo.com",
    "name": "Juan Pérez",
    "public_slug": "usuario",
    "created_at": "2026-05-23T18:18:16.123456",
    "updated_at": "2026-05-23T18:18:16.123456"
  }
}
```

---

### 4. API Pública (Sin Autenticación)

Estas rutas permiten que clientes externos (no registrados) puedan ver el catálogo de eventos/servicios de un comercio y agendar citas a través de enlaces directos. **No requieren cabecera `Authorization`.**

#### A. Directorio Público de Eventos de un Usuario
Obtiene todos los eventos de un administrador basados en su `public_slug` que estén **activos** (`is_active = true`) y sean **públicos** (`is_public = true`).

* **Ruta:** `/api/public/users/<public_slug>/events`
* **Método:** `GET`

##### Respuestas del Servidor:

###### 🔴 Código `404 Not Found` (Usuario no existe)
```json
{
  "error": "Usuario no encontrado"
}
```

###### 🟢 Código `200 OK` (Búsqueda Exitosa)
Retorna una lista con la información de todos los eventos configurados como públicos.
```json
[
  {
    "id": 1,
    "group_id": 1,
    "user_id": 1,
    "title": "Corte de Cabello Premium",
    "description": "Incluye lavado y perfilado de barba.",
    "slug": "corte-cabello-premium",
    "duration": 45,
    "buffer_time": 15,
    "is_active": true,
    "is_public": true,
    "created_at": "2026-05-24T10:20:00.123456",
    "updated_at": "2026-05-24T10:20:00.123456"
  }
]
```

---

#### B. Detalle de un Evento Específico (Enlace Directo)
Obtiene la información de un servicio específico utilizando el slug del usuario y del evento. Filtra estrictamente por evento **activo** (`is_active = true`), ignorando si es público.

* **Ruta:** `/api/public/users/<public_slug>/events/<event_slug>`
* **Método:** `GET`

##### Respuestas del Servidor:

###### 🔴 Código `404 Not Found` (Usuario no existe, o evento inexistente/inactivo)
```json
{
  "error": "Evento no encontrado o inactivo"
}
```

###### 🟢 Código `200 OK` (Búsqueda Exitosa)
```json
{
  "id": 2,
  "group_id": 1,
  "user_id": 1,
  "title": "Tinte Especializado (Privado)",
  "description": "Servicio de tinte personalizado.",
  "slug": "tinte-especializado-privado",
  "duration": 90,
  "buffer_time": 30,
  "is_active": true,
  "is_public": false,
  "created_at": "2026-05-24T10:25:00.123456",
  "updated_at": "2026-05-24T10:25:00.123456"
}
```

---

### 5. API de Soporte Técnico (Solo Rol: `tecnico`)

Estas rutas permiten al equipo de soporte técnico gestionar las cuentas de la plataforma, suspender accesos por impago y asignar contraseñas temporales. **Todas requieren la cabecera `Authorization: Bearer <token_tecnico>` del usuario con rol técnico.**

#### A. Crear Usuario (Admin o Técnico)
*   **Ruta:** `/api/technical/users`
*   **Método:** `POST`
*   **Request Body:**
    ```json
    {
      "email": "nuevo.admin@ejemplo.com",
      "password": "contraseñasupersegura",
      "name": "Clínica Dental Gonzalez",
      "role": "admin"
    }
    ```
*   **Respuesta Exitosa (`201 Created`):**
    ```json
    {
      "message": "Usuario creado exitosamente por soporte tecnico",
      "user": {
        "id": 10,
        "email": "nuevo.admin@ejemplo.com",
        "name": "Clínica Dental Gonzalez",
        "public_slug": "nuevoadmin",
        "role": "admin",
        "is_blocked": false,
        "password_status": "active",
        "created_at": "2026-05-24T12:00:00.000Z",
        "updated_at": "2026-05-24T12:00:00.000Z"
      }
    }
    ```

---

#### B. Eliminar Usuario
*   **Ruta:** `/api/technical/users/<id>`
*   **Método:** `DELETE`
*   **Respuesta Exitosa (`200 OK`):**
    ```json
    {
      "message": "Usuario eliminado exitosamente"
    }
    ```

---

#### C. Bloquear Usuario (Suspensión por Pago / Administrativo)
*   **Ruta:** `/api/technical/users/<id>/block`
*   **Método:** `POST`
*   **Respuesta Exitosa (`200 OK`):**
    ```json
    {
      "message": "Usuario bloqueado y suspendido exitosamente",
      "user": {
        "id": 10,
        "email": "admin@ejemplo.com",
        "is_blocked": true,
        "role": "admin",
        "password_status": "active"
      }
    }
    ```

---

#### D. Desbloquear Usuario (Reactivación de Cuenta)
*   **Ruta:** `/api/technical/users/<id>/unblock`
*   **Método:** `POST`
*   **Respuesta Exitosa (`200 OK`):**
    ```json
    {
      "message": "Usuario desbloqueado y reactivado exitosamente",
      "user": {
        "id": 10,
        "email": "admin@ejemplo.com",
        "is_blocked": false,
        "role": "admin",
        "password_status": "active"
      }
    }
    ```

---

#### E. Cambiar Contraseña Manualmente (Forzar Cambio Obligatorio)
Establece una contraseña temporal de soporte y marca el estatus del usuario como `"on_change"`.
*   **Ruta:** `/api/technical/users/<id>/change-password`
*   **Método:** `POST`
*   **Request Body:**
    ```json
    {
      "new_password": "clave_temporal_123"
    }
    ```
*   **Respuesta Exitosa (`200 OK`):**
    ```json
    {
      "message": "Contrasenia modificada exitosamente. Se requerira cambio obligatorio en el proximo login.",
      "user": {
        "id": 10,
        "email": "admin@ejemplo.com",
        "is_blocked": false,
        "role": "admin",
        "password_status": "on_change"
      }
    }
    ```

---

### 6. Flujo de Cambio de Contraseña Obligatoria (Cliente Admin)

Cuando soporte técnico asigna una contraseña manual, el sistema fuerza su restablecimiento de la siguiente manera:

1.  **Inicio de sesión del cliente:** El cliente inicia sesión usando su correo y la contraseña temporal.
    *   **Respuesta de la API (`200 OK` con bandera especial):**
        ```json
        {
          "message": "Cambio de contrasenia temporal obligatorio requerido",
          "require_password_change": true,
          "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
          "token_type": "Bearer",
          "user": {
            "id": 10,
            "email": "admin@ejemplo.com",
            "password_status": "on_change",
            "is_blocked": false,
            "role": "admin"
          }
        }
        ```
2.  **Bloqueo y Redirección en Frontend (React):** El frontend detecta la presencia del flag `"require_password_change": true`, bloquea la navegación habitual al panel y redirige al usuario forzosamente a un formulario para establecer una nueva clave.
3.  **Establecer Contraseña Definitiva:** El cliente ingresa su nueva contraseña definitiva en el formulario. El frontend consume el endpoint de reset enviando el token obtenido en el login:
    *   **Ruta:** `/api/auth/reset-temp-password`
    *   **Método:** `POST`
    *   **Headers:** `Authorization: Bearer <access_token>`
    *   **Request Body:**
        ```json
        {
          "new_password": "mi_nueva_clave_definitiva_segura"
        }
        ```
    *   **Respuesta Exitosa (`200 OK`):**
        ```json
        {
          "message": "Contrasenia restablecida exitosamente. Ahora tu cuenta esta activa.",
          "user": {
            "id": 10,
            "email": "admin@ejemplo.com",
            "password_status": "active",
            "is_blocked": false,
            "role": "admin"
          }
        }
        ```

---

## 🛠️ Errores Genéricos del Servidor

La API tiene controladores globales para asegurar que cualquier fallo no controlado responda con un JSON en lugar de una página HTML de error de Flask.

### Código `404 Not Found` (Ruta inexistente)
```json
{
  "error": "Recurso no encontrado"
}
```

### Código `500 Internal Server Error` (Error en el servidor)
```json
{
  "error": "Error interno del servidor"
}
```
