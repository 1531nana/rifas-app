## PRD padre

`issues/prd.md`

## Que construir

Gestion completa de rifas para el admin: crear una rifa con todos sus campos, listarlas, ver el detalle y editarlas con las restricciones definidas. Al crear una rifa se genera automaticamente un `public_token` opaco unico. El admin puede editar descripcion, tipo de loteria y fecha, pero no el precio ni la cantidad de numeros si ya existe alguna reserva activa.

## Criterios de aceptacion

- [ ] `POST /raffles` crea una rifa con: nombre, tipo de loteria, cantidad de numeros, valor de boleta, descripcion del premio, fecha del sorteo
- [ ] La rifa creada incluye un `public_token` unico generado automaticamente
- [ ] `GET /raffles` retorna la lista de rifas del admin autenticado (activas y cerradas)
- [ ] `GET /raffles/{id}` retorna el detalle de una rifa
- [ ] `PATCH /raffles/{id}` permite editar descripcion, tipo de loteria y fecha del sorteo
- [ ] `PATCH /raffles/{id}` rechaza cambios de precio o cantidad de numeros si hay reservas activas
- [ ] Un admin no puede ver ni editar rifas de otro admin
- [ ] El frontend muestra la lista de rifas del admin en el dashboard
- [ ] El frontend tiene formulario de creacion de rifa con todos los campos
- [ ] El frontend tiene formulario de edicion con los campos permitidos

## Bloqueado por

- Bloqueado por `issues/002-autenticacion-admin.md`

## Historias de usuario abordadas

- Historia de usuario 4
- Historia de usuario 5
- Historia de usuario 6
- Historia de usuario 10
- Historia de usuario 11
