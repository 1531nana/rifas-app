# Bitacora de Transferencia

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
