## PRD padre

`issues/prd.md`

## Que construir

Pagina publica accesible mediante el `public_token` de la rifa, sin necesidad de autenticacion. Muestra toda la informacion de la rifa: nombre, premio, descripcion, fecha del sorteo, valor de boleta y tipo de loteria. Esta es la pagina de entrada para el comprador.

## Criterios de aceptacion

- [ ] `GET /public/raffles/{public_token}` retorna la informacion publica de la rifa sin requerir autenticacion
- [ ] Retorna 404 si el token no existe
- [ ] El frontend renderiza la pagina en la ruta `/r/{public_token}`
- [ ] La pagina muestra: nombre de la rifa, descripcion del premio, fecha del sorteo, valor de boleta y tipo de loteria
- [ ] La pagina es responsive y funciona correctamente en movil
- [ ] Si la rifa esta cerrada, se muestra un mensaje indicandolo

## Bloqueado por

- Bloqueado por `issues/003-crud-rifas.md`

## Historias de usuario abordadas

- Historia de usuario 18
- Historia de usuario 19
