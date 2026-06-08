# Despliegue y URLs

Este proyecto queda preparado para tres superficies de entrega: sitio de documentacion, frontend y API.

## Sitio `/docs`

- Plataforma: GitHub Pages.
- Carpeta publicada: `docs/`.
- Workflow: `.github/workflows/pages.yml`.
- URL esperada del sitio: `https://1531nana.github.io/rifas-app/`.

Para activarlo en GitHub:

1. Entra a `Settings > Pages`.
2. En `Build and deployment`, selecciona `GitHub Actions`.
3. Ejecuta el workflow `Deploy docs to GitHub Pages` o sube cambios a `main`/`develop`.

## Frontend

- Plataforma sugerida: Vercel.
- Carpeta de proyecto en Vercel: `frontend`.
- Build command: `npm run build`.
- Output directory: `dist`.
- Variable obligatoria: `VITE_API_URL=<URL publica del backend>`.
- Archivo de rutas SPA: `frontend/vercel.json`.

Cuando Vercel cree el dominio, copia la URL final en la entrega. Ejemplo esperado:
`https://rifas-app.vercel.app`.

## Backend

- Plataforma sugerida: Railway.
- Carpeta de proyecto en Railway: `backend`.
- Start command: definido en `backend/railway.json`.
- Health check manual: `GET /health`.
- Variables minimas:
  - `DATABASE_URL`
  - `JWT_SECRET`
  - `FRONTEND_ORIGIN`
  - `APP_BASE_URL`
  - `WOMPI_PUBLIC_KEY`
  - `WOMPI_INTEGRITY_KEY`
  - `WOMPI_EVENTS_KEY`

Despues de generar el dominio publico en Railway, actualiza `APP_BASE_URL` con esa URL y usa la misma URL como `VITE_API_URL` en Vercel.

## Evidencia local

- Backend: `python -m pytest` con 33 pruebas aprobadas.
- Frontend: `npm.cmd run build` correcto.
- UI: el frontend compila como SPA y conserva rutas profundas con rewrite a `index.html`.
