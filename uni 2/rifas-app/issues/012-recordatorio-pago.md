## PRD padre

`issues/prd.md`

## Que construir

Job programado diario que detecta compradores con reservas activas sin pagar cuya rifa sortea en exactamente 15 dias, y les envia un recordatorio por WhatsApp. Usa la infraestructura de notificaciones de `issues/011-notificaciones-whatsapp.md`.

## Criterios de aceptacion

- [x] El job corre una vez al dia ✅
- [x] El job identifica todas las reservas con `status=pending` cuya rifa tiene `draw_date` en 15 dias (con tolerancia de +/- 1 dia para no depender de hora exacta) ✅
- [x] Se envia un WhatsApp de recordatorio a cada comprador identificado ✅
- [x] El mensaje incluye: nombre del comprador, numero de boleta, nombre de la rifa, fecha del sorteo y plazo para pagar ✅
- [x] No se envia mas de un recordatorio por reserva (el job no re-notifica si ya se notifico) ✅
- [x] El job es idempotente ✅
- [x] Los errores de envio individual no detienen el procesamiento del resto ✅

## Status

✅ COMPLETADO (2026-05-21)

## Bloqueado por

- Bloqueado por `issues/011-notificaciones-whatsapp.md`

## Historias de usuario abordadas

- Historia de usuario 17
- Historia de usuario 29
