# 📋 INVENTARIO COMPLETO DE ISSUES — Rifas App

**Fecha**: 2026-05-21  
**Total Issues**: 14 (+ 1 PRD padre)  
**Status**: 3 completados / 14 pendientes (21% completado)

---

## 📊 RESUMEN POR ESTADO

| Estado | Cantidad | Issues |
|--------|----------|--------|
| ✅ **Completado** | 3 | #001, #002, #003 |
| ⏳ **Listo para ejecutar** | 1 | #004 (desbloqueado) |
| 🔒 **Bloqueado** | 10 | #005–#014 |
| **TOTAL** | 14 | - |

---

## 📄 INVENTARIO DETALLADO

### ✅ COMPLETADOS (3/14)

---

#### **#001: Scaffold del Proyecto**
- **Estado**: ✅ COMPLETADO
- **Dependencias**: Ninguna (primer issue)
- **Qué construye**: 
  - Estructura backend: FastAPI + SQLModel + Alembic
  - Estructura frontend: React + Vite + TailwindCSS
  - Conexión PostgreSQL configurada
  - Endpoint `/health` funcional
  - Variables de entorno documentadas

- **Criterios de aceptación**:
  - [x] `GET /health` retorna `{"status": "ok"}` ✅
  - [x] Frontend carga sin errores ✅
  - [x] TailwindCSS está activo ✅
  - [x] Alembic configurado ✅
  - [x] `.env.example` documentado ✅

- **Comentarios técnicos**:
  - Stack: FastAPI + SQLModel + React 19 + Vite 6 + TailwindCSS
  - Base sólida para desarrollo

---

#### **#002: Autenticación de Admin**
- **Estado**: ✅ COMPLETADO
- **Depende de**: #001 (scaffold)
- **Qué construye**:
  - Flujo de registro y login
  - JWT tokens (access + refresh)
  - Bcrypt password hashing
  - Protección de rutas backend
  - Páginas login/registro frontend

- **Criterios de aceptación**:
  - [x] `POST /auth/register` con bcrypt ✅
  - [x] `POST /auth/login` retorna JWT ✅
  - [x] `POST /auth/login` rechaza credenciales inválidas (401) ✅
  - [x] `POST /auth/refresh` funciona ✅
  - [x] Rutas protegidas rechazan sin token ✅
  - [x] Frontend: login/registro funcionales ✅
  - [x] Redirección post-login ✅
  - [x] Botón logout limpia tokens ✅
  - [x] Rutas protegidas redirigen a login ✅

- **Comentarios técnicos**:
  - Security: JWT + bcrypt estándar
  - Manejo de tokens: access (corta duración) + refresh (larga)

---

#### **#003: CRUD de Rifas**
- **Estado**: ✅ COMPLETADO
- **Depende de**: #002 (autenticación)
- **Qué construye**:
  - Crear, listar, ver detalles, editar rifas
  - Generación automática de `public_token`
  - Restricciones de edición (no permitir cambios de precio/cantidad si hay reservas)
  - Aislamiento entre admins (no ver rifas de otros)
  - Formularios frontend

- **Criterios de aceptación**:
  - [x] `POST /raffles` crea rifa ✅
  - [x] Se genera `public_token` único ✅
  - [x] `GET /raffles` lista rifas del admin autenticado ✅
  - [x] `GET /raffles/{id}` detalle de rifa ✅
  - [x] `PATCH /raffles/{id}` edita descripción, tipo, fecha ✅
  - [x] `PATCH` rechaza cambios de precio si hay reservas ✅
  - [x] Admin no ve rifas de otros ✅
  - [x] Frontend: lista de rifas en dashboard ✅
  - [x] Frontend: formulario creación ✅
  - [x] Frontend: formulario edición ✅

- **Comentarios técnicos**:
  - Token opaco para acceso público
  - Validaciones de negocio (precio no editable con reservas)
  - Modelado: Admin (1:N) → Raffle

---

### ⏳ LISTO PARA EJECUTAR (1/14)

---

#### **#004: Vista Pública de la Rifa**
- **Estado**: ⏳ DESBLOQUEADO (listo ahora)
- **Depende de**: #003 (CRUD rifas completado ✅)
- **Bloqueado por**: Ninguno
- **Qué construye**:
  - Página pública sin autenticación
  - Acceso vía `public_token`
  - Muestra detalles: nombre, premio, descripción, fecha, precio, tipo

- **Criterios de aceptación** (9 totales):
  - [ ] `GET /public/raffles/{public_token}` retorna info sin auth
  - [ ] 404 si token no existe
  - [ ] Frontend renderiza en `/r/{public_token}`
  - [ ] Muestra: nombre, premio, fecha, precio, tipo
  - [ ] Responsive mobile
  - [ ] Mensaje si rifa está cerrada

- **Desbloquea**:
  - #005 (grilla de números)

---

### 🔒 BLOQUEADOS (10/14)

**Nota**: Los siguientes están bloqueados por sus dependencias. Se desbloquean secuencialmente.

---

#### **#005: Grilla de Números**
- **Estado**: 🔒 BLOQUEADO
- **Bloqueado por**: #004 (vista pública)
- **Qué construye**:
  - Grilla visual de números (verde=disponible, amarillo=reservado, rojo=vendido)
  - Cálculo de estados dinámico
  - Clickeable solo para verdes
  - Responsive mobile

- **Criterios de aceptación** (7 totales):
  - [ ] `GET /public/raffles/{token}/numbers` retorna lista con estado
  - [ ] Estados: `available`, `reserved`, `sold`
  - [ ] `reserved` con `expires_at` pasado → `available`
  - [ ] Grilla renderiza con colores
  - [ ] Solo verdes clickeables
  - [ ] Responsive
  - [ ] Estado en tiempo real al cargar

- **Desbloquea**:
  - #006 (reserva números)

---

#### **#006: Reserva de Números**
- **Estado**: 🔒 BLOQUEADO
- **Bloqueado por**: #005 (grilla números)
- **Qué construye**:
  - Modal de selección/reserva
  - Recolección datos comprador (nombre, celular, email)
  - Selección método pago (digital/efectivo)
  - Cálculo de tiempos de expiración

- **Criterios de aceptación** (9 totales):
  - [ ] `POST /public/reservations` crea reserva
  - [ ] 409 si número ya está reservado
  - [ ] `expires_at = now() + 48h` para digital
  - [ ] `expires_at = now() + 5 días` para efectivo
  - [ ] Número aparece amarillo tras reserva
  - [ ] Modal con formulario
  - [ ] Muestra plazo claramente
  - [ ] Validación celular (formato WhatsApp)
  - [ ] Error si número tomado concurrentemente

- **Desbloquea**:
  - #007 (pago Wompi)
  - #008 (pago efectivo)
  - #009 (expiración reservas)

---

#### **#007: Pago Wompi (Tarjeta/PSE)**
- **Estado**: 🔒 BLOQUEADO
- **Bloqueado por**: #006 (reservas)
- **Qué construye**:
  - Integración Wompi API
  - Checkout link generation
  - Webhook processing
  - Estados de pago: APPROVED → paid, DECLINED/VOIDED → liberar

- **Criterios de aceptación** (8 totales):
  - [ ] `POST /public/reservations/{id}/checkout` genera link Wompi
  - [ ] Frontend redirige a checkout
  - [ ] `POST /webhooks/wompi` procesa notificaciones
  - [ ] APPROVED → `paid`, número rojo
  - [ ] DECLINED → liberar número, vuelve verde
  - [ ] Validación de firma Wompi
  - [ ] Página confirmación exitosa
  - [ ] Página error/reintento

- **Desbloquea**:
  - #014 (dashboard estadísticas)

---

#### **#008: Pago en Efectivo**
- **Estado**: 🔒 BLOQUEADO
- **Bloqueado por**: #006 (reservas)
- **Qué construye**:
  - Instrucciones para pago en efectivo
  - Endpoint para que admin confirme pago
  - Panel admin con lista de compradores
  - Filtros por estado de pago

- **Criterios de aceptación** (6 totales):
  - [ ] Mensaje con instrucciones al seleccionar efectivo
  - [ ] `PATCH /reservations/{id}/confirm-cash` confirma pago
  - [ ] Solo admin dueño puede confirmar
  - [ ] Número aparece rojo tras confirmar
  - [ ] Panel admin muestra compradores con estado
  - [ ] Filtros por estado de pago

- **Desbloquea**:
  - #011 (notificaciones WhatsApp)
  - #014 (dashboard estadísticas)

---

#### **#009: Expiración de Reservas**
- **Estado**: 🔒 BLOQUEADO
- **Bloqueado por**: #006 (reservas)
- **Qué construye**:
  - Job periódico (cada 15-30 min)
  - Marca reservas expiradas
  - Libera números

- **Criterios de aceptación** (5 totales):
  - [ ] Job corre periódicamente
  - [ ] Marca `expired` si `expires_at < now()`
  - [ ] Números aparecen verdes al recargar
  - [ ] Idempotente (sin efectos duplicados)
  - [ ] Errores en logs, no detiene servidor

- **Desbloquea**:
  - Ninguno directo (mejora UX)

---

#### **#010: Imagen del Premio**
- **Estado**: 🔒 BLOQUEADO
- **Bloqueado por**: #003 (CRUD rifas)
- **Qué construye**:
  - Subida a Cloudinary
  - URL pública guardada
  - Mostrada en vista pública
  - Validaciones: max 5MB, JPG/PNG/WebP

- **Criterios de aceptación** (8 totales):
  - [ ] `POST /raffles/{id}/image` sube a Cloudinary
  - [ ] Campo opcional
  - [ ] Límite 5MB
  - [ ] Formatos: JPG, PNG, WebP
  - [ ] URL en `GET /public/raffles/{token}`
  - [ ] Campo en formulario frontend
  - [ ] Muestra en vista pública
  - [ ] Placeholder si no hay imagen

- **Desbloquea**:
  - Ninguno directo (mejora UX)

---

#### **#011: Notificaciones WhatsApp**
- **Estado**: 🔒 BLOQUEADO
- **Bloqueado por**: #008 (pago efectivo)
- **Qué construye**:
  - Módulo notificaciones
  - Integración Meta Cloud API
  - Template de confirmación pago
  - Manejo de errores (fallo silencioso con log)
  - Modo sandbox

- **Criterios de aceptación** (6 totales):
  - [ ] Función `send_whatsapp(phone, template, params)`
  - [ ] Envía vía Meta API
  - [ ] Errores en logs, no detienen flujo
  - [ ] Envía automático tras confirmar efectivo
  - [ ] Template aprobado en Meta
  - [ ] Modo prueba disponible

- **Desbloquea**:
  - #012 (recordatorio pago)
  - #013 (registro ganador)

---

#### **#012: Recordatorio de Pago por WhatsApp**
- **Estado**: 🔒 BLOQUEADO
- **Bloqueado por**: #011 (WhatsApp setup)
- **Qué construye**:
  - Job diario
  - Detecta reservas sin pagar
  - Sorteo en 15 días
  - Envía recordatorio WhatsApp

- **Criterios de aceptación** (7 totales):
  - [ ] Job corre 1 vez/día
  - [ ] Identifica `pending` con `draw_date` en 15 días (±1)
  - [ ] Envía WhatsApp
  - [ ] Mensaje incluye: nombre, número, rifa, fecha, plazo
  - [ ] Max 1 recordatorio/reserva
  - [ ] Idempotente
  - [ ] Errores individuales no detienen job

- **Desbloquea**:
  - Ninguno directo

---

#### **#013: Registro de Ganador**
- **Estado**: 🔒 BLOQUEADO
- **Bloqueado por**: #011 (WhatsApp setup)
- **Qué construye**:
  - Endpoint para registrar número ganador
  - Validación: número debe estar pagado
  - Cierre de rifa
  - Notificación WhatsApp al ganador

- **Criterios de aceptación** (8 totales):
  - [ ] `POST /raffles/{id}/winner` registra ganador
  - [ ] Error si número no está pagado
  - [ ] Rifa queda `closed`
  - [ ] WhatsApp al ganador
  - [ ] Rifa cerrada rechaza nuevas reservas
  - [ ] Vista pública muestra número ganador
  - [ ] Botón "Registrar ganador" en panel admin
  - [ ] Solo admin dueño puede

- **Desbloquea**:
  - Ninguno directo

---

#### **#014: Dashboard y Estadísticas**
- **Estado**: 🔒 BLOQUEADO
- **Bloqueado por**: #007 (Wompi) + #008 (efectivo)
- **Qué construye**:
  - Métricas por rifa
  - Total recaudado
  - Porcentaje vendidos
  - Listado de compradores
  - Grilla en tiempo real

- **Criterios de aceptación** (6 totales):
  - [ ] `GET /raffles/{id}/stats` retorna: total, vendidos, reservados, disponibles, pendientes
  - [ ] Dashboard resume metricas por rifa
  - [ ] Vista detalle muestra estadísticas completas
  - [ ] `GET /raffles/{id}/buyers` lista compradores
  - [ ] Admin ve grilla con estados
  - [ ] Lista compradores en panel

- **Desbloquea**:
  - Ninguno (último issue de flujo principal)

---

## 🔍 BÚSQUEDA DE MARCAS EN EL CÓDIGO

### Resultado: ❌ SIN TODO/FIXME/HACK ENCONTRADOS

Se ejecutó búsqueda en:
- `backend/**` → Sin matches
- `frontend/**` → Sin matches (excepto en package-lock.json que es ignorable)

**Conclusión**: El código actual está limpio, sin deuda técnica documentada.

---

## 📊 GRAFO DE DEPENDENCIAS

```
#001 (scaffold)
  └─ #002 (auth)
      └─ #003 (CRUD rifas)
          ├─ #004 (vista pública)
          │   └─ #005 (grilla)
          │       └─ #006 (reservas)
          │           ├─ #007 (pago Wompi) ─┐
          │           ├─ #008 (efectivo) ─┐ │
          │           └─ #009 (expiración) │ │
          ├─ #010 (imagen) ─────────────────┘ │
          │                                     │
          ├─ #008 (efectivo) ┐                 │
          │                  └─ #011 (WhatsApp) ─┐
          │                      ├─ #012 (recordatorio)
          │                      └─ #013 (ganador)
          │
          └─ #014 (dashboard) ← #007 + #008 completados
```

---

## 📈 TIMELINE ESTIMADO

| Ciclo | Issues | Estimado | Criterio |
|-------|--------|----------|----------|
| 1 | #001–#003 | ✅ Completado | Scaffold + Auth + CRUD |
| 2 | #004 | Ahora listo | Vista pública |
| 3 | #005–#006 | Tras #004 | Grilla + Reservas |
| 4 | #007–#009 | Tras #006 | Pagos + Expiración |
| 5 | #010–#011 | Paralelo | Imagen + WhatsApp |
| 6 | #012–#014 | Final | Recordatorios + Dashboard |

---

## ✅ ENTREGABLES POR ISSUE

Por cada issue completado, verificar:
1. Todos los criterios de aceptación ✅
2. Tests en verde (pytest, npm test)
3. Commits con formato `feat(#<ID>): ...`
4. Entrada en `handoffs.md`
5. Código sin FIXME/TODO
6. Auditoría QA completada

---

**Documento generado**: 2026-05-21  
**Status**: Listo para compartir con equipo  
**Siguiente paso**: Ejecutar `./ralph/once.ps1 004`
