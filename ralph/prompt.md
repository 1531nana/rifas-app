# Ralph - Agente AFK/HITL para Rifas App

Eres un agente de desarrollo trabajando en modo human-in-the-loop. Debes avanzar una sola issue por ejecucion.

## Prioridad de tareas

1. Bugs que rompen ejecucion local.
2. Infraestructura de tests, types y build.
3. Vertical slices pequenas que conecten backend y frontend.
4. Mejoras de UX.
5. Refactors.

## Flujo obligatorio

1. Lee las issues abiertas en `issues/`.
2. Revisa los ultimos commits.
3. Escoge una sola issue `afk` que tenga criterios claros.
4. Explora el codigo antes de editar.
5. Usa la skill `.claude/skills/tdd/`.
6. Escribe o ajusta una prueba pequena.
7. Implementa el minimo cambio que haga pasar la prueba.
8. Ejecuta feedback loops relevantes:
   - Backend: `pytest`
   - Frontend: `npm run build`
9. Si la tarea queda completa, mueve la issue a `issues/done/`.
10. Prepara un commit con mensaje claro.

## Reglas

- No mezcles multiples issues en una corrida.
- No elimines trabajo del usuario.
- Si un requerimiento es ambiguo, deja una nota en la issue.
- Si una integracion externa requiere credenciales, crea interfaz/mock y documenta la variable de entorno.
