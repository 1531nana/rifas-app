# 🛣️ RUTAS Y ENDPOINTS IMPLEMENTADOS

**Fecha**: 2026-05-21  
**Status**: Basado en issues #001–#003 completados

---

## 📌 Endpoints Actuales (Completados)

### Backend: FastAPI

#### Health Check
```http
GET /health
Response: {"status": "ok"}
Auth: ❌ No requerida
Status: ✅ Implementado
```

---

### Autenticación (Issue #002)

#### Registrar Admin
```http
POST /auth/register
Content-Type: application/json

Body:
{
  "email": "admin@rifa.com",
  "password": "secure_password",
  "full_name": "Juan García"
}

Response (201):
{
  "id": 1,
  "email": "admin@rifa.com",
  "full_name": "Juan García",
  "created_at": "2026-05-21T10:00:00Z"
}

Auth: ❌ No requerida
Status: ✅ Implementado
```

#### Login
```http
POST /auth/login
Content-Type: application/x-www-form-urlencoded

Body:
email=admin@rifa.com&password=secure_password

Response (200):
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer"
}

Response (401):
{"detail": "Invalid credentials"}

Auth: ❌ No requerida
Status: ✅ Implementado
```

#### Refresh Token
```http
POST /auth/refresh
Authorization: Bearer <refresh_token>

Response (200):
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer"
}

Auth: ✅ Requerida (refresh_token)
Status: ✅ Implementado
```

---

### Rifas (Issue #003)

#### Listar Rifas del Admin
```http
GET /raffles
Authorization: Bearer <access_token>

Response (200):
[
  {
    "id": 1,
    "name": "Moto Mayo",
    "lottery_type": "Loteria Bogota",
    "total_numbers": 100,
    "ticket_price": 25000,
    "prize_description": "Moto 125cc",
    "draw_date": "2026-05-31T20:00:00Z",
    "public_token": "opaque_token_abc123xyz",
    "status": "active",
    "admin_id": 1,
    "created_at": "2026-05-21T10:00:00Z"
  }
]

Auth: ✅ Requerida
Status: ✅ Implementado
```

#### Crear Rifa
```http
POST /raffles
Authorization: Bearer <access_token>
Content-Type: application/json

Body:
{
  "name": "Moto Mayo",
  "lottery_type": "Loteria Bogota",
  "total_numbers": 100,
  "ticket_price": 25000,
  "prize_description": "Moto 125cc nuevecita",
  "draw_date": "2026-05-31T20:00:00Z"
}

Response (201):
{
  "id": 1,
  "name": "Moto Mayo",
  "lottery_type": "Loteria Bogota",
  "total_numbers": 100,
  "ticket_price": 25000,
  "prize_description": "Moto 125cc nuevecita",
  "draw_date": "2026-05-31T20:00:00Z",
  "public_token": "opaque_token_abc123xyz",
  "status": "active",
  "admin_id": 1,
  "created_at": "2026-05-21T10:00:00Z"
}

Auth: ✅ Requerida
Status: ✅ Implementado
```

#### Ver Detalle de Rifa
```http
GET /raffles/{raffle_id}
Authorization: Bearer <access_token>

Response (200):
{
  "id": 1,
  "name": "Moto Mayo",
  "lottery_type": "Loteria Bogota",
  "total_numbers": 100,
  "ticket_price": 25000,
  "prize_description": "Moto 125cc",
  "draw_date": "2026-05-31T20:00:00Z",
  "public_token": "opaque_token_abc123xyz",
  "status": "active",
  "admin_id": 1,
  "created_at": "2026-05-21T10:00:00Z",
  "reservations": [
    {
      "id": 1,
      "number": 42,
      "buyer_name": "Carlos",
      "buyer_phone": "+573001234567",
      "buyer_email": "carlos@email.com",
      "payment_method": "credit_card",
      "status": "paid",
      "expires_at": "2026-05-23T10:00:00Z"
    }
  ]
}

Auth: ✅ Requerida
Status: ✅ Implementado
```

#### Editar Rifa
```http
PATCH /raffles/{raffle_id}
Authorization: Bearer <access_token>
Content-Type: application/json

Body:
{
  "prize_description": "Moto 200cc mejorada",
  "lottery_type": "Loteria Medellin",
  "draw_date": "2026-06-01T20:00:00Z"
}

Response (200):
{
  "id": 1,
  "name": "Moto Mayo",
  "lottery_type": "Loteria Medellin",
  "total_numbers": 100,
  "ticket_price": 25000,
  "prize_description": "Moto 200cc mejorada",
  "draw_date": "2026-06-01T20:00:00Z",
  ...
}

Response (400):
{"detail": "Cannot modify ticket_price: active reservations exist"}

Auth: ✅ Requerida
Status: ✅ Implementado
```

#### Confirmar Pago en Efectivo
```http
PATCH /raffles/{raffle_id}/reservations/{reservation_id}/confirm-cash
Authorization: Bearer <access_token>

Response (200):
{
  "id": 1,
  "number": 42,
  "buyer_name": "Carlos",
  "buyer_phone": "+573001234567",
  "payment_method": "cash",
  "status": "paid",
  "updated_at": "2026-05-21T10:30:00Z"
}

Auth: ✅ Requerida
Status: ✅ Implementado
```

---

## ⏳ Endpoints Próximos (Issue #004+)

### Públicas (Sin Autenticación)

#### Ver Rifa Pública
```http
GET /public/raffles/{public_token}
# Issue #004
# Response: detalles de rifa (nombre, premio, fecha, precio, tipo)
```

#### Listar Números de Rifa
```http
GET /public/raffles/{public_token}/numbers
# Issue #005
# Response: lista de números con estados (available/reserved/sold)
```

#### Crear Reserva
```http
POST /public/reservations
# Issue #006
# Body: número, datos comprador, método pago
# Response: reserva creada con expires_at
```

#### Checkout Wompi
```http
POST /public/reservations/{id}/checkout
# Issue #007
# Response: enlace pago Wompi
```

#### Webhook Wompi
```http
POST /webhooks/wompi
# Issue #007
# Body: notificación Wompi
# Actualiza estado de reserva (paid/liberated)
```

#### Subir Imagen Premio
```http
POST /raffles/{id}/image
# Issue #010
# Body: archivo imagen (max 5MB, JPG/PNG/WebP)
# Respuesta: URL en Cloudinary
```

#### Registrar Ganador
```http
POST /raffles/{id}/winner
# Issue #013
# Body: {"number": 42}
# Respuesta: rifa cerrada, notificación WhatsApp
```

#### Ver Estadísticas Rifa
```http
GET /raffles/{id}/stats
# Issue #014
# Response: total recaudado, números vendidos, pendientes, etc.
```

#### Listar Compradores
```http
GET /raffles/{id}/buyers
# Issue #014
# Response: lista de compradores con nombre, celular, email, estado pago
```

---

## 🎨 Rutas Frontend (React)

### Implementadas

- `/` → Redirect a `/admin`
- `/admin` → AdminDashboard (login/registro/lista rifas)
- `/login` → Página de login (almacenada en AdminDashboard)

### Próximas

- `/r/{public_token}` → Vista pública rifa (#004)
- `/r/{public_token}/pay` → Grilla + reserva (#005, #006)
- `/dashboard/stats` → Estadísticas admin (#014)

---

## 📋 Modelos de Base de Datos

### Implementados

#### Admin
```python
id: int (PK)
email: str (unique)
password_hash: str (bcrypt)
full_name: str
created_at: datetime
```

#### Raffle
```python
id: int (PK)
admin_id: int (FK → Admin)
name: str
lottery_type: str
total_numbers: int
ticket_price: float
prize_description: str
prize_image_url: str (nullable)
draw_date: datetime
public_token: str (unique)
status: str (enum: active, closed)
created_at: datetime
updated_at: datetime
```

#### Reservation
```python
id: int (PK)
raffle_id: int (FK → Raffle)
number: int
buyer_name: str
buyer_phone: str
buyer_email: str (nullable)
payment_method: str (enum: credit_card, pse, cash)
status: str (enum: pending, paid, expired)
wompi_transaction_id: str (nullable)
expires_at: datetime
created_at: datetime
updated_at: datetime
```

---

## 🔐 Autenticación y Seguridad

### Implementado

- ✅ JWT (access token + refresh token)
- ✅ Bcrypt password hashing
- ✅ CORS configurado
- ✅ Admin isolation (no ver rifas de otros)
- ✅ Route protection (401 sin token)

### Por Implementar

- 🔒 Validación de firma Wompi webhook
- 🔒 Rate limiting
- 🔒 Email verification (opcional)
- 🔒 Role-based access control (RBAC)

---

## 📊 Test Coverage (Actual)

```
backend/tests/test_api.py
├── test_health.py ................. ✅ PASS
├── test_auth_register.py ........... ✅ PASS
├── test_auth_login.py .............. ✅ PASS
├── test_auth_refresh.py ............ ✅ PASS
├── test_raffles_create.py .......... ✅ PASS
├── test_raffles_list.py ............ ✅ PASS
├── test_raffles_get.py ............. ✅ PASS

Total: 7/7 ✅ PASS (100%)
```

---

**Documento generado**: 2026-05-21  
**Base**: Issues completados #001–#003  
**Próxima revisión**: Post-issue #004
