# Client Brief - Sistema de Gestion de Rifas Digital

## Cliente

Organizador de rifas tradicionales que vende mediante talonarios fisicos, contacto persona a persona y pagos principalmente en efectivo.

## Problema

El proceso actual limita el alcance comercial, requiere trabajo manual repetitivo, dificulta el seguimiento de pagos pendientes y aumenta el riesgo de errores: boletas sin pagar, datos incompletos, numeros duplicados o compradores sin comprobante.

## Objetivo del proyecto

Construir una aplicacion web que permita crear, publicar y administrar rifas digitales, manteniendo una experiencia simple para compradores sin cuenta y un panel claro para el organizador.

## Usuarios

- Admin / Vendedor: crea cuenta, inicia sesion y gestiona rifas, compradores, pagos y resultados.
- Comprador: accede por enlace publico, selecciona numero, registra datos y escoge metodo de pago.

## Alcance de primera entrega

- Estructura base del monorepo.
- Backend con FastAPI.
- Frontend con React.
- Registro/login de admin.
- Creacion y listado de rifas.
- Enlace publico de rifa.
- Vista publica con grilla de numeros.
- Reserva basica de numero por comprador sin login.
- Issues redactadas y flujo de trabajo con Claude Code documentado.

## Restricciones

- La boleta solo participa si queda pagada.
- Los compradores no deben crear cuenta.
- Los numeros reservados no pueden ser tomados por otro comprador.
- Las reservas pendientes vencen y liberan el numero.
- Wompi y WhatsApp se integran en fases posteriores.

## Criterios de exito

- El repositorio permite ejecutar backend y frontend localmente.
- El README explica arquitectura, instalacion y flujo de ramas.
- El desarrollo queda dividido en issues claras para trabajar con PRs.
- La primera vertical slice demuestra admin -> crear rifa -> comprador reserva numero.
