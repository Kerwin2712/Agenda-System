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
