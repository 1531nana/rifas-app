# Bitacora de Transferencia

## Handoff - Issues #1 y #2

Fecha: 2026-05-18

Alcance cerrado:
- Issue #1: scaffold completo con FastAPI, Alembic, PostgreSQL, React+Vite+TailwindCSS. Endpoint `GET /health` operativo. Variables de entorno documentadas en `.env.example`. README con instrucciones de setup local.
- Issue #2: flujo de autenticacion de admins con `POST /auth/register`, `POST /auth/login` (JWT + refresh token), `POST /auth/refresh` y cierre de sesion. Contrasenas hasheadas con bcrypt. Rutas protegidas en backend y frontend con redireccion al login si no hay sesion activa.

Decisiones consolidadas:
- JWT de corta duracion (access) + refresh token almacenado en base de datos.
- Estructura modular desde el inicio: `models/domain.py`, `models/schemas.py`, `services/`, `api/`, `core/`.
- Migraciones con Alembic; no se usa `create_all` directo en arranque.
- Frontend protege rutas con un componente guardian que lee el token del almacenamiento local.

Pendientes exactos:
- Issues #3 en adelante bloqueados hasta merge de esta base.
- Configurar variables de entorno reales en Railway/Vercel antes de despliegue en produccion.

---

## Handoff - Issue #3

Fecha: 2026-05-22

Alcance cerrado:
- Issue #3: CRUD completo de rifas para el admin. `POST /raffles` crea rifa con `public_token` unico generado automaticamente. `GET /raffles` y `GET /raffles/{id}` con aislamiento por admin. `PATCH /raffles/{id}` permite editar descripcion, tipo de loteria y fecha; rechaza cambios de precio o cantidad de numeros si existen reservas activas.
- Frontend: lista de rifas en dashboard, formulario de creacion y formulario de edicion con campos restringidos segun estado.

Decisiones consolidadas:
- `public_token` generado con `secrets.token_urlsafe` al crear la rifa; inmutable despues.
- Validacion de reservas activas en `services/raffles.py` antes de aplicar el patch; la capa `api/` solo delega.
- Un admin no puede acceder a rifas de otro admin; filtro aplicado a nivel de servicio, no de router.

Pendientes exactos:
- Issues #4 y #5 desbloqueados: vista publica y grilla de numeros.
- Agregar indices a `public_token` en la siguiente migracion de Alembic para busquedas eficientes.

---

## Handoff - Issues #4 y #5

Fecha: 2026-05-24

Alcance cerrado:
- Issue #4: endpoint publico `GET /public/raffles/{public_token}` sin autenticacion. Retorna 404 si el token no existe. Frontend renderiza `/r/{public_token}` con nombre, premio, fecha, valor y tipo de loteria. Muestra mensaje si la rifa esta cerrada. Pagina responsive.
- Issue #5: endpoint `GET /public/raffles/{public_token}/numbers` con estados `available`, `reserved`, `sold`. Reservas con `expires_at` pasado se devuelven como `available` (verificacion lazy). Grilla visual con colores (verde/amarillo/rojo) responsive en movil; solo numeros verdes son clickeables.

Decisiones consolidadas:
- Verificacion lazy de expiracion en el endpoint de numeros: no se depende exclusivamente del job periodico (issue #9) para mostrar disponibilidad correcta.
- El estado del numero se calcula en `services/raffles.py`, no en el router ni en el frontend.
- La pagina publica no requiere login; el `public_token` opaco es la unica llave de acceso.

Pendientes exactos:
- Issue #6 desbloqueado: flujo de reserva desde la grilla.
- Evaluar paginacion o virtualizacion de la grilla si las rifas superan los 1000 numeros.

---

## Handoff - Issues #6, #7 y #8

Fecha: 2026-05-24

Alcance cerrado:
- Issue #6: `POST /public/reservations` crea reserva con datos del comprador (nombre, celular, email opcional) y metodo de pago. Retorna 409 si el numero ya tiene reserva activa. `expires_at = now() + 48h` para pago digital, `now() + 5 dias` para efectivo. El numero pasa a amarillo inmediatamente. Validacion de formato de celular para WhatsApp.
- Issue #7: `POST /public/reservations/{id}/checkout` genera enlace de pago Wompi. `POST /webhooks/wompi` procesa resultado con validacion de firma. Estado `APPROVED` marca reserva como `paid` y numero como rojo; `DECLINED`/`VOIDED` libera el numero. Paginas de confirmacion y error en frontend.
- Issue #8: flujo de pago en efectivo. Al seleccionar efectivo el comprador ve instrucciones de contacto con el organizador. `PATCH /reservations/{id}/confirm-cash` permite al admin dueno de la rifa marcar la reserva como `paid`. Panel del admin lista compradores con estado de pago y filtro por estado.

Decisiones consolidadas:
- Validacion de firma Wompi en `services/` antes de modificar estado; si la firma falla se retorna 400 sin cambiar datos.
- Solo el admin dueno de la rifa puede confirmar pagos en efectivo; control aplicado en el servicio comparando `raffle.admin_id`.
- El modal de reserva vive en el frontend como componente separado; la logica de plazos (`48h` / `5 dias`) se define en `lib/constants.js`.
- Las credenciales de Wompi (`WOMPI_PUBLIC_KEY`, `WOMPI_PRIVATE_KEY`, `WOMPI_EVENTS_SECRET`) van en variables de entorno; en desarrollo se usan claves sandbox.

Pendientes exactos:
- Issue #9 desbloqueado: job de expiracion periodica de reservas.
- Configurar webhook de Wompi en produccion apuntando al endpoint real antes del lanzamiento.
- Issue #11 (notificaciones WhatsApp al confirmar efectivo) pendiente de implementar.

---

## Handoff - Issue #9

Fecha: 2026-05-18

Alcance cerrado:
- Issue #9: job periodico `expire_old_reservations` en `core/scheduler.py` que corre cada 15 minutos. Marca como `expired` todas las reservas con `status=pending` y `expires_at < now()`. Idempotente: multiples ejecuciones no producen efectos duplicados. Errores del job se registran en logs sin detener el servidor.

Decisiones consolidadas:
- Scheduler iniciado junto con el ciclo de vida de FastAPI (`lifespan`); no requiere proceso separado.
- El job complementa la verificacion lazy del endpoint de numeros: ambas capas garantizan consistencia de estado.
- No se emiten notificaciones al expirar una reserva; el comprador simplemente pierde el numero.

Pendientes exactos:
- Issues #10 y #11 desbloqueados: imagen del premio y notificaciones WhatsApp.
- Evaluar frecuencia del job en produccion segun volumen de reservas concurrentes.

---

## Handoff - Issue #12

Fecha: 2026-06-06

Alcance cerrado:
- Issue #12: job diario `send_payment_reminders()` en `services/recordatorio.py`. Busca reservas `status=pending` con `reminder_sent_at IS NULL` cuya rifa sortea en 14–16 días. Envía WhatsApp con template `payment_reminder` y marca `reminder_sent_at`. Scheduler actualizado con job cada 24h.
- Nuevo campo `reminder_sent_at: Optional[datetime]` en `Reservation` (domain.py).
- Config `meta_template_payment_reminder = "payment_reminder"` en `core/config.py`.
- 50 tests pasando. Todas las issues del sprint completadas (#12–#14).

Decisiones consolidadas:
- `services/recordatorio.py` sigue el mismo patrón que `services/ganador.py`: un módulo por caso de uso, funciones privadas `_`, función pública como punto de entrada único.
- El job no bloquea el resto si Meta Cloud API falla: loguea advertencia por reserva y continúa con las demás.
- `reminder_sent_at` se escribe solo si el envío fue exitoso, garantizando idempotencia real.

Pendientes exactos:
- Candidatos arquitectónicos 1, 2 y 3 del checkpoint no aplicados (deuda técnica documentada).
- Build del frontend falla por Node.js v16.9.0 (requiere v18+); problema preexistente del entorno, no de los cambios de este sprint.
- PR de la rama `feature/handoff-issues` pendiente de abrir hacia `develop`.

---

## Handoff - Issues #13, #14 + Checkpoint Arquitectónico

Fecha: 2026-06-06

Alcance cerrado:
- Issue #14: endpoints `GET /raffles/{id}/stats` y `GET /raffles/{id}/buyers`. Schemas `RaffleStatsRead` y `BuyerRead` en `schemas.py`. Funciones `get_raffle_stats()` y `get_raffle_buyers()` en `services/raffles.py`.
- Issue #13: campo `winner_number` en modelo `Raffle`. Nuevo servicio `services/ganador.py` con `register_winner()`. Endpoint `POST /raffles/{id}/winner`. Vista pública expone `winner_number`. Config `meta_template_winner_notification`.
- Checkpoint arquitectónico: candidato 4 aplicado — `_reserva_vigente()` como función pura; `get_number_states()`, `get_raffle_detail()`, `get_raffle_stats()` y `reserve_number()` ya no llaman `expire_old_reservations()`.

Decisiones consolidadas:
- Un módulo por caso de uso nuevo: `services/ganador.py` es el patrón a seguir.
- Las funciones de lectura no producen efectos de escritura. La expiración lazy se resuelve en memoria.
- `expire_old_reservations()` es exclusivo del scheduler.
- Monkeypatches en tests deben apuntar al módulo que importa `send_whatsapp`, no al de `notifications`.

Pendientes exactos:
- Issue #12 pendiente: job diario de recordatorio de pago (WhatsApp a compradores con rifa en 15 días).
- Agregar `reminder_sent_at` a `Reservation` y recrear BD antes de tests.
- Candidatos 1, 2 y 3 del checkpoint arquitectónico aún no aplicados (deuda técnica conocida).

---

## Handoff - Issues #10 y #11

Fecha: 2026-05-25

Alcance cerrado:
- Issue #10: imagen opcional del premio, endpoint `POST /raffles/{id}/image`, validacion JPG/PNG/WebP, limite 5MB, URL expuesta en `/public/raffles/{public_token}` y vista publica con imagen o placeholder.
- Issue #11: modulo `app.services.notifications` con `send_whatsapp(phone, template, params)`, sandbox local, envio Meta Cloud API cuando hay credenciales, y confirmacion automatica al aprobar pago en efectivo.
- Entregables de contexto: `handoffs.md` y `architecture-checkpoint.md` en la raiz.

Decisiones consolidadas:
- Mantener `app.services.raffles` como servicio de aplicacion para el flujo de rifa/reserva/pago ya existente.
- Agregar `app.services.notifications` como puerto simple para WhatsApp, sin bloquear la transaccion principal si Meta falla.
- Usar Cloudinary si `CLOUDINARY_CLOUD_NAME` y `CLOUDINARY_UPLOAD_PRESET` existen; en desarrollo se guarda en `UPLOAD_DIR` y se sirve por `/uploads`.
- Mantener la ruta existente `POST /raffles/{raffle_id}/reservations/{reservation_id}/confirm-cash` y sumar compatibilidad con `PATCH /reservations/{id}/confirm-cash`.

Pendientes exactos:
- Configurar credenciales reales de Cloudinary y Meta antes de produccion.
- Confirmar en Meta Business que el template `payment_confirmation` tenga el mismo orden de parametros: comprador, numero, rifa, fecha de sorteo.
- Revisar issues posteriores (#12-#14) en otro ciclo; no se tocaron en este cambio.
