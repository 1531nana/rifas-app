# Reporte de Control Arquitectonico

## Diagnostico Inicial

La rama `develop` ya tenia el flujo base de rifas, reservas, pago efectivo y Wompi. El riesgo para #10 y #11 era agregar integraciones externas directamente en routers o componentes de UI, dejando reglas de negocio repartidas y dificilmente testeables.

Candidatos detectados:
- `backend/app/services/raffles.py`: concentra rifa, reserva y confirmacion de pago.
- `backend/app/api/raffles.py`: expone endpoints admin; riesgo de crecer con logica de archivos.
- Nuevo limite de integracion: Cloudinary y Meta Cloud API necesitaban sandbox y manejo de errores.

## Tres Propuestas de Interfaz

### Sub-agente A - Servicio de aplicacion extendido

```python
upload_prize_image(session, raffle, file) -> Raffle
confirm_cash_payment(session, raffle, reservation_id) -> Reservation
```

Ventaja: los routers siguen delgados y el flujo principal se mantiene en una sola capa.
Riesgo: `raffles.py` puede crecer si todos los proveedores externos quedan ahi.

### Sub-agente B - Puertos por integracion

```python
CloudinaryImageStore.upload(file) -> str
WhatsAppNotifier.send(template, phone, params) -> bool
```

Ventaja: proveedores reemplazables y pruebas unitarias mas limpias.
Riesgo: agrega mas clases de las necesarias para dos issues pequenos.

### Sub-agente C - Endpoints directos con helpers locales

```python
POST /raffles/{id}/image
PATCH /reservations/{id}/confirm-cash
```

Ventaja: implementacion rapida.
Riesgo: reglas de validacion, storage y notificacion quedan mezcladas con FastAPI.

## Solucion Hibrida Implementada

Se eligio A con una parte de B:
- `upload_prize_image` vive en `services/raffles.py` porque actualiza la rifa y valida el archivo.
- `send_whatsapp` vive en `services/notifications.py` como puerto estable para Meta Cloud API.
- Los routers solo autentican, resuelven la rifa/reserva y llaman al servicio.
- Los fallos de WhatsApp se registran y retornan `False`, sin revertir el pago confirmado.

## Justificacion Tecnica

La solucion preserva el flujo transaccional existente y evita duplicar confirmaciones de pago. Cloudinary y WhatsApp quedan configurables por variables de entorno, con modo sandbox para desarrollo y pruebas. La compatibilidad con `/public/raffles/{public_token}` y `PATCH /reservations/{id}/confirm-cash` cubre los criterios literales de los issues sin romper las rutas que ya usa el frontend.

## Validacion Ejecutada

- `pytest` backend completo: 33 passed.
- `npm run build` frontend: verde.
- `git diff` revisado: alcance limitado a #10, #11, `handoffs.md` y `architecture-checkpoint.md`.
