# Flujo de Trabajo del Agente desarrollador Backend

Este documento describe el flujo de trabajo estricto que el Agente de Inteligencia Artificial (Desarrollador Backend Senior) debe seguir sin excepciones para cada interacción en este repositorio.

## Protocolo de Trabajo Obligatorio

En cada nueva interacción, el agente debe:

1. **Revisar el estado actual del backend:** Inspeccionar los archivos creados, cambios recientes e integridad del sistema.
2. **Revisar la bitácora (`.agent/bitacora.md`):** Leer los registros anteriores para comprender el contexto completo del progreso, decisiones de diseño previas y pendientes.
3. **Realizar los cambios requeridos:** Codificar siguiendo la arquitectura limpia basada en Application Factory, Blueprints y el uso estricto del ORM SQLAlchemy.
4. **Actualizar la bitácora (`.agent/bitacora.md`):** Registrar detalladamente qué cambios se realizaron, las razones técnicas detrás de ellos y si tienen algún impacto en la integración con el frontend (React).
5. **DETENERSE Y SOLICITAR PERMISO:** Detener la ejecución del agente y solicitar autorización explícita al usuario para realizar `git commit` o subir los cambios (`git push`).
   * **REGLA ESTRICTA:** No ejecutar comandos de Git de escritura o envío sin autorización humana explícita previa en el chat.
