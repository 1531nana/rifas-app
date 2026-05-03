# Rifas App

Sistema web para digitalizar el ciclo completo de una rifa: desde su creacion y publicacion, pasando por la seleccion y pago de numeros, hasta el registro del ganador. Los compradores acceden mediante un enlace publico sin necesidad de crear cuenta y pueden pagar con tarjeta, PSE o efectivo. El organizador gestiona todo desde un panel de control.

---
## Objetivo academico

Este proyecto cumple los criterios del curso:

- Es util para el dia a dia de un desarrollador porque permite practicar APIs REST, autenticacion, modelado de datos, concurrencia de reservas, frontend conectado y flujo de trabajo con agentes.
- Tiene backend y frontend separados.
- Tiene complejidad decente: usuarios admin, enlaces publicos, reservas con vencimiento, estados de pago, integraciones futuras con Wompi y WhatsApp.
---

## Stack tecnologico

| Capa | Tecnologia |
|------|-----------|
| Backend | Python + FastAPI + SQLModel, SQLite local para desarrollo|
| Frontend | React + Vite + TailwindCSS |
| Base de datos | PostgreSQL |
| Pagos | Wompi (tarjeta de credito y PSE) |
| Notificaciones | Meta Cloud API (WhatsApp Business) |
| Imagenes | Cloudinary |
| Despliegue backend | Railway |
| Despliegue frontend | Vercel |

---

## Arquitectura

```text
backend/
  app/
    api/          Endpoints REST
    core/         Configuracion, seguridad y base de datos
    models/       Entidades SQLModel
    services/     Reglas de negocio
  tests/          Pruebas iniciales de API
frontend/
  src/
    pages/        Vistas admin y comprador
    lib/          Cliente HTTP
docs/
  client-brief.md Brief del cliente
  prd.md          PRD resumido
issues/           Issues en markdown para importar a GitHub
ralph/            Prompt y runner del agente AFK/HITL
.claude/skills/   Skills locales usados por el flujo Claude Code
```

El sistema es *multi-organizador*: cada admin gestiona sus propias rifas de forma aislada. Los compradores acceden a cada rifa mediante un public_token opaco unico, sin necesidad de registrarse.

### Modulos principales

- *Rifas* — CRUD de rifas, generacion de token publico, estados active / closed
- *Numeros* — Estados calculados dinamicamente: available, reserved, sold
- *Reservas* — Timeout de 48h para pagos digitales, 5 dias para efectivo; expiracion lazy + job periodico
- *Pagos* — Wompi via webhook para digital; confirmacion manual del admin para efectivo
- *Notificaciones* — Templates de WhatsApp aprobados por Meta: confirmacion de pago, recordatorio 15 dias antes del sorteo, notificacion al ganador
- *Archivos* — Subida de imagen del premio a Cloudinary (campo opcional, max 5MB, formatos JPG/PNG/WebP)


---

## Flujo del comprador

1. El admin comparte el enlace /r/{public_token} de la rifa
2. El comprador ve la informacion de la rifa y la grilla de numeros (verde=disponible, rojo=vendido, amarillo=reservado)
3. Selecciona un numero disponible — queda reservado inmediatamente para otros
4. Completa el formulario con nombre, celular y email opcional
5. Elige metodo de pago: tarjeta/PSE (Wompi) o efectivo
6. Recibe confirmacion por WhatsApp una vez completado el pago

---

## Flujo del admin

1. Se registra con email y contrasena
2. Crea una rifa con nombre, premio, fecha, valor de boleta y tipo de loteria
3. Comparte el enlace publico generado automaticamente
4. Monitorea ventas en tiempo real desde el dashboard
5. Confirma pagos en efectivo manualmente
6. Registra el numero ganador para cerrar la rifa

---
## Flujo de ramas

La regla del equipo es:

```text
main -> develop -> feature/XX
```

- `main`: solo entregas estables.
- `develop`: integracion de PRs aprobados.
- `feature/01-base-project`, `feature/02-auth-admin`, etc.: trabajo por issue.

Comandos sugeridos:

```bash
git checkout -b develop
git checkout -b feature/01-base-project
```
---
## Issues del proyecto

Las tareas de desarrollo estan documentadas en la carpeta issues/. El PRD completo esta en [issues/prd.md](issues/prd.md).

| # | Issue | Bloqueado por |
|---|-------|---------------|
| 001 | Scaffold del proyecto | — |
| 002 | Autenticacion del admin | 001 |
| 003 | CRUD de rifas | 002 |
| 004 | Vista publica de la rifa | 003 |
| 005 | Grilla de numeros | 004 |
| 006 | Reserva de numeros | 005 |
| 007 | Pago con Wompi | 006 |
| 008 | Pago en efectivo | 006 |
| 009 | Expiracion de reservas | 006 |
| 010 | Imagen del premio | 003 |
| 011 | Notificaciones WhatsApp | 008 |
| 012 | Recordatorio de pago | 011 |
| 013 | Registro del ganador | 011 |
| 014 | Dashboard de estadisticas | 007, 008 |

---

## Como aplicar el flujo del articulo de AI Hero

El articulo "Running Your AFK Agent" propone trabajar con un agente observado por una persona, usando issues claros y ciclos de feedback. En este repo lo aplicamos asi:

1. Las tareas viven en `issues/` como archivos markdown, no como instrucciones sueltas.
2. `ralph/prompt.md` define como el agente escoge una sola tarea por corrida.
3. `ralph/once.ps1` carga issues, ultimos commits y prompt para ejecutar Claude Code en modo observado.
4. El agente debe usar `.claude/skills/tdd/` para escribir una prueba pequena antes de implementar.
5. Antes de cerrar una tarea debe correr feedback loops: tests del backend, build del frontend y revision manual del diff.
6. Las tareas terminadas se mueven a `issues/done/` y se suben mediante PR desde `feature/XX` hacia `develop`.

En esta primera entrega el desarrollo inicial queda preparado para ese flujo: brief, PRD, issues, skills y codigo base.

## Ejecutar backend

```bash
cd backend
py -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

La API queda en `http://127.0.0.1:8000`.

En Windows usa `py` si `python` abre Microsoft Store.

## Ejecutar frontend

```bash
cd frontend
npm install
npm run dev
```

El frontend queda en `http://127.0.0.1:5173`.

## Variables de entorno

Copia `.env.example` a `.env` en `backend/`.

```env
DATABASE_URL=sqlite:///./rifas.db
JWT_SECRET=change-me
ACCESS_TOKEN_MINUTES=60
```

---

## Despliegue

| Servicio | Plataforma |
|----------|-----------|
| Backend + BD | Railway |
| Frontend | Vercel |

---

## Estado inicial implementado

- Registro e inicio de sesion de admin.
- JWT para rutas protegidas.
- Crear/listar rifas por admin.
- Enlace publico por token opaco.
- Ver detalle publico de rifa.
- Reservar numero disponible con datos de comprador.
- Liberacion lazy de reservas vencidas.
- Tests iniciales para auth y reserva publica.

---
## Roadmap inmediato

- Migrar SQLite local a PostgreSQL.
- Agregar bloqueo transaccional fuerte para concurrencia real.
- Integrar Wompi para pagos digitales.
- Integrar Meta Cloud API para WhatsApp.
- Completar dashboard admin con compradores y confirmacion de efectivo.
- Publicar issues en GitHub y trabajar por PR.
---
## Publicar issues en GitHub

Cuando el repo ya exista en GitHub y `gh auth status` este autenticado:

```powershell
.\scripts\create-github-issues.ps1
```

El script toma los markdown de `issues/` y crea issues con titulo, cuerpo y labels.

## Fuera de alcance

- Generador automatico de numeros ganadores (el sorteo siempre es fisico)
- Notificaciones por email
- Aplicacion movil nativa
- Soporte para multiples ganadores por rifa
- Reventa o transferencia de boletas
