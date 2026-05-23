## PRD padre

`issues/prd.md`

## Que construir

Flujo de pago en efectivo: el comprador selecciona esta opcion y ve las instrucciones para coordinar el pago con el organizador. En el panel del admin, aparece la reserva pendiente de efectivo y el admin puede confirmarla manualmente. Ver `issues/011-notificaciones-whatsapp.md` para la notificacion que se dispara tras la confirmacion.

## Criterios de aceptacion

- [x] Al seleccionar efectivo en el modal, el comprador ve un mensaje con instrucciones (ej. "Contacta al organizador para coordinar el pago. Tienes 5 dias.") ✅
- [x] `PATCH /reservations/{id}/confirm-cash` permite al admin dueno de la rifa marcar la reserva como `paid` ✅
- [x] Solo el admin dueno de la rifa puede confirmar pagos de esa rifa ✅
- [x] Tras confirmar, el numero aparece como rojo (vendido) en la grilla ✅
- [x] El panel del admin muestra la lista de compradores con estado de pago, incluyendo pendientes de efectivo ✅
- [x] El admin puede filtrar compradores por estado de pago en el panel ✅

## Status

✅ COMPLETADO (2026-05-21)

## Bloqueado por

- Bloqueado por `issues/006-reserva-numeros.md`

## Historias de usuario abordadas

- Historia de usuario 26
- Historia de usuario 27
