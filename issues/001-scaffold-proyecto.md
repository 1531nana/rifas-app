## PRD padre

`issues/prd.md`

## Que construir

Configurar la estructura base del proyecto con backend FastAPI y frontend React+Vite+TailwindCSS conectados a PostgreSQL. El resultado debe ser un endpoint `/health` funcional en el backend y una pantalla en blanco con Tailwind cargado en el frontend, ambos desplegables en Railway y Vercel respectivamente.

Incluye:
- Estructura de carpetas del backend (FastAPI, Alembic para migraciones, estructura modular)
- Estructura de carpetas del frontend (React + Vite + TailwindCSS)
- Conexion a PostgreSQL con Alembic configurado
- Variables de entorno documentadas (.env.example)
- README con instrucciones de setup local

## Criterios de aceptacion

- [ ] `GET /health` retorna `{"status": "ok"}` desde el backend
- [ ] El frontend carga en el navegador sin errores de consola
- [ ] TailwindCSS esta activo (un elemento con clase Tailwind se renderiza correctamente)
- [ ] Alembic puede correr migraciones contra una BD PostgreSQL local
- [ ] Existe `.env.example` con todas las variables necesarias documentadas

## Bloqueado por

Ninguno - puede comenzar inmediatamente

## Historias de usuario abordadas

Base tecnica para todas las historias de usuario del PRD.
