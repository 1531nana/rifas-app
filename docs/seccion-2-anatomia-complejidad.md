# Sección 2: Anatomía de la Complejidad

> **Responsable:** Persona 4 (con apoyo técnico de Persona 1)
> Análisis del código fuente usando los conceptos de Ousterhout.

---

## Marco teórico aplicado

<!-- Breve recordatorio de los conceptos usados en esta sección:
     módulos profundos, módulos superficiales, information hiding, information leakage.
     Referenciar marco-teorico.md -->

---

## Módulos profundos identificados

<!-- Identificar al menos 2-3 módulos donde la interfaz sea simple
     pero la implementación oculte complejidad importante.

     Para cada módulo responder:
     - ¿Cuál es el módulo? (archivo + función/clase)
     - ¿Qué problema resuelve?
     - ¿Por qué su interfaz es simple?
     - ¿Qué complejidad oculta internamente?
     - ¿Por qué puede considerarse un módulo profundo?

     Incluir fragmento de código real. -->

### Ejemplo de estructura por módulo

```
Módulo: backend/app/services/...
Interfaz pública: nombre_funcion(param1, param2) -> Tipo
Complejidad oculta: ...
```

---

## Módulos superficiales identificados

<!-- Identificar partes donde la IA creó archivos o funciones demasiado pequeños.

     Para cada módulo responder:
     - ¿Qué módulo o archivo era superficial?
     - ¿Por qué aumentaba la complejidad?
     - ¿Qué problema generaba en el mantenimiento?
     - ¿Qué directriz humana se dio para corregirlo?
     - ¿Se unificó, eliminó o mejoró?

     Incluir fragmento de código o captura. -->

---

## Directrices humanas para mejorar la profundidad de los módulos

<!-- Listar las instrucciones concretas que el equipo le dio al agente
     para corregir módulos superficiales. Ejemplos:
     - "crea esos servicios en un nuevo archivo, mantén el principio S"
     - instrucciones en CLAUDE.md que guiaron el diseño -->

---

## Fugas de información detectadas

<!-- ¿En algún punto los detalles de BD o HTTP se filtraron hacia capas superiores?
     Describir el caso concreto con código.

     Para cada fuga responder:
     - ¿Dónde ocurrió?
     - ¿Qué detalle interno se filtró?
     - ¿Por qué era un problema? -->

---

## Aplicación de Information Hiding

<!-- ¿Cómo corrigieron las fugas detectadas?
     ¿Qué capa quedó encargada de ocultar cada detalle?
     Mostrar comparación antes/después si aplica. -->

---

## Conclusión de la sección

<!-- Evaluación global: ¿el código generado por Claude tiende a módulos profundos
     o superficiales? ¿Qué rol tuvo la supervisión humana en corregir esto? -->

---

## Evidencias

<!-- Insertar capturas de:
     - Fragmentos de código de módulos profundos y superficiales
     - Estructura de carpetas final
     - Comparación antes/después de refactors
     Ver carpeta evidencias/ -->
