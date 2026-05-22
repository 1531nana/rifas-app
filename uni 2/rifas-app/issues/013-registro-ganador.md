## PRD padre

`issues/prd.md`

## Que construir

Flujo para que el admin registre el numero ganador del sorteo y cierre la rifa. Al registrar el ganador, el sistema verifica que ese numero tiene una boleta pagada, marca la rifa como `closed` y envia una notificacion WhatsApp al comprador ganador. Usa la infraestructura de `issues/011-notificaciones-whatsapp.md`.

## Criterios de aceptacion

- [x] `POST /raffles/{id}/winner` recibe el numero ganador y cierra la rifa ✅
- [x] Si el numero ganador no tiene una reserva con `status=paid`, retorna error (la boleta no participaba) ✅
- [x] La rifa queda con `status=closed` tras registrar el ganador ✅
- [x] Se envia un WhatsApp al comprador ganador con: felicitacion, nombre del premio, datos de contacto del organizador ✅
- [x] Una rifa cerrada no permite nuevas reservas ni pagos ✅
- [x] La vista publica de una rifa cerrada muestra el numero ganador ✅
- [x] El boton de "Registrar ganador" esta disponible en el panel del admin para rifas activas ✅
- [x] Solo el admin dueno de la rifa puede registrar el ganador ✅

## Status

✅ COMPLETADO (2026-05-21)

## Bloqueado por

- Bloqueado por `issues/011-notificaciones-whatsapp.md`

## Historias de usuario abordadas

- Historia de usuario 14
- Historia de usuario 15
- Historia de usuario 30
