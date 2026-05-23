# Entregables Completados

Fecha de auditoria: 2026-05-23  
Estado: codigo e issues cerrados localmente; frontend/backend validados; verificacion Git pendiente por entorno.

## Entregable 1 - Historial de commits automatizados

Estado: pendiente de verificacion local.

Este entorno no tiene `git` disponible en PATH y la carpeta no expone `.git`, por lo que no pude comprobar `git log`, autoria Ralph ni publicar commits. El repositorio indicado para entrega es:

https://github.com/1531nana/rifas-app

Comandos que deben ejecutarse cuando Git este disponible:

```bash
git status --short --branch
git log --oneline --decorate --graph -20
git remote -v
```

## Entregable 2 - Bitacora de transferencia

Estado: completado.

Archivo actualizado: `handoffs.md`

Incluye:
- Componentes construidos para issues #001-#014.
- Decisiones de arquitectura consolidadas.
- Pendientes exactos para la siguiente ventana.
- Validaciones ejecutadas y limitaciones del entorno.

## Entregable 3 - Reporte de control arquitectonico

Estado: completado.

Archivo actualizado: `architecture-checkpoint.md`

Incluye:
- Diagnostico inicial.
- Tres propuestas paralelas de interfaz.
- Justificacion de la solucion hibrida.
- Cambios implementados.
- Validacion y pendientes.

## Estado de issues

Los 14 archivos en `issues/` no tienen checkboxes pendientes:

```bash
rg "[ ]" issues
```

Resultado en esta auditoria: sin coincidencias.

## Validacion ejecutada

Frontend:

```bash
cd frontend
npm.cmd run build
npm.cmd audit --audit-level=moderate
```

Resultado: build verde y 0 vulnerabilidades moderadas o superiores.

Backend:

```bash
cd backend
..\.venv\Scripts\python.exe -m pytest
..\.venv\Scripts\python.exe -m alembic upgrade head
```

Resultado: `pytest` verde con 2 passed y 32 warnings de deprecacion; `alembic upgrade head` aplicado correctamente sobre SQLite. Se agregaron pruebas para auth refresh, edicion, checkout, webhook Wompi, stats, buyers, ganador y bloqueo de reservas en rifa cerrada.
