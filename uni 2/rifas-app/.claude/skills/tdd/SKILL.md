---
name: tdd
description: Desarrollo guiado por tests con el ciclo rojo-verde-refactor. Usar cuando el usuario quiera construir funcionalidades o corregir bugs usando TDD, mencione "rojo-verde-refactor", quiera tests de integracion, o pida desarrollo test-first.
---

# Desarrollo Guiado por Tests

## Filosofia

**Principio central**: Los tests deben verificar comportamiento a traves de interfaces publicas, no detalles de implementacion. El codigo puede cambiar completamente; los tests no deberian.

**Los buenos tests** son de estilo integracion: ejercitan rutas de codigo reales a traves de APIs publicas. Describen _que_ hace el sistema, no _como_ lo hace. Un buen test se lee como una especificacion - "el usuario puede hacer checkout con un carrito valido" te dice exactamente que capacidad existe. Estos tests sobreviven refactorizaciones porque no les importa la estructura interna.

**Los malos tests** estan acoplados a la implementacion. Mockean colaboradores internos, prueban metodos privados, o verifican a traves de medios externos (como consultar una base de datos directamente en lugar de usar la interfaz). La senal de alerta: tu test falla cuando refactorizas, pero el comportamiento no ha cambiado. Si renombras una funcion interna y los tests fallan, esos tests estaban probando la implementacion, no el comportamiento.

Ver [tests.md](tests.md) para ejemplos y [mocking.md](mocking.md) para guias de mocking.

## Anti-patron: Cortes Horizontales

**NO escribas todos los tests primero, luego toda la implementacion.** Esto es "corte horizontal" - tratar ROJO como "escribir todos los tests" y VERDE como "escribir todo el codigo".

Esto produce **tests malos**:

- Tests escritos en masa prueban comportamiento _imaginado_, no _real_
- Terminas probando la _forma_ de las cosas (estructuras de datos, firmas de funciones) en lugar del comportamiento orientado al usuario
- Los tests se vuelven insensibles a cambios reales - pasan cuando el comportamiento falla, fallan cuando el comportamiento esta bien
- Te adelantas a tus faros, comprometiendote con la estructura de tests antes de entender la implementacion

**Enfoque correcto**: Cortes verticales via trazadores. Un test → una implementacion → repetir. Cada test responde a lo que aprendiste del ciclo anterior. Como acabas de escribir el codigo, sabes exactamente que comportamiento importa y como verificarlo.

```
MAL (horizontal):
  ROJO:  test1, test2, test3, test4, test5
  VERDE: impl1, impl2, impl3, impl4, impl5

BIEN (vertical):
  ROJO→VERDE: test1→impl1
  ROJO→VERDE: test2→impl2
  ROJO→VERDE: test3→impl3
  ...
```

## Flujo de trabajo

### 1. Planificacion

Antes de escribir cualquier codigo:

- [ ] Confirmar con el usuario que cambios de interfaz son necesarios
- [ ] Confirmar con el usuario que comportamientos probar (priorizar)
- [ ] Identificar oportunidades para [modulos profundos](deep-modules.md) (interfaz pequena, implementacion profunda)
- [ ] Disenar interfaces para [testabilidad](interface-design.md)
- [ ] Listar los comportamientos a probar (no pasos de implementacion)
- [ ] Obtener aprobacion del usuario sobre el plan

Preguntar: "¿Como deberia verse la interfaz publica? ¿Cuales comportamientos son mas importantes de probar?"

**No puedes probar todo.** Confirmar con el usuario exactamente que comportamientos importan mas. Enfocar el esfuerzo de testing en rutas criticas y logica compleja, no en cada caso borde posible.

### 2. Trazador

Escribir UN test que confirme UNA cosa sobre el sistema:

```
ROJO:  Escribir test para el primer comportamiento → el test falla
VERDE: Escribir codigo minimo para pasar → el test pasa
```

Este es tu trazador - demuestra que el camino funciona de extremo a extremo.

### 3. Ciclo incremental

Para cada comportamiento restante:

```
ROJO:  Escribir el siguiente test → falla
VERDE: Codigo minimo para pasar → pasa
```

Reglas:

- Un test a la vez
- Solo el codigo suficiente para pasar el test actual
- No anticipar tests futuros
- Mantener los tests enfocados en comportamiento observable

### 4. Refactorizacion

Despues de que todos los tests pasen, buscar [candidatos para refactorizar](refactoring.md):

- [ ] Extraer duplicacion
- [ ] Profundizar modulos (mover complejidad detras de interfaces simples)
- [ ] Aplicar principios SOLID donde sea natural
- [ ] Considerar lo que el nuevo codigo revela sobre el codigo existente
- [ ] Ejecutar tests despues de cada paso de refactorizacion

**Nunca refactorizar en ROJO.** Llegar a VERDE primero.

## Lista de verificacion por ciclo

```
[ ] El test describe comportamiento, no implementacion
[ ] El test usa solo la interfaz publica
[ ] El test sobreviviria una refactorizacion interna
[ ] El codigo es minimo para este test
[ ] No se agregaron funcionalidades especulativas
```
