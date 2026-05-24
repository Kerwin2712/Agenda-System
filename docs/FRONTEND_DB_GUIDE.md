# Guía de Base de Datos para el Desarrollador de Frontend

Esta guía detalla la estructura de la base de datos de nuestro sistema de citas con el fin de facilitar la integración de la API con el Frontend. Aquí encontrarás los formatos de datos requeridos, flujos lógicos clave y las estructuras de los endpoints teóricos correspondientes.

---

## 1. Estructura de Tablas y Atributos

### Tabla: `users` (Administradores/Dueños de Comercio)
Guarda la información de inicio de sesión y datos básicos del comercio.
*   **`id`** (`Integer`): ID autoincrementable.
*   **`email`** (`String`): Correo único de acceso del administrador.
*   **`name`** (`String`): Nombre del comercio o administrador.
*   **`role`** (`String`): Rol del usuario (por defecto `"admin"`).

### Tabla: `events` (Tipos de Cita / Servicios)
Guarda los diferentes servicios o tipos de citas configurables creados por el admin.
*   **`id`** (`Integer`): ID autoincrementable.
*   **`user_id`** (`Integer`): ID del administrador dueño del servicio.
*   **`title`** (`String`): Nombre del servicio (ej. *"Asesoría Técnica de 30 min"*).
*   **`description`** (`Text`): Descripción detallada visible para el cliente (opcional).
*   **`duration`** (`Integer`): Duración de la cita en **minutos**.
*   **`buffer_time`** (`Integer`): Tiempo de espera o descanso obligatorio después de cada cita en **minutos**.
*   **`is_active`** (`Boolean`): Indica si el servicio está activo y disponible para reservas.

### Tabla: `event_availabilities` (Disponibilidad Horaria Recurrente)
Guarda los rangos horarios recurrentes semanales asignados a cada tipo de cita.
*   **`id`** (`Integer`): ID autoincrementable.
*   **`event_id`** (`Integer`): ID del evento/servicio asociado.
*   **`day_of_week`** (`Integer`): Día de la semana en formato entero (**1 = Lunes**, **7 = Domingo**).
*   **`start_time`** (`Time`): Hora de inicio de atención (en formato `"HH:MM:SS"`, ej. `"09:00:00"`).
*   **`end_time`** (`Time`): Hora de fin de atención (en formato `"HH:MM:SS"`, ej. `"17:00:00"`).

### Tabla: `appointments` (Citas Reservadas)
Guarda las citas agendadas por los clientes externos.
*   **`id`** (`Integer`): ID autoincrementable.
*   **`event_id`** (`Integer`): ID del tipo de cita reservada.
*   **`client_name`** (`String`): Nombre completo del cliente.
*   **`client_email`** (`String`): Correo electrónico del cliente.
*   **`client_phone`** (`String`): **Teléfono del cliente** (dato crítico para que el admin lo contacte).
*   **`start_time`** (`DateTime`): Fecha y hora de inicio de la cita (formato ISO-8601 UTC: `"YYYY-MM-DDTHH:MM:SSZ"`).
*   **`end_time`** (`DateTime`): Fecha y hora de fin de la cita (calculada automáticamente sumando la duración al inicio).
*   **`status`** (`String`): Estado de la cita (valores posibles: `"pending"`, `"confirmed"`, `"cancelled"`).
*   **`notes`** (`Text`): Mensaje o comentarios del cliente al reservar (opcional).

---

## 2. Formato de Datos Requeridos (Estándares)

Para asegurar una comunicación limpia con la API, el Frontend debe enviar los datos en los siguientes formatos estandarizados:

1.  **Fechas y Horas Completas (Citas):**
    *   Utilizar formato **ISO-8601 UTC**.
    *   *Ejemplo:* `2026-05-24T14:30:00Z`
2.  **Horas de Disponibilidad Semanal:**
    *   Utilizar formato de 24 horas `"HH:MM:SS"` o `"HH:MM"`.
    *   *Ejemplo:* `09:00:00` o `18:30:00`
3.  **Días de la semana:**
    *   Números enteros del **1 (Lunes)** al **7 (Domingo)**.

---

## 3. Flujos de Trabajo Recomendados para el Frontend

### Flujo A: Creación y Configuración del Servicio (Admin)
1.  **Crear el Evento:** El administrador completa un formulario con el título, descripción, duración y tiempo de espera (buffer). El frontend envía una petición POST al endpoint de creación de eventos.
2.  **Configurar Disponibilidad:** El administrador asigna su horario semanal. El frontend envía un array con la disponibilidad recurrente.
    *   *Ejemplo de payload recomendado a enviar:*
        ```json
        {
          "availabilities": [
            { "day_of_week": 1, "start_time": "09:00", "end_time": "13:00" },
            { "day_of_week": 1, "start_time": "14:00", "end_time": "18:00" },
            { "day_of_week": 2, "start_time": "09:00", "end_time": "17:00" }
          ]
        }
        ```

### Flujo B: Renderizado del Calendario y Generación de Slots (Cliente)
Para mostrar al cliente las horas disponibles para reservar:
1.  El cliente selecciona un servicio (`event_id`) y un día específico en el calendario.
2.  El frontend realiza una petición HTTP al backend para obtener las horas disponibles para ese día.
3.  **¿Qué calcula el backend?**
    *   Obtiene la disponibilidad base para ese día de la semana desde `event_availabilities`.
    *   Busca las citas ya reservadas en `appointments` para esa fecha específica.
    *   Calcula los bloques libres (slots) restando las citas existentes y aplicando el `buffer_time` configurado.
4.  El frontend muestra los slots de tiempo resultantes para que el cliente seleccione uno.

### Flujo C: Confirmación de Cita (Cliente)
Cuando el cliente elige una hora disponible, se le solicita llenar un formulario con su nombre, correo y número telefónico. El frontend envía una petición POST para crear la cita:
```json
{
  "event_id": 3,
  "client_name": "Juan Pérez",
  "client_email": "juan.perez@example.com",
  "client_phone": "+56912345678",
  "start_time": "2026-05-26T10:00:00Z",
  "notes": "Prefiero que nos contactemos por WhatsApp antes de la cita."
}
```

### Flujo D: Panel de Control e Interacción con el Cliente (Admin)
En el panel del comercio, el administrador debe poder ver la lista de citas agendadas y gestionarlas:
1.  El frontend realiza una petición GET a las citas del administrador.
2.  La UI debe mostrar los datos críticos de forma clara:
    *   **Fecha y hora** de la cita.
    *   **Servicio** agendado.
    *   **Nombre del cliente**.
    *   **Teléfono del cliente** renderizado de forma accionable (ej. con un botón directo a WhatsApp `https://wa.me/telefono` o un enlace de llamada `tel:telefono`).
    *   **Acciones:** Botón para confirmar (`status = "confirmed"`) o cancelar (`status = "cancelled"`).
