# Software Journey

Este directorio contiene el sitio estatico de documentacion para la entrega final.

- Pagina principal: [index.html](index.html)
- PRD resumido: [prd.md](prd.md)
- Brief del cliente: [client-brief.md](client-brief.md)
- Checkpoint arquitectonico: [../architecture-checkpoint.md](../architecture-checkpoint.md)

La pagina principal puede publicarse desde GitHub Pages usando la carpeta `docs`.

## Estado actual

- Sitio estatico del Software Journey agregado en `docs/index.html`.
- Estilos responsive agregados en `docs/software-journey.css`.
- Validacion ejecutada: `python -m pytest` en backend con 33 pruebas aprobadas.
- Validacion ejecutada: `npm.cmd run build` en frontend con build correcto.

## Pendiente para la proxima PR o cierre final

- Activar GitHub Pages desde la carpeta `docs`.
- Copiar la URL publica del sitio desplegado en la entrega.
- Hacer merge final de `develop` a `main` si la entrega exige rama estable `main`.
- Ejecutar una prueba E2E sobre el sitio desplegado cuando exista URL publica.
- Opcional: limpiar warnings deprecados de `datetime.utcnow` y `on_event` en FastAPI.
