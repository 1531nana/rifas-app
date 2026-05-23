## PRD padre

`issues/prd.md`

## Que construir

Pagina publica accesible mediante el `public_token` de la rifa, sin necesidad de autenticacion. Muestra toda la informacion de la rifa: nombre, premio, descripcion, fecha del sorteo, valor de boleta y tipo de loteria. Esta es la pagina de entrada para el comprador.

## Criterios de aceptacion

- [x] `GET /public/raffles/{public_token}` retorna la informacion publica de la rifa sin requerir autenticacion ✅
- [x] Retorna 404 si el token no existe ✅
- [x] El frontend renderiza la pagina en la ruta `/r/{public_token}` ✅
- [x] La pagina muestra: nombre de la rifa, descripcion del premio, fecha del sorteo, valor de boleta y tipo de loteria ✅
- [x] La pagina es responsive y funciona correctamente en movil ✅
- [x] Si la rifa esta cerrada, se muestra un mensaje indicandolo ✅

## Status

✅ COMPLETADO (2026-05-21)

## Bloqueado por

- Bloqueado por `issues/003-crud-rifas.md`

## Historias de usuario abordadas

- Historia de usuario 18
- Historia de usuario 19
