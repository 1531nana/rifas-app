# Sección 3: El Veredicto Retrospectivo de los Sub-Agentes

> **Responsable:** Persona 5
> Conectar el Punto de Control Arquitectónico (Tarea 2) con el resultado final del sprint.
> Referencia base: `architecture-checkpoint.md` en la raíz del repositorio.

###empezar aqui

## Recuperación del Punto de Control Arquitectónico

El diagnóstico inicial (ver `architecture-checkpoint.md`) se ejecutó sobre la rama `develop` cuando ya existía el flujo base de rifas, reservas, pago en efectivo e integración Wompi. La fricción principal detectada fue el riesgo de agregar integraciones externas (Cloudinary, Meta Cloud API) directamente en los routers FastAPI o en componentes de UI, lo que dispersaría las reglas de negocio y haría difícil el testing.

**Candidatos de profundización detectados:**
- `backend/app/services/raffles.py`: concentraba lógica de rifa, reserva y confirmación de pago.
- `backend/app/api/raffles.py`: exponía endpoints administrativos con riesgo de crecer descontroladamente al agregar lógica de archivos.
- **Nuevo límite de integración**: Cloudinary y Meta Cloud API requerían sandbox y manejo de errores robusto para no bloquear los flujos transaccionales existentes.

---

## Debate de los tres sub-agentes

Durante el checkpoint arquitectónico, tres sub-agentes propusieron enfoques distintos para integrar Cloudinary y WhatsApp sin contaminar la capa de presentación.

### Sub-agente A — Servicio de aplicación extendido

```python
upload_prize_image(session, raffle, file) -> Raffle
confirm_cash_payment(session, raffle, reservation_id) -> Reservation
```

- **Ventaja principal**: los routers permanecen delgados y el flujo principal se mantiene en una sola capa de servicios.
- **Riesgo principal**: `services/raffles.py` podría crecer desproporcionadamente si todos los proveedores externos quedan allí.

### Sub-agente B — Puertos por integración

```python
CloudinaryImageStore.upload(file) -> str
WhatsAppNotifier.send(template, phone, params) -> bool
```

- **Ventaja principal**: proveedores reemplazables y pruebas unitarias más limpias (mock directo).
- **Riesgo principal**: agrega más clases de las necesarias para dos issues pequeños (#10 y #11), incrementando la carga cognitiva inicial.

### Sub-agente C — Endpoints directos con helpers locales

```python
POST /raffles/{id}/image
PATCH /reservations/{id}/confirm-cash
```

- **Ventaja principal**: implementación rápida, menor cantidad de archivos nuevos.
- **Riesgo principal**: reglas de validación, storage y notificación quedan mezcladas con FastAPI, dificultando los tests y reutilización posterior.

---

## Decisiones adoptadas

Se adoptó una **solución híbrida: A con una parte de B**.

| Recomendación | Implementación | Commit(s) |
|---------------|----------------|-----------|
| Extender `services/raffles.py` para flujo de rifa/reserva/pago | `upload_prize_image()` y `confirm_cash_payment()` viven allí | `f2e2f6b` |
| Puerto simple para WhatsApp | `services/notifications.py` con `send_whatsapp()` | `f2e2f6b` |
| Routers solo autentican y delegan | `api/raffles.py` mantiene grosor mínimo | `f2e2f6b` |
| Fallos de WhatsApp no revertir pago | `send_whatsapp()` retorna `bool`, loguea error, no levanta excepción | `f2e2f6b` |
| **Candidato 4 — Lectura pura** | `_reserva_vigente()` como función pura; `get_number_states()`, `get_raffle_detail()`, `get_raffle_stats()` y `reserve_number()` dejan de llamar `expire_old_reservations()` | `53105fe` |
| Un módulo por caso de uso nuevo | `services/ganador.py` e `services/recordatorio.py` | `7f94d57`, `4cd01ea` |

**PRs que materializaron las decisiones:**
- `#32` — CRUD rifas (base previa).
- `#35` — Handoffs issues #1-#9.
- `#36` — Issues #10-#14, handoffs finales y cierre de sprint.

---

## Decisiones descartadas

| Decisión descartada | Razón | Registro de deuda técnica |
|---------------------|-------|---------------------------|
| **Sub-agente A puro** (todo en `services/raffles.py`) | Evitar que el servicio de rifas absorbiera notificaciones y storage; se extrajo `notifications.py` como puerto. | Documentado en `handoffs.md`: candidatos 1, 2 y 3 del checkpoint arquitectónico no aplicados en su totalidad. |
| **Sub-agente B puro** (clases reemplazables por integración) | Para el alcance actual (#10 y #11) resultaba excesivo crear abstracciones de clase; una función pura con variables de entorno fue suficiente. | Deuda técnica conocida: si en el futuro se agregan SMS, push o email, se deberá refactorizar `notifications.py` a un patrón de puertos formales (clases/protocolos). |
| **Sub-agente C** (endpoints directos con lógica mezclada) | Rechazado explícitamente porque rompería la testabilidad y reutilización ya establecidas desde los issues #1-#9. | — |

---

## Impacto en la velocidad de desarrollo

El checkpoint **aceleró** el desarrollo de los issues finales.

- **#12 (recordatorio de pago)**: la existencia del puerto `send_whatsapp()` permitió implementar el job diario en `services/recordatorio.py` en pocas horas, reutilizando la infraestructura de #11 sin modificar confirmación de pago.
- **#13 (registro de ganador)**: el candidato 4 (lectura pura) hizo trivial agregar la validación de boleta pagada: `register_winner()` consulta el estado directamente sin preocuparse por side effects de expiración.
- **#14 (estadísticas)**: `get_raffle_stats()` pudo reutilizar `_reserva_vigente()` y el cálculo de estados ya existente en `get_number_states()`, sin tocar routers ni modelos.

En total, los tres issues se cerraron en un solo sprint sin bloqueos arquitectónicos.

---

## Elasticidad de la arquitectura frente al cambio

La arquitectura resultó **flexible** frente a los issues #12 y #13.

- **#12**: solo se agregó `services/recordatorio.py`, un campo `reminder_sent_at` en `Reservation` y una línea en el scheduler. Ni los routers ni la lógica de reserva existente fueron modificados.
- **#13**: se agregó `services/ganador.py`, un campo `winner_number` en `Raffle` y un endpoint en `api/raffles.py`. La notificación al ganador reutilizó `send_whatsapp()` sin cambiar `notifications.py`.
- **#14**: se agregaron dos funciones de lectura pura (`get_raffle_stats`, `get_raffle_buyers`) al servicio de rifas; el endpoint fue una línea de delegación.

En ningún caso fue necesario modificar más de un módulo por capa (modelo + servicio + router). La elasticidad provino de:
1. La separación servicio/lector ya existente.
2. El puerto de notificaciones estable.
3. La función pura `_reserva_vigente()` que evita que la lógica de expiración se replicara en cada lector nuevo.

---

## Change Amplification

**No ocurrió Change Amplification significativo** en los issues #10-#14.

- **Ejemplo de lo que se evitó**: si `send_whatsapp()` hubiera estado embebido en `confirm_cash_payment()`, agregar el recordatorio de pago (#12) o la notificación al ganador (#13) habría exigido modificar `services/raffles.py` o `services/ganador.py` directamente, encadenando cambios en tests y routers.
- **Decisión arquitectónica que lo previno**: el puerto `services/notifications.py` desacopló el envío de mensajes del flujo transaccional. Cada nuevo caso de uso (confirmación de pago, recordatorio, ganador) solo importa la función y la usa; no modifica su implementación.

El único punto de fricción menor fue la actualización del modelo `Reservation` con `reminder_sent_at`, que requirió recrear la base de datos de desarrollo (no hay migraciones automáticas configuradas aún), pero esto es una limitación operativa, no de arquitectura.

---

## Veredicto final

**Evaluación crítica: fue una buena arquitectura para el alcance del sprint.**

- El debate de sub-agentes **agregó valor real**, no fue ceremonial: obligó a rechazar la tentación de implementar rápido (Sub-agente C) y a encontrar un equilibrio entre extensibilidad y simplicidad (híbrido A+B).
- La decisión de mantener funciones puras para lectura (`_reserva_vigente`) pagó dividendos inmediatos en #12, #13 y #14: los nuevos endpoints de estadísticas y ganador no requirieron preocuparse por expiraciones ni transacciones de escritura.
- **¿Qué habría diseñado diferente desde el principio?**
  - Haber establecido `services/notifications.py` como un puerto formal (clase abstracta o protocolo) desde #11, para que la deuda técnica de "función pura vs. clase reemplazable" no existiera.
  - Incluir migraciones Alembic desde el scaffold (#1) para evitar recreaciones manuales de la BD al agregar campos como `reminder_sent_at` y `winner_number`.
  - Definir un módulo `services/ports/` desde el inicio, para que cada integración externa (Wompi, Cloudinary, Meta) tuviera su propio contrato explícito.

---

## Evidencias

1. **Reporte del checkpoint**: `architecture-checkpoint.md` en la raíz del repositorio. Resume el diagnóstico inicial, las tres propuestas y la justificación técnica de la híbrida.
2. **Comparación recomendaciones vs. decisiones finales**:
   - Checkpoint recomendó evitar crecimiento descontrolado de `api/raffles.py` → resultado: el router mantiene grosor mínimo (solo autenticación, validación de propiedad y delegación).
   - Checkpoint recomendó sandbox para Meta → resultado: `meta_sandbox` en `core/config.py` y modo no-bloqueante en `send_whatsapp()`.
3. **Tests como evidencia de velocidad**:
   - `pytest` backend: 33 passed en `f2e2f6b` (#10, #11); 50 passed en `4cd01ea` (#12, cierre sprint).
   - `npm run build` frontend: verde en todos los handoffs.
4. **Ejemplos de cambio fácil vs. difícil**:
   - **Fácil**: agregar `POST /raffles/{id}/winner` (#13). Se requirió un servicio nuevo de 48 líneas y un endpoint de 8 líneas, sin tocar confirmación de pago ni reservas.
   - **Difícil** (pre-checkpoint): confirmar pago en efectivo con notificación WhatsApp (#11). Sin la decisión híbrida, habría requerido modificar el mismo archivo que manejaba reservas, estadísticas y notificaciones, amplificando el cambio.
