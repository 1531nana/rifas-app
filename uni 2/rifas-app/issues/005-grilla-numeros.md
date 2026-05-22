## PRD padre

`issues/prd.md`

## Que construir

Grilla visual de numeros en la vista publica de la rifa. Cada numero muestra su estado mediante colores: verde (disponible), rojo (vendido/pagado), amarillo (reservado/pendiente). La grilla debe ser responsive y usable en movil.

## Criterios de aceptacion

- [x] `GET /public/raffles/{public_token}/numbers` retorna la lista de numeros con su estado calculado ✅
- [x] Los estados posibles son: `available`, `reserved`, `sold` ✅
- [x] Un numero `reserved` con `expires_at` pasado se retorna como `available` ✅
- [x] La grilla renderiza todos los numeros de la rifa con el color correspondiente ✅
- [x] Numeros verdes (disponibles) son clickeables; rojos y amarillos no ✅
- [x] La grilla es responsive: se adapta correctamente a pantallas de movil ✅
- [x] El estado de los numeros refleja la realidad en tiempo real al cargar la pagina ✅

## Status

✅ COMPLETADO (2026-05-21)

## Bloqueado por

- Bloqueado por `issues/004-vista-publica-rifa.md`

## Historias de usuario abordadas

- Historia de usuario 20
