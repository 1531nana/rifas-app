# Punto de Control Arquitectonico

Fecha: 2026-05-22  
Alcance: auditoria mid-sprint y cierre de issues #001-#014  
Resultado: solucion hibrida implementada parcialmente en codigo, con deuda explicita para produccion.

---

## 1) Diagnostico inicial

El repo tenia una discrepancia fuerte entre documentacion e implementacion: los issues #004-#014 aparecian completados, pero buena parte de la logica vivia en `backend/app/services/issues_4_14.py` como funciones sueltas no integradas. Ese archivo usaba strings de estado y campos inexistentes (`winner_number`, `wompi_transaction_id`, `reminder_sent_at`), mientras que los routers reales no exponian webhook Wompi, checkout, ganador, stats, compradores, refresh token, upload de imagen ni edicion completa de rifas.

Riesgos detectados:
- Doble fuente de verdad entre `services/raffles.py` y `services/issues_4_14.py`.
- Transiciones de pago/reserva dispersas y sin ruta unica.
- Falta de indice de concurrencia para evitar doble reserva.
- Documentacion de pruebas/commits no verificable en este entorno por ausencia de Python/Git.
- Scaffold prometia Tailwind/Alembic/PostgreSQL, pero no estaban configurados.

---

## 2) Candidatos de profundizacion

1. `backend/app/services/raffles.py`: profundizar como servicio de aplicacion para rifas, reservas, pagos, notificaciones y ganador.
2. `backend/app/services/issues_4_14.py`: eliminar logica satelite o convertirla en compatibilidad para evitar caminos paralelos.
3. Infraestructura base: agregar Alembic, variables de integracion, Tailwind real y constraints de base de datos.

El componente elegido fue el primero, con soporte del segundo y tercero.

---

## 3) Propuestas paralelas de interfaz

### Sub-agente A - Servicio de aplicacion unico

Interfaz sugerida:

```python
class RaffleApplicationService:
    def create_raffle(admin_id, command): ...
    def get_public_raffle(public_token): ...
    def reserve_number(public_token, command): ...
    def confirm_cash_payment(admin_id, raffle_id, reservation_id): ...
    def create_payment_checkout(reservation_id): ...
    def handle_payment_webhook(provider, payload): ...
    def expire_reservations(): ...
    def send_payment_reminders(): ...
    def close_raffle_with_winner(admin_id, raffle_id, winner_number): ...
    def get_stats(admin_id, raffle_id): ...
```

Ventaja: endpoints, jobs y webhooks usan una sola puerta transaccional.  
Riesgo: puede crecer como modulo grande si no se extraen puertos despues.

### Sub-agente B - Dominio por casos de uso

Interfaz sugerida:

```text
use_cases/raffles/create_raffle.py
use_cases/reservations/reserve_number.py
use_cases/payments/process_wompi_webhook.py
use_cases/notifications/send_payment_reminders.py
```

Ventaja: cada intencion del negocio queda testeable y pequena.  
Riesgo: para este sprint agrega muchos archivos y puede frenar el cierre funcional.

### Sub-agente C - Puertos y adaptadores

Interfaz sugerida:

```python
class RaffleRepository: ...
class PaymentGateway: ...
class NotificationGateway: ...
class Scheduler: ...
```

Ventaja: Wompi, WhatsApp, DB y jobs quedan reemplazables.  
Riesgo: requiere una migracion gradual para no romper el codigo actual.

---

## 4) Solucion hibrida implementada

Se eligio una ruta pragmatica:
- Profundizar `app.services.raffles` como servicio de aplicacion real.
- Convertir `services/issues_4_14.py` en archivo de compatibilidad que reexporta funciones integradas.
- Mantener routers existentes y agregar rutas faltantes: `PATCH /raffles/{id}`, `POST /raffles/{id}/image`, `GET /raffles/{id}/stats`, `GET /raffles/{id}/buyers`, `POST /raffles/{id}/winner`, `POST /webhooks/wompi`, `/jobs/*`, y aliases `/public/*`.
- Agregar gateways condicionales para Wompi, WhatsApp y Cloudinary: sandbox/local en desarrollo y HTTP real cuando hay credenciales.
- Agregar Alembic y un indice unico parcial para reservas activas.

Justificacion:
La opcion A cierra el mayor riesgo inmediato: caminos paralelos y features documentadas pero no accesibles. Se tomaron ideas de C para dejar limites de integracion claros (Wompi/WhatsApp/scheduler), y se pospuso la granularidad de B hasta que exista una suite de tests verde en Python.

---

## 5) Cambios aplicados

Backend:
- `auth.py`: refresh token real.
- `models/domain.py`: ganador, transaccion Wompi y recordatorio.
- `models/schemas.py`: DTOs de update, checkout, webhook, stats, buyers y winner.
- `services/raffles.py`: edicion, imagen local/Cloudinary, checkout, webhook, notificaciones WhatsApp, recordatorios, ganador, stats, buyers, expiracion global y control de concurrencia.
- `api/raffles.py`, `api/public.py`, `api/webhooks.py`, `api/jobs.py`: rutas expuestas.
- `core/database.py`: migracion ligera SQLite e indice unico parcial.
- `alembic/`: migracion inicial para SQLite/PostgreSQL.

Frontend:
- Tailwind configurado y activo.
- Dashboard admin con refresh token, edicion, upload, filtros, efectivo y ganador.
- Vista publica con rifa cerrada, instrucciones de efectivo y redirect a checkout Wompi.
- Pagina simple de resultado de pago.

---

## 6) Validacion

Ejecutado y verificado:
- `npm.cmd run build` desde `frontend/`: verde.
- `npm.cmd audit --audit-level=moderate`: 0 vulnerabilidades.
- `rg "[ ]" issues`: sin checkboxes pendientes.

No ejecutado por limitacion del entorno:
- `pytest`: Python no esta instalado; `py` no existe y `python` apunta a Microsoft Store.
- `git log`: Git no esta instalado/en PATH y no se ve `.git` en la carpeta local.

---

## 7) Recomendacion siguiente

Antes de declarar entrega final en GitHub:
1. Instalar Python y Git.
2. Correr `pip install -r backend/requirements.txt`.
3. Correr `alembic upgrade head`.
4. Correr `pytest`.
5. Confirmar `git status`, `git log --oneline`, y publicar commits trazables por issue.
6. Si el proyecto va a produccion, configurar Wompi/WhatsApp/Cloudinary reales e introducir outbox para notificaciones post-commit.
