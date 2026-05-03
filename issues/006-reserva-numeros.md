## PRD padre

`issues/prd.md`

## Que construir

Flujo de seleccion y reserva de un numero por parte del comprador. Al hacer click en un numero disponible, se abre un modal con el formulario de datos del comprador (nombre, celular, email opcional) y seleccion del metodo de pago. Al confirmar, el numero queda reservado inmediatamente y se muestra el plazo para completar el pago (48h para digital, 5 dias para efectivo).

## Criterios de aceptacion

- [ ] `POST /public/reservations` crea una reserva con numero, datos del comprador y metodo de pago seleccionado
- [ ] Si el numero ya tiene una reserva activa no expirada, retorna 409
- [ ] La reserva se crea con `expires_at = now() + 48h` para pagos digitales
- [ ] La reserva se crea con `expires_at = now() + 5 dias` para pago en efectivo
- [ ] El numero aparece inmediatamente como amarillo (reservado) tras la reserva exitosa
- [ ] El modal muestra el formulario con: nombre completo (requerido), celular (requerido), email (opcional), metodo de pago
- [ ] El comprador ve claramente el plazo que tiene para completar el pago
- [ ] El celular se valida con formato correcto (necesario para WhatsApp)
- [ ] Si el numero es tomado por otro comprador entre click y confirmacion, se muestra error claro

## Bloqueado por

- Bloqueado por `issues/005-grilla-numeros.md`

## Historias de usuario abordadas

- Historia de usuario 21
- Historia de usuario 22
- Historia de usuario 23
- Historia de usuario 31
