## Decisiones técnicas

### Arquitectura

El proyecto está organizado **por módulo** (`auth`, `notification`, `delivery`, `channels`), de modo que cada carpeta corresponde a una parte del flujo de la aplicación y es fácil ubicar dónde vive cada responsabilidad.

Dentro de cada módulo, el código se separa en tres capas:

- **Router:** maneja lo HTTP: rutas, códigos de estado, validación de entrada con Pydantic y traducción de errores de negocio a respuestas HTTP.
- **Service:** contiene la lógica de negocio y orquesta los canales de envío. Es el único que maneja la transacción (`commit`).
- **Repository:** encapsula el acceso a datos con SQLAlchemy. Nunca hace `commit`.

Cada repository se define a partir de una interfaz (`ABC`) y se inyecta en el service mediante el sistema de dependencias de FastAPI. Esto permite testear el service con implementaciones en memoria, sin base de datos, y cambiar la implementación de persistencia respetando el mismo contrato.

Stack: FastAPI, SQLAlchemy 2.0 async con psycopg 3, PostgreSQL y Alembic para migraciones.

### Modelo de datos

| Tabla | Contenido |
|---|---|
| `users` | Usuario, email (único, guardado en minúsculas) y contraseña hasheada |
| `notifications` | Título, contenido, canal, destinatario, estado actual y `user_id` (FK). Incluye `deleted_at` para soft delete |
| `deliveries` | Un registro por cada intento de envío: estado, detalles propios del canal (JSONB), error y fecha. FK a `notifications` |

Todas las fechas usan `timestamptz`, y las claves foráneas tienen índice, ya que se usan en cada consulta filtrada por usuario o por notificación.

### Canales de notificación: patrón Strategy

Cada canal (Email, SMS, Push) implementa la misma interfaz, `INotificationChannel`, con dos métodos:

- `validate(notification)`: aplica las reglas propias del canal. Se ejecuta **antes de guardar**.
- `send(notification)`: ejecuta los pasos del envío y devuelve un `DeliveryResult` (estado, detalles y error).

El service no conoce los canales concretos: los obtiene por nombre desde un **registry**, y llama siempre a los mismos dos métodos. Gracias al polimorfismo, no hay una cadena de `if/elif` por canal.

**Agregar un canal nuevo** consiste en crear su clase y registrarla en el registry. El service, el router y los demás canales no se modifican.

Los canales no acceden a la base de datos: reciben datos y devuelven un resultado. El service es quien persiste el envío. Esto los hace fáciles de testear de forma aislada.

El canal se guarda como texto validado por el registry, y no como un Enum de base de datos, para que agregar un canal no requiera una migración.

| Canal | Validación | Envío (simulado) |
|---|---|---|
| Email | Formato del destinatario con `email-validator` | Genera un template HTML con título y contenido escapados |
| SMS | Teléfono en formato E.164 y contenido de hasta 160 caracteres | Registra el número y el largo del mensaje |
| Push | Formato del token de dispositivo | Arma el payload (token, título, cuerpo y datos) |

Cada canal permite simular un fallo con un destinatario especial (por ejemplo, un token que empieza con `fail-`), para probar el registro del estado `failed`.

### Envío y registro: por qué existe `deliveries`

La tabla `deliveries` separa **lo que creó el usuario** (la notificación) de **lo que ocurrió al enviarla** (cada intento de envío):

- `notifications.status` refleja el estado actual (`pending`, `sent`, `failed`), y `deliveries` conserva el historial.
- Lo propio de cada canal (el template del email, el payload del push, el número del SMS) se guarda en `details` (JSONB). Así, `content` conserva siempre el mensaje original del usuario, y un canal nuevo no requiere cambios en el esquema.
- Un envío es un hecho que ya ocurrió: queda registrado para trazabilidad, soporte y auditoría.
- Permite registrar varios intentos de una misma notificación, por ejemplo ante futuros reintentos.

La creación ocurre en **una sola transacción**: se valida, se guarda la notificación como `pending`, se envía, se registra la delivery y se actualiza el estado. Una notificación inválida nunca se persiste. Si el proveedor falla durante el envío, el error se registra en el log y queda guardado como una delivery `failed`, en lugar de perderse.

### Soft delete

Eliminar una notificación completa `deleted_at` en lugar de borrar la fila, para conservar el historial de envíos asociado. El filtro de registros eliminados se aplica en el repository, de modo que vive en un único lugar.

### Actualización

- Se aplican solo los campos enviados (`exclude_unset`). Enviar `null` de forma explícita en un campo obligatorio se rechaza con 422.
- Después de aplicar los cambios, se vuelve a validar el resultado final con las reglas del canal correspondiente; por ejemplo, cambiar un SMS a Email exige un destinatario de email válido.
- Editar una notificación **no la reenvía**: el envío ocurre solo al crearla.

### Autenticación y autorización

- **JWT** con PyJWT. El token es stateless, incluye el id del usuario y una fecha de expiración, y se firma con una clave definida por variable de entorno.
- Contraseñas hasheadas con **argon2** (`pwdlib`).
- Login con el flujo estándar OAuth2 *password* de FastAPI. El email se envía en el campo `username`, lo que permite autenticarse desde Swagger.
- Los endpoints de notificaciones requieren un token válido a través de la dependencia `get_current_user`.
- El `user_id` se obtiene siempre del token, nunca del body ni de la URL, para evitar el acceso a recursos ajenos (IDOR). Una notificación de otro usuario responde **404**, sin revelar que existe.
- El login responde con el mismo mensaje si el email no existe o si la contraseña es incorrecta, para no revelar qué emails están registrados.

### Validación y seguridad

- Los schemas de Pydantic definen qué campos controla el cliente. `status` y `user_id` los asigna el servidor, lo que evita la asignación masiva de campos (*mass assignment*).
- Validación en capas: Pydantic valida tipos y largos; cada canal valida su formato con una lista blanca; SQLAlchemy usa consultas parametrizadas contra la inyección SQL.
- El contenido del usuario se escapa al generar el HTML del email, para prevenir la inyección de HTML.
- El listado está paginado, con un límite máximo por página.

### Manejo de errores

El service lanza excepciones propias del dominio (`NotificationNotFoundError`, `UnknownChannelError`, `NotificationValidationError`), sin conocer HTTP. El router las traduce a respuestas: 404 para un recurso inexistente o ajeno, y 422 para un canal desconocido o datos que no cumplen las reglas del canal.

### Limitaciones conocidas y próximos pasos

- **Envío asíncrono:** hoy el envío ocurre dentro del request, así que la respuesta espera al proveedor. Para escalar, la notificación se guardaría como `pending` y un worker la enviaría desde una cola (por ejemplo, RabbitMQ), con reintentos.
- **Proveedores reales:** cada canal delegaría el envío en un cliente de proveedor detrás de una interfaz (por ejemplo, `EmailProvider`, con implementaciones para SendGrid o SES). Así se podría cambiar de proveedor sin modificar el canal, y simular las respuestas en los tests.
- **Desacople completo de la persistencia:** el service todavía recibe la sesión para hacer el commit. Para independizarlo del todo de SQLAlchemy, se incorporaría un patrón *Unit of Work*.
- **Límite real del SMS:** 160 caracteres aplica al alfabeto GSM-7. Con emojis o ciertos caracteres especiales, el mensaje se codifica en UCS-2 y el límite baja a 70.
- **Tokens:** no hay refresh tokens ni revocación; un token es válido hasta que expira.
- **Privacidad:** las notificaciones eliminadas conservan datos personales del destinatario. En producción se agregaría un proceso de purga o anonimización periódica.
- Rate limiting por usuario y templates de email con Jinja2.