## PRD padre

`issues/prd.md`

## Que construir

Metricas y estadisticas por rifa en el panel del admin. El dashboard muestra para cada rifa: total recaudado, porcentaje de numeros vendidos, cantidad de pagos pendientes y visualizacion en tiempo real del estado de numeros. El admin tambien puede ver el listado completo de compradores con todos sus datos.

## Criterios de aceptacion

- [ ] `GET /raffles/{id}/stats` retorna: total recaudado (suma de boletas pagadas), numeros vendidos, numeros reservados, numeros disponibles, pagos pendientes (reservas activas sin pagar)
- [ ] El dashboard del admin muestra las metricas resumidas para cada rifa en la lista
- [ ] La vista detalle de una rifa muestra las estadisticas completas
- [ ] `GET /raffles/{id}/buyers` retorna el listado de compradores con: nombre, celular, email, numero comprado, metodo de pago, estado de pago
- [ ] El admin puede ver la grilla de numeros de su rifa con estados en tiempo real desde su panel
- [ ] La lista de compradores es visible en el panel del admin dentro del detalle de cada rifa

## Bloqueado por

- Bloqueado por `issues/007-pago-wompi.md`
- Bloqueado por `issues/008-pago-efectivo.md`

## Historias de usuario abordadas

- Historia de usuario 7
- Historia de usuario 8
- Historia de usuario 9
