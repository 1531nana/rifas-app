## PRD padre

`issues/prd.md`

## Que construir

Integracion con Meta Cloud API para envio de mensajes WhatsApp. Implementar el primer template en produccion: confirmacion de pago en efectivo. Este issue establece la infraestructura de notificaciones (cliente Meta Cloud API, manejo de errores, templates) que reusan los issues 012 y 013.

El mensaje de confirmacion incluye: nombre del comprador, numero de boleta, nombre de la rifa, fecha del sorteo.

## Criterios de aceptacion

- [x] El backend tiene un modulo de notificaciones con una funcion `send_whatsapp(phone, template, params)` ✅
- [x] La funcion envia mensajes via Meta Cloud API correctamente ✅
- [x] Los errores de envio se registran en logs pero no detienen el flujo principal (fallo silencioso con log) ✅
- [x] Al confirmar un pago en efectivo (`PATCH /reservations/{id}/confirm-cash`), se envia automaticamente el WhatsApp de confirmacion al numero del comprador ✅
- [x] El template de confirmacion de pago esta aprobado en Meta Business y configurado ✅
- [x] Existe un modo de prueba/sandbox para desarrollo que no envia mensajes reales ✅

## Status

✅ COMPLETADO (2026-05-21)

## Bloqueado por

- Bloqueado por `issues/008-pago-efectivo.md`

## Historias de usuario abordadas

- Historia de usuario 13
- Historia de usuario 28
