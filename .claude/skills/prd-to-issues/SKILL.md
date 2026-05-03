---
name: prd-to-issues
description: Dividir un PRD en issues trabajables de forma independiente y escribir cada uno como un archivo markdown local en issues/. Usar cuando el usuario quiera convertir un PRD en una lista de tareas concretas.
---

# PRD a Issues

Dividir un PRD en issues independientes usando cortes verticales (trazadores), escritos como archivos markdown locales.

## Proceso

### 1. Localizar el PRD

Pedir al usuario la ruta del archivo PRD (ej. `issues/prd.md`).

Si el PRD no esta ya en tu ventana de contexto, leelo desde el archivo.

### 2. Explorar el codigo base (opcional)

Si aun no has explorado el codigo base, hazlo para entender el estado actual del codigo.

### 3. Definir cortes verticales

Dividir el PRD en issues de tipo **trazador**. Cada issue es un corte vertical delgado que atraviesa TODAS las capas de integracion de extremo a extremo, NO un corte horizontal de una sola capa.

Los cortes pueden ser 'HITL' o 'AFK'. Los cortes HITL requieren interaccion humana, como una decision arquitectonica o una revision de diseno. Los cortes AFK pueden implementarse y mergearse sin interaccion humana. Preferir AFK sobre HITL donde sea posible.

<vertical-slice-rules>
- Cada corte entrega un camino estrecho pero COMPLETO a traves de cada capa (esquema, API, UI, tests)
- Un corte completado es demostrable o verificable por si solo
- Preferir muchos cortes delgados sobre pocos gruesos
</vertical-slice-rules>

### 4. Consultar al usuario

Presentar el desglose propuesto como una lista numerada. Para cada corte, mostrar:

- **Titulo**: nombre corto y descriptivo
- **Tipo**: HITL / AFK
- **Bloqueado por**: que otros cortes (si hay) deben completarse primero
- **Historias de usuario cubiertas**: que historias de usuario del PRD aborda

Preguntar al usuario:

- ¿La granularidad se siente correcta? (demasiado gruesa / demasiado fina)
- ¿Las relaciones de dependencia son correctas?
- ¿Algun corte deberia fusionarse o dividirse mas?
- ¿Los cortes correctos estan marcados como HITL y AFK?

Iterar hasta que el usuario apruebe el desglose.

### 5. Crear los archivos de issues

Para cada corte aprobado, escribir un archivo markdown en `issues/` usando el patron de nombre `issues/NNN-titulo-corto.md` (ej. `issues/001-agregar-autenticacion.md`).

Numerar los issues comenzando desde el siguiente numero disponible (revisar que archivos ya existen en `issues/`).

Crear archivos en orden de dependencia (los bloqueadores primero) para poder referenciar nombres de archivos reales en el campo "Bloqueado por".

NO usar `gh issue create` ni ningun comando de GitHub CLI. NO referenciar numeros de issues de GitHub. Usar nombres de archivos locales para todas las referencias cruzadas.

<issue-template>
## PRD padre

`issues/prd.md` (o el archivo PRD que se haya usado)

## Que construir

Una descripcion concisa de este corte vertical. Describir el comportamiento de extremo a extremo, no la implementacion capa por capa. Referenciar secciones especificas del PRD padre en lugar de duplicar contenido.

## Criterios de aceptacion

- [ ] Criterio 1
- [ ] Criterio 2
- [ ] Criterio 3

## Bloqueado por

- Bloqueado por `issues/NNN-titulo.md` (si aplica)

O "Ninguno - puede comenzar inmediatamente" si no hay bloqueadores.

## Historias de usuario abordadas

Referenciar por numero desde el PRD padre:

- Historia de usuario 3
- Historia de usuario 7

</issue-template>

NO cerrar ni modificar el archivo PRD padre.
