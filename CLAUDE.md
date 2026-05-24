# CLAUDE.md — Rifas App

Instrucciones para Claude Code en este proyecto. Estas reglas tienen precedencia sobre los defaults del sistema.

## Calidad de código — no negociable

- Escribe código limpio desde el primer intento. No dejes TODOs, hacks o lógica duplicada.
- Cada función hace una sola cosa. Si necesitas un comentario para explicar qué hace una función, renómbrala.
- Nombra variables y funciones con intención: `expire_old_reservations` en vez de `process`.
- No agregues abstracciones prematuras. Tres líneas similares son mejores que una abstracción innecesaria.

## Separación de responsabilidades

### Backend (FastAPI)

| Capa | Carpeta | Responsabilidad |
|------|---------|-----------------|
| Dominio | `models/domain.py` | Entidades SQLModel, enums, reglas de negocio puras |
| Validación | `models/validators.py` | Constantes de validación, funciones puras sin dependencias externas |
| Schemas | `models/schemas.py` | Contratos de entrada/salida (Pydantic). Usa validadores del dominio |
| Servicios | `services/` | Casos de uso: orquestan dominio + persistencia. Aquí va la lógica de negocio |
| API | `api/` | Solo HTTP: recibe request, llama servicio, retorna response. Sin lógica de negocio |
| Core | `core/` | Infraestructura: DB, config, seguridad, scheduler |

**Reglas:**
- La capa `api/` no contiene lógica de negocio. Si un endpoint hace más que llamar un servicio, mueve esa lógica al servicio.
- Los validadores de dominio (`validators.py`) no importan nada de FastAPI ni SQLModel.
- Los servicios no conocen FastAPI (no usan `HTTPException` excepto para errores de dominio comunicados hacia arriba).

### Frontend (React)

| Tipo | Carpeta | Responsabilidad |
|------|---------|-----------------|
| Páginas | `pages/` | Un archivo por página. Orquestan estado y renderizan layout |
| Componentes | `pages/` o `components/` | Un archivo por componente. Sin lógica de negocio interna |
| Cliente HTTP | `lib/api.js` | Todas las llamadas fetch centralizadas aquí |
| Constantes | `lib/constants.js` | Valores compartidos entre componentes (plazos, opciones, etc.) |

**Reglas:**
- Un componente por archivo. No definir componentes auxiliares dentro del mismo archivo de una página.
- Las constantes compartidas van en `lib/constants.js`, no inline dentro de componentes.
- El estado de UI (modal abierto, mensaje de error) vive en el componente padre que lo necesita.
- No duplicar lógica de formato/cálculo: extraerla a `lib/` si se usa en más de un lugar.

## TDD obligatorio para cada issue

Sigue el ciclo rojo → verde → refactor:

1. Escribe el test que describe el comportamiento esperado.
2. Confirma que falla (rojo).
3. Implementa el mínimo código para que pase (verde).
4. Refactoriza sin romper tests.

Cada issue tiene su propio archivo de tests: `tests/test_NNN_nombre-issue.py`. No acumules todo en `test_api.py`.

## Estructura de archivos

- Un archivo por responsabilidad. Si un archivo crece más de ~150 líneas, evalúa si mezcla responsabilidades.
- No crear archivos de utilidades genéricos (`utils.py`, `helpers.js`). Nombralos por su dominio (`validators.py`, `formatters.js`).
- Las constantes de dominio van separadas de la lógica que las usa.

## Convenciones del proyecto

- **Idioma**: código y mensajes de error en español (ver `AGENTS.md`).
- **Tests**: un archivo por issue en `tests/`. Correr con `cd backend && PYTHONPATH=. pytest`.
- **Build frontend**: verificar siempre con `cd frontend && npm run build` antes de cerrar una issue.
- **Issues completadas**: mover de `issues/` a `issues/done/`.
