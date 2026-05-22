---
name: write-a-prd
description: Generar un PRD a partir del brief del cliente y escribirlo como archivo markdown local en issues/. Usar cuando el usuario quiera convertir una solicitud del cliente en un PRD estructurado.
---

Esta skill se invoca cuando el usuario quiere crear un PRD. Puedes saltarte pasos si no los consideras necesarios.

1. Pedir al usuario una descripcion larga y detallada del problema que quiere resolver y cualquier idea potencial de soluciones.

2. Explorar el repositorio para verificar sus afirmaciones y entender el estado actual del codigo base.

3. Interrogar al usuario sin piedad sobre cada aspecto de este plan hasta llegar a un entendimiento compartido. Recorrer cada rama del arbol de diseno, resolviendo las dependencias entre decisiones una por una.

4. Esbozar los modulos principales que necesitaras construir o modificar para completar la implementacion. Buscar activamente oportunidades para extraer modulos profundos que puedan probarse de forma aislada.

Un modulo profundo (a diferencia de uno superficial) es aquel que encapsula mucha funcionalidad en una interfaz simple y testeable que raramente cambia.

Verificar con el usuario que estos modulos coinciden con sus expectativas. Preguntar al usuario para cuales modulos quiere que se escriban tests.

5. Una vez que tengas un entendimiento completo del problema y la solucion, usar la plantilla a continuacion para escribir el PRD. El PRD debe escribirse como archivo markdown local en `issues/prd.md`. Crear el directorio `issues/` si no existe. NO enviar un issue a GitHub ni llamar a ningun servicio externo.

<prd-template>

## Enunciado del problema

El problema que enfrenta el usuario, desde la perspectiva del usuario.

## Solucion

La solucion al problema, desde la perspectiva del usuario.

## Historias de usuario

Una lista LARGA y numerada de historias de usuario. Cada historia de usuario debe tener el formato:

1. Como <actor>, quiero <funcionalidad>, para <beneficio>

<user-story-example>
1. Como cliente de banca movil, quiero ver el saldo de mis cuentas, para poder tomar decisiones mas informadas sobre mis gastos
</user-story-example>

Esta lista de historias de usuario debe ser extremadamente extensa y cubrir todos los aspectos de la funcionalidad.

## Decisiones de implementacion

Una lista de decisiones de implementacion que se tomaron. Puede incluir:

- Los modulos que se construiran/modificaran
- Las interfaces de esos modulos que se modificaran
- Aclaraciones tecnicas del desarrollador
- Decisiones arquitectonicas
- Cambios de esquema
- Contratos de API
- Interacciones especificas

NO incluir rutas de archivos especificas ni fragmentos de codigo. Pueden quedar desactualizados muy rapidamente.

## Decisiones de testing

Una lista de decisiones de testing que se tomaron. Incluir:

- Una descripcion de que hace un buen test (solo probar comportamiento externo, no detalles de implementacion)
- Que modulos se probaran
- Arte previo para los tests (es decir, tipos similares de tests en el codigo base)

## Fuera de alcance

Una descripcion de las cosas que estan fuera del alcance de este PRD.

## Notas adicionales

Cualquier nota adicional sobre la funcionalidad.

</prd-template>
