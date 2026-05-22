# Checklist Final

Fecha: 2026-05-22  
Auditor: Codex

## Cumplimiento funcional

- [x] #001 scaffold: FastAPI, React/Vite, Tailwind, Alembic, `.env.example`.
- [x] #002 autenticacion admin: register/login/refresh, JWT, bcrypt, rutas protegidas.
- [x] #003 CRUD rifas: crear/listar/detalle/editar, ownership, restricciones con reservas.
- [x] #004 vista publica: `/r/{token}` y alias `/public/raffles/{token}`.
- [x] #005 grilla numeros: estados `available`, `reserved`, `sold`.
- [x] #006 reserva numeros: validacion, expiracion por metodo y conflicto 409.
- [x] #007 Wompi: checkout sandbox, webhook, aprobacion y liberacion por rechazo/cancelacion.
- [x] #008 efectivo: instrucciones, confirmacion manual y ownership.
- [x] #009 expiracion: lazy + job periodico cada 15 minutos + endpoint manual.
- [x] #010 imagen premio: upload JPG/PNG/WebP hasta 5MB y URL publica.
- [x] #011 WhatsApp: servicio sandbox/Meta, confirmacion de pago sin bloquear flujo.
- [x] #012 recordatorios: job idempotente con `reminder_sent_at`.
- [x] #013 ganador: registro, cierre de rifa, notificacion y bloqueo de nuevas reservas.
- [x] #014 dashboard: stats, compradores, filtros y grilla publica en tiempo real.

## Entregables academicos

- [x] `handoffs.md` actualizado.
- [x] `architecture-checkpoint.md` actualizado con 3 propuestas paralelas.
- [x] `ENTREGABLES_COMPLETADOS.md` actualizado.
- [x] Issues #001-#014 sin checkboxes pendientes.
- [ ] Historial Git/Ralph verificado: pendiente porque Git no esta disponible en este entorno.

## Validacion tecnica

- [x] `npm.cmd run build` en `frontend/`.
- [x] `npm.cmd audit --audit-level=moderate` en `frontend/` con 0 vulnerabilidades.
- [ ] `pytest` en `backend/`: pendiente porque Python no esta instalado.
- [ ] `alembic upgrade head`: pendiente por falta de Python.
- [ ] `git log`: pendiente por falta de Git.

## Riesgos restantes

- Las integraciones Wompi y WhatsApp estan en modo sandbox salvo que se configuren credenciales reales.
- El scheduler en proceso sirve para desarrollo; en produccion conviene mover jobs a worker/cron externo con locks.
- Antes de entrega final en GitHub hay que instalar Python/Git, correr pruebas backend y crear commits trazables por issue.
