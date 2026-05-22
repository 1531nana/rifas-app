# Bitacora de Transferencias

Cada entrada es un resumen compacto para reiniciar una ventana de contexto sin arrastrar ruido.

---

## Entrada 1 - Cierre funcional issues 001-014

Fecha: 2026-05-22  
Autor: Codex + revision senior  
Issues: #001-#014 marcados como completados en `issues/`

Componentes construidos:
- Backend FastAPI/SQLModel con auth admin, access/refresh JWT, CRUD de rifas, vista publica, reservas, pagos efectivo/digital, webhook Wompi, imagen de premio local o Cloudinary, expiracion lazy + job periodico, recordatorios, ganador, stats y compradores.
- Frontend React/Vite con Tailwind activo, login/registro, dashboard admin, creacion/edicion de rifas, subida de imagen, filtros de compradores, confirmacion de efectivo, registro de ganador, vista publica, grilla de numeros y checkout Wompi.
- Infraestructura: Alembic configurado, `.env.example` ampliado, SQLite dev y PostgreSQL via `DATABASE_URL`, indice unico parcial para evitar doble reserva activa.

Decisiones consolidadas:
1. Mantener routers finos y concentrar el flujo de rifas/reservas/pagos en `app.services.raffles` como servicio de aplicacion pragmatico.
2. Usar integraciones en modo sandbox cuando no hay credenciales reales: Wompi acepta `pub_test_local`; WhatsApp registra logs sin bloquear el flujo.
3. Preservar compatibilidad de rutas: `/r/{token}` para frontend actual y `/public/raffles/{token}` como alias cercano al PRD.
4. Reforzar concurrencia con `ux_active_reservation_number` sobre `(raffle_id, number)` para estados `pending` y `paid`.

Pendientes exactos:
- Ejecutar `pytest` cuando haya Python instalado; en este entorno `python`/`py` no estan disponibles.
- Verificar `git log` y commits Ralph cuando Git este instalado/en PATH; esta carpeta local no expone `.git` ni `git`.
- Reemplazar sandbox Wompi por cliente/firmas reales antes de produccion y configurar `WOMPI_EVENTS_SECRET`; WhatsApp y Cloudinary ya tienen cliente HTTP condicional cuando existen credenciales.
- Publicar o confirmar el repo remoto para que el entregable de commits sea verificable.

Validacion local hecha:
- `npm.cmd run build` en `frontend/`: verde.
- `npm.cmd audit --audit-level=moderate` en `frontend/`: 0 vulnerabilidades.
- `rg "[ ]" issues`: sin criterios pendientes en los 14 archivos de issues.

Proximo contexto recomendado:
Revisar `architecture-checkpoint.md`, instalar Python/Git, correr `pip install -r backend/requirements.txt`, `alembic upgrade head`, `pytest`, y luego hacer commit/PR con mensaje por issue o squash final trazable.
