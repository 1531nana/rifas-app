## PRD padre

`issues/prd.md`

## Que construir

Integracion con Wompi para pagos con tarjeta de credito y PSE. Tras seleccionar uno de estos metodos y completar el formulario de datos, el comprador es dirigido al checkout de Wompi. Wompi notifica el resultado via webhook y el backend actualiza el estado de la reserva a `paid` (aprobado) o libera el numero (rechazado).

## Criterios de aceptacion

- [ ] `POST /public/reservations/{id}/checkout` genera un enlace de pago Wompi para la reserva
- [ ] El frontend redirige al comprador al checkout de Wompi tras crear la reserva con metodo digital
- [ ] `POST /webhooks/wompi` procesa la notificacion de Wompi correctamente
- [ ] Un webhook con estado `APPROVED` marca la reserva como `paid` y el numero como vendido (rojo)
- [ ] Un webhook con estado `DECLINED` o `VOIDED` libera la reserva (numero vuelve a verde)
- [ ] El webhook valida la firma de Wompi antes de procesar
- [ ] El comprador ve una pagina de confirmacion tras pago exitoso
- [ ] El comprador ve una pagina de error/reintento tras pago fallido

## Bloqueado por

- Bloqueado por `issues/006-reserva-numeros.md`

## Historias de usuario abordadas

- Historia de usuario 24
- Historia de usuario 25
