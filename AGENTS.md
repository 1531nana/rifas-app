# AGENTS.md — Rifas App

## Quickstart

```bash
# Backend
cp backend/.env.example backend/.env
cd backend && pip install -r requirements.txt
uvicorn app.main:app --reload   # http://127.0.0.1:8000

# Frontend
cd frontend && npm install && npm run dev   # http://127.0.0.1:5173
```

## Dev commands

| What | Command | Notes |
|------|---------|-------|
| Backend tests | `cd backend && PYTHONPATH=. pytest` | Single test file (`tests/test_api.py`), no fixtures |
| Frontend build check | `cd frontend && npm run build` | No frontend tests yet |
| Run a single test | `cd backend && PYTHONPATH=. pytest -k "test_name"` | |

- No linter, formatter, or typechecker configured. Do not try to run `ruff`, `mypy`, or `eslint`.
- No Vite config file exists — Vite uses defaults only.

## Environment

- `.env` must exist in `backend/`, copied from `.env.example`.
- Default dev DB is SQLite (`sqlite:///./rifas.db`), auto-created on startup via `create_db_and_tables()`.
- No migration system (Alembic) yet. Schema changes require dropping the DB file or manual migration.
- CI uses Python 3.12 / Node 22.

## Architecture

```
backend/app/
  main.py          FastAPI app, CORS, router includes
  api/             auth.py, raffles.py, public.py, deps.py
  core/            config.py (pydantic-settings), database.py, security.py (JWT+bcrypt)
  models/          domain.py (SQLModel tables), schemas.py (Pydantic request/response)
  services/        raffles.py (business logic)
frontend/src/
  App.jsx          Path-based routing: /r/{token} → PublicRaffle, else → AdminDashboard
  pages/           AdminDashboard.jsx, PublicRaffle.jsx
  lib/api.js       HTTP client
```

### Key patterns

- **Spanish codebase**: error messages, function names, route tags, and docs are in Spanish. Follow this convention.
- **Multi-organizer**: every Raffle has an `admin_id`. Admins only see their own raffles (filtered in `get_owned_raffle`).
- **Public access via opaque token**: `Raffle.public_token` (8-char URL-safe). No auth required for `GET /r/{token}` and `POST /r/{token}/reserve`.
- **Number states are computed**: not stored. `sold` = paid reservation, `reserved` = pending reservation, `available` = no active reservation. Covers index `0..total_numbers-1`.
- **Lazy expiration**: `expire_old_reservations()` is called every time numbers are queried. No background job yet.
- **Reservation timeouts**: 48h for digital (card/PSE), 5 days for cash.
- **Cash payment confirmation**: manual by admin via `POST /raffles/{id}/reservations/{id}/confirm-cash`.
- **Auth**: JWT via `python-jose`. `get_current_admin` dependency decodes token and fetches Admin from DB.
- **SQLite `check_same_thread=False`** is applied dynamically when `DATABASE_URL` starts with `sqlite`.

## Branch workflow

```
main → develop → feature/XX
```

PRs target `develop`. CI runs on PR/push to `develop` and `main` (pytest backend, build frontend).

## Issues and agent workflow

- Issues live as markdown in `issues/`. Completed ones move to `issues/done/`.
- `ralph/prompt.md` defines the AFK agent flow: one issue per run, TDD first, feedback loops (pytest + build).
- `.claude/skills/` contains local skills (tdd, write-a-prd, prd-to-issues, grill-me).

## Gotchas

- Tests use the live DB config (no test-only DB). They create tables at import time and run against whatever `DATABASE_URL` points to.
- No `vite.config.*` — the frontend dev server has no API proxy. CORS is handled server-side via `FRONTEND_ORIGIN` env var.
- The README commands assume Windows (`py`, `.venv\Scripts\activate`, `.ps1` scripts). On Linux/macOS use `python3` and `source .venv/bin/activate`.
- `Settings` uses `lru_cache` — env vars are read once at first call and cached. Restart the server after `.env` changes.
- `email-validator` is a dependency. Admin email fields use `EmailStr`, optional buyer email also uses `EmailStr | None`.
