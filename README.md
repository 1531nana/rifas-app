# Rifas App

Sistema web para digitalizar la gestion de rifas tradicionales. La primera entrega incluye autenticacion de admin, creacion/listado de rifas y flujo publico inicial para que un comprador reserve un numero sin crear cuenta.

## Objetivo academico

Este proyecto cumple los criterios del curso:

- Es util para el dia a dia de un desarrollador porque permite practicar APIs REST, autenticacion, modelado de datos, concurrencia de reservas, frontend conectado y flujo de trabajo con agentes.
- Tiene backend y frontend separados.
- Tiene complejidad decente: usuarios admin, enlaces publicos, reservas con vencimiento, estados de pago, integraciones futuras con Wompi y WhatsApp.

## Stack

- Backend: Python, FastAPI, SQLModel, SQLite local para desarrollo.
- Frontend: React, Vite, CSS modular simple.
- Base de datos objetivo: PostgreSQL.
- Deploy objetivo: Railway para API/BD y Vercel para frontend.

## Estructura

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

## Estado inicial implementado

- Registro e inicio de sesion de admin.
- JWT para rutas protegidas.
- Crear/listar rifas por admin.
- Enlace publico por token opaco.
- Ver detalle publico de rifa.
- Reservar numero disponible con datos de comprador.
- Liberacion lazy de reservas vencidas.
- Tests iniciales para auth y reserva publica.

## Roadmap inmediato

- Migrar SQLite local a PostgreSQL.
- Agregar bloqueo transaccional fuerte para concurrencia real.
- Integrar Wompi para pagos digitales.
- Integrar Meta Cloud API para WhatsApp.
- Completar dashboard admin con compradores y confirmacion de efectivo.
- Publicar issues en GitHub y trabajar por PR.

## Publicar issues en GitHub

Cuando el repo ya exista en GitHub y `gh auth status` este autenticado:

```powershell
.\scripts\create-github-issues.ps1
```

El script toma los markdown de `issues/` y crea issues con titulo, cuerpo y labels.
