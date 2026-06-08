# Sección 2: Anatomía de la Complejidad

---

## Marco teórico aplicado

En *A Philosophy of Software Design*, John Ousterhout define la complejidad como cualquier cosa en la estructura de un sistema que dificulta entenderlo o modificarlo. La complejidad se manifiesta principalmente en tres síntomas: change amplification (un cambio lógico requiere editar muchos lugares), cognitive load (el desarrollador debe tener en mente demasiadas cosas al mismo tiempo) y unknown unknowns (no es obvio qué código hay que tocar para hacer un cambio).

La herramienta principal contra la complejidad es la **profundidad de los módulos**: un módulo profundo tiene una interfaz pequeña que oculta una implementación grande y compleja. Un módulo superficial tiene una interfaz del mismo tamaño que su implementación; agrega capas sin agregar valor.

Ousterhout también introduce el concepto de **Information Hiding**: los detalles de implementación de un módulo deben estar encapsulados y no deben ser visibles desde el exterior. Cuando estos detalles se filtran hacia otras capas, cualquier cambio interno se convierte en un cambio en cascada.

---

## Módulos profundos identificados

### 1. `services/raffles.py` — `reserve_number()`

**¿Cuál es el módulo?**
La función `reserve_number(session, raffle, payload)` en `backend/app/services/raffles.py` (línea 222).

**¿Qué problema resuelve?**
Reservar un número de rifa de forma segura: valida que la rifa esté activa, que el número esté en rango, que ninguna reserva vigente ocupe ese número, y crea la reserva con el plazo de expiración correcto según el método de pago.

**¿Por qué su interfaz es simple?**
El endpoint que la llama solo necesita invocarla con tres argumentos:

```python
# api/public.py — el consumidor no sabe nada de lo que hay adentro
return reserve_number(session, raffle, payload)
```

**¿Qué complejidad oculta internamente?**

```python
# services/raffles.py líneas 222–252
def reserve_number(session: Session, raffle: Raffle, payload: ReservationCreate) -> Reservation:
    if raffle.status != RaffleStatus.active:
        raise HTTPException(...)                         # 1. Valida estado de la rifa

    if payload.number >= raffle.total_numbers:
        raise HTTPException(...)                         # 2. Valida rango del número

    ahora = datetime.utcnow()
    candidatas = session.exec(                           # 3. Consulta reservas activas
        select(Reservation).where(
            Reservation.raffle_id == raffle.id,
            Reservation.number == payload.number,
            Reservation.status.in_([...]),
        )
    ).all()
    if any(_reserva_vigente(r, ahora) for r in candidatas):
        raise HTTPException(...)                         # 4. Detecta conflicto de reserva

    timeout = timedelta(days=5) if payload.payment_method == PaymentMethod.cash \
              else timedelta(hours=48)                   # 5. Calcula expiración según método de pago

    reservation = Reservation(...)                       # 6. Crea la reserva con todos sus campos
    session.add(reservation)
    session.commit()
    session.refresh(reservation)
    return reservation
```

**¿Por qué es un módulo profundo?**
Oculta seis pasos distintos (validación de estado, validación de rango, consulta SQL, lógica de vigencia, política de expiración por método de pago y persistencia) detrás de una sola invocación. El ratio interfaz/implementación es muy favorable.

---

### 2. `lib/api.js` — `request()`

**¿Cuál es el módulo?**
La función `request(path, options)` en `frontend/src/lib/api.js` (línea 20).

**¿Qué problema resuelve?**
Centraliza todas las llamadas HTTP del frontend, incluyendo autenticación, renovación automática de tokens y parseo uniforme de errores.

**¿Por qué su interfaz es simple?**
Desde cualquier componente:

```javascript
const data = await request(`/r/${token}`);
```

**¿Qué complejidad oculta internamente?**

```javascript
// lib/api.js líneas 20–58
export async function request(path, options = {}) {
  const token = localStorage.getItem("rifas_token");   // 1. Inyecta token de autenticación
  const response = await fetch(`${API_URL}${path}`, {
    ...options,
    headers: { "Content-Type": "application/json",
                Authorization: `Bearer ${token}`, ... },
  });

  if (response.status === 401 && localStorage.getItem("rifas_refresh")) {
    const newToken = await attemptRefresh();            // 2. Detecta 401 y renueva token
    if (newToken) {
      const retry = await fetch(...);                  // 3. Reintenta la petición original
      const data = await retry.json().catch(() => null);
      if (!retry.ok) throw ...;
      return data;
    }
  }

  const data = await response.json().catch(() => null);
  if (!response.ok) {
    const error = new Error(parsearMensajeError(data?.detail)); // 4. Parsea errores de FastAPI
    throw error;
  }
  return data;
}
```

La función `attemptRefresh()` adicional deduplica refreshes concurrentes mediante el patrón `refreshPromise` (líneas 88–118), evitando múltiples llamadas simultáneas a `/auth/refresh`.

**¿Por qué es un módulo profundo?**
Encapsula el ciclo completo de autenticación y renovación de tokens. Ningún componente React conoce la existencia de tokens, refresh tokens, localStorage o el formato de errores de FastAPI.

---

### 3. `services/wompi.py` — `validar_firma_webhook()`

**¿Cuál es el módulo?**
La función `validar_firma_webhook(payload, events_key)` en `backend/app/services/wompi.py` (línea 52).

**¿Qué problema resuelve?**
Valida criptográficamente que un webhook recibido proviene de Wompi y no fue manipulado en tránsito.

**¿Por qué su interfaz es simple?**

```python
# api/webhooks.py — el endpoint solo llama una función
if not wompi.validar_firma_webhook(payload.model_dump(), settings.wompi_events_key):
    raise HTTPException(status_code=400, detail="Firma invalida")
```

**¿Qué complejidad oculta internamente?**

```python
# services/wompi.py líneas 52–76
def validar_firma_webhook(payload: dict, events_key: str) -> bool:
    try:
        signature = payload["signature"]
        properties: list[str] = signature["properties"]   # 1. Extrae propiedades a concatenar
        checksum: str = signature["checksum"]
        timestamp: int = payload["timestamp"]

        concatenated = ""
        data = payload["data"]
        for prop in properties:                           # 2. Recorre rutas anidadas tipo "a.b.c"
            value: dict = data
            for key in prop.split("."):
                value = value[key]
            concatenated += str(value)

        concatenated += str(timestamp)                    # 3. Agrega timestamp
        concatenated += events_key                        # 4. Agrega clave secreta

        computed = hashlib.sha256(concatenated.encode()).hexdigest()  # 5. SHA-256
        return computed == checksum                       # 6. Compara con checksum de Wompi
    except (KeyError, TypeError):
        return False                                      # 7. Maneja payloads malformados
```

**¿Por qué es un módulo profundo?**
Implementa el algoritmo oficial de validación de Wompi con navegación dinámica de paths, criptografía y manejo de errores silencioso, todo detrás de un booleano.

---

### 4. `services/notifications.py` — `send_whatsapp()`

**¿Cuál es el módulo?**
La función `send_whatsapp(phone, template, params)` en `backend/app/services/notifications.py`.

**¿Qué complejidad oculta internamente?**
Detecta si está en modo sandbox (y en ese caso solo loguea), construye el payload de la API de Meta Cloud, hace la llamada HTTP, maneja errores sin propagar excepciones (el flujo de pago nunca se bloquea por un error de notificación) y retorna un booleano de éxito.

```python
# services/notifications.py línea 17
if settings.meta_sandbox or not settings.meta_api_token or not settings.meta_phone_number_id:
    logger.info("[SANDBOX] WhatsApp to %s ...", phone, template, params or {})
    return True  # En sandbox, simula éxito sin llamadas externas
```

**¿Por qué es profundo?**
Tres servicios distintos (`raffles.py`, `ganador.py`, `recordatorio.py`) simplemente llaman `send_whatsapp(phone, template, params)` sin conocer si hay credenciales reales, si hay sandbox, ni la estructura de la API de Meta.

---

## Módulos superficiales identificados

### 1. `services/pagos.py` — `confirmar_pago()` y `cancelar_pago()`

**¿Qué módulo o archivo era superficial?**
El archivo `backend/app/services/pagos.py` contiene solo dos funciones de ~10 líneas cada una. Cada función hace exactamente una consulta SQL y un cambio de estado:

```python
# services/pagos.py — confirmar_pago(), líneas 8–19
def confirmar_pago(session: Session, reservation_id: int) -> None:
    reservation = session.exec(
        select(Reservation).where(Reservation.id == reservation_id)
    ).first()
    if reservation is None or reservation.status != ReservationStatus.pending:
        return
    reservation.status = ReservationStatus.paid
    reservation.paid_at = datetime.utcnow()
    session.add(reservation)
    session.commit()
```

**¿Por qué aumentaba la complejidad?**
La lógica es casi idéntica a lo que `services/raffles.py` ya hace en `confirm_cash_payment()`. Un desarrollador nuevo debe navegar a un archivo separado para entender una operación trivial, lo que aumenta el cognitive load sin aportar abstracción adicional.

**¿Qué problema generaba en el mantenimiento?**
Si se cambia la lógica de transición de estado de `Reservation` (por ejemplo, agregar un evento de auditoría), hay que actualizar tanto `pagos.py` como `raffles.py`, que manejan la misma entidad con lógica similar.

**¿Qué directriz humana se dio para corregirlo?**
El equipo estableció en `CLAUDE.md` que los servicios deben organizarse por dominio, no por punto de entrada. La lógica de confirmación de pagos por webhook debería consolidarse en `services/raffles.py` o en un módulo de estado de reservas, no en un archivo separado llamado `pagos.py`.

**¿Se unificó, se eliminó o se mejoró?**
El archivo existe pero no fue fusionado. La directriz humana identificó el problema; la corrección quedó pendiente de refactor.

---

### 2. `models/validators.py` — archivo de una sola función

**¿Qué módulo o archivo era superficial?**
`backend/app/models/validators.py` tiene 10 líneas y una única función:

```python
# models/validators.py
PHONE_RE = re.compile(r"^\+\d[\d\s\-]{6,29}$")

def validate_phone(value: str) -> str:
    if not PHONE_RE.match(value):
        raise ValueError("El celular debe estar en formato internacional (ej: +573001112233)")
    return value
```

**¿Por qué aumentaba la complejidad?**
Un archivo que solo contiene un regex y una función de validación genera un módulo con interfaz = implementación. No oculta nada que no sea obvio leer en el sitio donde se usa.

**¿Qué problema generaba en el mantenimiento?**
Requiere un import adicional en `schemas.py` para una operación que podría estar inline en el validador de Pydantic, o agrupada con otras validaciones relacionadas si existieran más.

**¿Qué directriz humana se dio para corregirlo?**
`CLAUDE.md` establece: *"No crear archivos de utilidades genéricos. Nombrarlos por su dominio."* El archivo fue creado correctamente con nombre de dominio (`validators.py`), pero su superficialidad indica que fue creado prematuramente anticipando más validadores que nunca llegaron.

**¿Se unificó, se eliminó o se mejoró?**
Se mantuvo, pero la directriz indica que debería crecer (agregando validaciones de `buyer_name`, `draw_date`, etc.) o fusionarse directamente en el schema donde se usa.

---

## Directrices humanas para mejorar la profundidad de los módulos

Las siguientes intervenciones humanas corrigieron o previnieron módulos superficiales:

**1. Consolidación de lógica de vigencia de reserva:**
La función privada `_reserva_vigente(reservation, ahora)` en `services/raffles.py` (línea 138) fue identificada como lógica que la IA inicialmente replicaba en múltiples funciones (`get_number_states`, `get_raffle_detail`, `get_raffle_stats`). La directriz humana fue extraerla a una función pura privada y llamarla desde todos los sitios:

```python
# services/raffles.py — función pura sin dependencias externas
def _reserva_vigente(reservation: Reservation, ahora: datetime) -> bool:
    """Función pura: determina si una reserva ocupa un número sin tocar la BD."""
    if reservation.status == ReservationStatus.paid:
        return True
    if reservation.status == ReservationStatus.pending:
        return reservation.expires_at > ahora
    return False
```

**2. Un archivo por responsabilidad en el frontend:**
La directriz `CLAUDE.md` establece que los componentes auxiliares no deben definirse dentro del mismo archivo de una página. La IA inicialmente generó `ReservaModal` dentro de `PublicRaffle.jsx`. La instrucción humana la separó a su propio archivo `ReservaModal.jsx`.

**3. Constantes compartidas en `lib/constants.js`:**
Los valores `AVISO_PAGO`, `LABEL_BOTON_PAGO` y `EMPTY_BUYER` fueron inicialmente definidos inline dentro de `ReservaModal.jsx`. La directriz humana los movió a `lib/constants.js` para evitar duplicación cuando `AdminDashboard.jsx` necesitara los mismos valores:

```javascript
// lib/constants.js — extraído por directriz humana
export const AVISO_PAGO = {
  cash: "Contacta al organizador para coordinar el pago. Tienes 5 días.",
  card: "Serás redirigido a Wompi para completar el pago con tarjeta ahora mismo.",
  pse:  "Serás redirigido a Wompi para completar el pago por PSE ahora mismo.",
};
```

**4. Separación wompi/pagos/webhooks:**
La lógica criptográfica de Wompi fue separada de la lógica de negocio de pagos. `services/wompi.py` maneja solo el protocolo Wompi (firmas, URLs, referencias), mientras que `services/pagos.py` maneja solo el cambio de estado de la reserva. El endpoint `api/webhooks.py` orquesta ambos sin mezclar sus responsabilidades.

---

## Fugas de información detectadas

### Fuga 1: El frontend codifica la regla de negocio de los 5 días

**¿Dónde ocurrió la fuga?**
`frontend/src/pages/PublicRaffle.jsx`, línea 45:

```javascript
// PublicRaffle.jsx línea 45
setNotice("¡Número reservado! Tienes 5 días para completar el pago en efectivo.");
```

**¿Qué detalle interno se filtró?**
La regla de negocio "las reservas en efectivo expiran en 5 días" está definida en el backend:

```python
# services/raffles.py línea 239
timeout = timedelta(days=5) if payload.payment_method == PaymentMethod.cash else timedelta(hours=48)
```

El frontend hardcodeó el valor "5 días" directamente en el mensaje al usuario, creando una dependencia oculta con el backend.

**¿Por qué era un problema?**
Si el negocio decide cambiar el plazo a 3 días, hay que modificar dos archivos en dos repositorios distintos. El backend cambia, pero la UI sigue diciéndole al usuario "5 días". Este es el síntoma clásico de change amplification.

**¿Cómo aplicaron Information Hiding?**
La solución correcta es que el backend devuelva el campo `expires_at` en la respuesta de reserva (ya lo hace en `ReservationRead`), y el frontend lo calcule a partir de esa fecha en lugar de hardcodear el texto.

**¿Qué capa quedó encargada de ocultar ese detalle?**
El servicio `reserve_number()` en el backend. El dato `expires_at` ya se expone en `ReservationRead`; la UI solo necesita leerlo.

---

### Fuga 2: El frontend conoce qué métodos de pago redirigen a Wompi

**¿Dónde ocurrió la fuga?**
`frontend/src/pages/ReservaModal.jsx`, línea 16:

```javascript
// ReservaModal.jsx línea 16
if (reserva && buyer.payment_method !== "cash") {
  setRedirigiendo(true);
  const checkout = await request(`/r/${token}/reservations/${reserva.id}/checkout`, { method: "POST" });
  window.location.href = checkout.checkout_url;
}
```

**¿Qué detalle interno se filtró?**
La decisión de que `card` y `pse` redirigen a Wompi (y `cash` no) es lógica de negocio del backend. El frontend replicate esta decisión al verificar `payment_method !== "cash"`.

**¿Por qué era un problema?**
Si se agrega un nuevo método de pago en línea (por ejemplo, `nequi`), hay que actualizar el backend Y el frontend. La condición de bifurcación está duplicada.

**¿Cómo aplicaron Information Hiding?**
El endpoint de checkout podría devolver un campo `redirect_required: bool` o `checkout_url: null` cuando el pago es en efectivo. El frontend solo verificaría si `checkout_url` existe, sin conocer qué métodos son online.

**¿Qué capa quedó encargada de ocultar ese detalle?**
Debería ser el backend en el endpoint `/checkout`. En el estado actual, la lógica está repartida entre ambas capas.

---

### Fuga 3: HTTPException en la capa de servicios

**¿Dónde ocurrió la fuga?**
`services/raffles.py` (líneas 64, 80, 86, 134, 224, 226, 237, 263–267), `services/ganador.py` (líneas 12, 21–25) y `services/wompi.py` (líneas 115, 118, 122).

```python
# services/raffles.py línea 64 — HTTPException en la capa de servicios
raise HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="No se puede cambiar el precio ni la cantidad de numeros porque hay reservas activas",
)
```

**¿Qué detalle interno se filtró?**
`HTTPException` es una abstracción del protocolo HTTP, perteneciente a FastAPI. Al usarla en la capa de servicios, la capa de negocio conoce detalles del transporte HTTP (códigos de estado, estructura de respuesta de error).

**¿Por qué era un problema?**
Si en el futuro se expone la misma lógica vía CLI, WebSocket o tarea schedulada (como ya ocurre con `run_expiration_job`), los servicios que lanzan `HTTPException` fallarán de forma incoherente porque no están en un contexto HTTP.

**¿Cómo aplicaron Information Hiding?**
La solución es que los servicios lancen excepciones de dominio propias (`ReservaConflictoError`, `RifaCerradaError`) y que la capa `api/` las capture y las convierta en `HTTPException`. Así la capa de negocio no conoce HTTP.

**¿Qué capa quedó encargada de ocultar ese detalle?**
Debería ser exclusivamente `api/`. En el estado actual, la responsabilidad está mezclada.

---

## Aplicación de Information Hiding

Los casos donde el equipo aplicó Information Hiding correctamente:

| Módulo | Detalle oculto | Capa que lo encapsula |
|--------|---------------|----------------------|
| `lib/api.js` | Tokens JWT, lógica de refresh, formato de errores FastAPI | `lib/api.js` — ningún componente toca `localStorage` directamente |
| `services/wompi.py` | Algoritmo SHA-256 de validación de firma Wompi, estructura del payload | `services/wompi.py` — el webhook solo llama `validar_firma_webhook()` |
| `services/notifications.py` | API de Meta Cloud, modo sandbox, formato de components WhatsApp | `services/notifications.py` — los servicios solo llaman `send_whatsapp()` |
| `core/security.py` | Algoritmo JWT, bcrypt, claims internos del token | `core/security.py` — `deps.py` solo llama `decode_access_token()` |
| `services/raffles.py` | Lógica de vigencia de reserva (función `_reserva_vigente`) | privada dentro del módulo — usada en 3 funciones sin reexponerse |
| `lib/constants.js` | Textos de aviso y labels de botones por método de pago | `lib/constants.js` — componentes los importan sin conocer la lógica detrás |

---


## Conclusión de la sección

El proyecto **rifas-app** muestra una arquitectura con buena tendencia hacia módulos profundos en las capas de infraestructura y servicios externos. Las funciones `request()`, `send_whatsapp()`, `validar_firma_webhook()` y `reserve_number()` son ejemplos claros donde interfaces pequeñas ocultan implementaciones complejas.

Las principales oportunidades de mejora identificadas son:

1. **Eliminar HTTPException de los servicios**: la lógica de negocio no debería conocer el protocolo HTTP. Esto es la fuga de información más sistémica del proyecto.

2. **Consolidar `services/pagos.py`**: las dos funciones del archivo podrían fusionarse en `services/raffles.py` o en un módulo de estados de reserva más rico, eliminando un módulo superficial.

3. **Cerrar la fuga del plazo en efectivo**: el campo `expires_at` ya existe en la respuesta del backend. El frontend debe leerlo en lugar de hardcodear "5 días".

4. **Abstraer la decisión de redirección a Wompi**: mover la condición `payment_method !== "cash"` al backend para que el frontend solo reaccione a la presencia o ausencia de `checkout_url`.

La raíz común de los problemas identificados es que la IA generó código funcional pero sin evaluar el costo futuro de los acoplamientos entre capas. Las directrices humanas documentadas en `CLAUDE.md` fueron el mecanismo principal para corregir estos patrones: separar archivos por responsabilidad, prohibir lógica de negocio en la capa `api/` y centralizar constantes compartidas.