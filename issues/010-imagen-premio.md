## PRD padre

`issues/prd.md`

## Que construir

Subida opcional de imagen del premio al crear o editar una rifa. La imagen se almacena en Cloudinary y su URL publica se guarda en la BD. La imagen se muestra en la vista publica de la rifa para los compradores.

## Criterios de aceptacion

- [ ] `POST /raffles/{id}/image` sube una imagen a Cloudinary y guarda la URL en la rifa
- [ ] El campo de imagen es opcional: una rifa puede existir sin imagen
- [ ] La imagen subida tiene un tamano maximo de 5MB
- [ ] Solo se aceptan formatos JPG, PNG y WebP
- [ ] La URL de la imagen se incluye en la respuesta de `GET /public/raffles/{public_token}`
- [ ] El formulario de creacion/edicion de rifa incluye un campo de subida de imagen
- [ ] La imagen del premio se muestra en la vista publica de la rifa si existe
- [ ] Si no hay imagen, la vista publica muestra un placeholder o simplemente no muestra imagen

## Bloqueado por

- Bloqueado por `issues/003-crud-rifas.md`

## Historias de usuario abordadas

- Historia de usuario 16
