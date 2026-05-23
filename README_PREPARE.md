# Preparacion Local

## Backend

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
alembic upgrade head
uvicorn app.main:app --reload
```

API: `http://127.0.0.1:8000`

## Frontend

```powershell
cd frontend
npm install
npm run dev
```

App: `http://127.0.0.1:5173`

## Validacion

```powershell
cd backend
pytest

cd ..\frontend
npm run build
npm audit --audit-level=moderate
```

## Nota de entorno

En la auditoria Codex de 2026-05-22 no se pudo ejecutar `pytest`, `alembic` ni `git log` porque Python y Git no estaban disponibles en PATH. El build y audit del frontend si fueron ejecutados correctamente.
