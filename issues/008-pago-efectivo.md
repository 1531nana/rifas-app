## PRD padre

`issues/prd.md`

## Que construir

Flujo de pago en efectivo: el comprador selecciona esta opcion y ve las instrucciones para coordinar el pago con el organizador. En el panel del admin, aparece la reserva pendiente de efectivo y el admin puede confirmarla manualmente. Ver `issues/011-notificaciones-whatsapp.md` para la notificacion que se dispara tras la confirmacion.

## Criterios de aceptacion

- [ ] Al seleccionar efectivo en el modal, el comprador ve un mensaje con instrucciones (ej. "Contacta al organizador para coordinar el pago. Tienes 5 dias.")
- [ ] `PATCH /reservations/{id}/confirm-cash` permite al admin dueno de la rifa marcar la reserva como `paid`
- [ ] Solo el admin dueno de la rifa puede confirmar pagos de esa rifa
- [ ] Tras confirmar, el numero aparece como rojo (vendido) en la grilla
- [ ] El panel del admin muestra la lista de compradores con estado de pago, incluyendo pendientes de efectivo
- [ ] El admin puede filtrar compradores por estado de pago en el panel

## Bloqueado por

- Bloqueado por `issues/006-reserva-numeros.md`

## Historias de usuario abordadas

- Historia de usuario 26
- Historia de usuario 27
