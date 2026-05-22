## PRD padre

`issues/prd.md`

## Que construir

Job periodico que libera reservas expiradas. Ejecuta regularmente y marca como `expired` todas las reservas con `status=pending` cuyo `expires_at` ya paso. Esto complementa la verificacion lazy del endpoint de numeros.

## Criterios de aceptacion

- [x] El job corre periodicamente (cada 15-30 minutos es suficiente) ✅
- [x] El job marca como `expired` todas las reservas con `status=pending` y `expires_at < now()` ✅
- [x] Los numeros con reservas expiradas aparecen como disponibles (verde) al recargar la grilla ✅
- [x] El job es idempotente: correrlo varias veces no produce efectos duplicados ✅
- [x] Los errores del job se registran en logs sin detener el servidor ✅

## Status

✅ COMPLETADO (2026-05-21)

## Bloqueado por

- Bloqueado por `issues/006-reserva-numeros.md`

## Historias de usuario abordadas

- Historia de usuario 31
