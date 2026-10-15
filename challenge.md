# Desafío Técnico - Full Stack Take Home Challenge

## Descripción

Vas a desarrollar un sistema básico de gestión de notificaciones para usuarios autenticados.

El sistema debe permitir que cada usuario pueda gestionar y enviar notificaciones por distintos canales.

## Requerimientos funcionales

### 1. Autenticación de usuarios

- Registro de usuario con email y contraseña.
- Inicio de sesión que devuelva un token de acceso.
- Los endpoints deberán requerir un token válido para ser accedidos.

### 2. Gestión de notificaciones

- Crear una notificación (campos: título, contenido, canal).
- Modificar una notificación existente.
- Eliminar una notificación.
- Consultar todas las notificaciones propias.

### 3. Envío de notificaciones

Cada vez que una notificación sea creada, deberá ejecutarse el envío de la misma por el canal especificado.

Los canales disponibles son:

- Email
- SMS
- Push Notification

Cada canal debe requerir una lógica de envío distinta, simulando pasos específicos por canal. Por ejemplo:

- **Email:** Validar el formato del destinatario, generar un template y registrar el envío.
- **SMS:** Limitar el contenido a 160 caracteres, registrar el número y la fecha de envío.
- **Push Notification:** Validar el token de dispositivo, formatear el payload y registrar el estado del envío.

La lógica debe estar preparada para que agregar un nuevo canal no implique modificar la lógica existente.

## Requerimientos técnicos

- Base de datos relacional (PostgreSQL, MySQL, SQLite, etc.).
- API RESTful utilizando la tecnología de backend que prefieras.
- El candidato puede optar por agregar un frontend simple para consumir los endpoints, pero no es obligatorio.

## Criterios de evaluación

Se evaluará:

- La claridad y organización del código.
- La arquitectura elegida para manejar los distintos canales de notificación y sus lógicas.
- La correcta implementación de la autenticación y autorización.
- La escalabilidad y mantenibilidad del sistema.
- El uso adecuado de la base de datos.

El proyecto debe ser entregado aplicando las mejores prácticas que el candidato considere adecuadas, tanto a nivel de código, arquitectura, seguridad y documentación.

## Entrega

Incluí un `README.md` con:

- Instrucciones de instalación y ejecución.
- Breve descripción de las decisiones técnicas tomadas.
