# PRD - Sistema de Gestion de Rifas Digital

## Estado

Aprobado para primera entrega academica.

## Solucion

Aplicacion web multi-organizador para digitalizar rifas: el admin crea rifas y comparte un enlace publico; el comprador entra sin login, elige numero y registra sus datos. La plataforma controla estados de numero, pagos pendientes y futuras notificaciones.

## Funcionalidades primera entrega

- Registro e inicio de sesion de admin con JWT.
- CRUD inicial de rifas: crear y listar.
- Token publico opaco por rifa.
- Vista publica `/r/:public_token`.
- Grilla de numeros con estados `available`, `reserved`, `sold`.
- Reserva de numero con nombre, celular, email opcional y metodo de pago.

## Funcionalidades posteriores

- Confirmacion manual de efectivo.
- Wompi para tarjeta y PSE.
- Webhook de pagos.
- WhatsApp Business Cloud API.
- Job diario de recordatorios.
- Registro de ganador y cierre de rifa.
- Imagenes en Cloudinary.
- PostgreSQL en produccion.

## Entidades

- `Admin`: vendedor autenticado.
- `Raffle`: rifa creada por un admin.
- `Reservation`: numero reservado por comprador.
- `Buyer`: en la primera version se representa dentro de `Reservation`; puede separarse si crece el dominio.

## Reglas clave

- Un numero no puede tener dos reservas activas.
- Reserva en efectivo vence en 5 dias.
- Reserva digital vence en 48 horas.
- Reserva pagada no vence.
- Boleta pendiente no participa en el sorteo.
- El comprador no necesita login.

## Testing inicial

- Registro de admin.
- Creacion de rifa.
- Lectura publica de rifa.
- Reserva de numero disponible.
- Rechazo de reserva duplicada.
