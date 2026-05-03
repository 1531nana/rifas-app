# Cuando usar mocks

Usar mocks **solo en limites del sistema**:

- APIs externas (pagos, email, etc.)
- Bases de datos (a veces - preferir BD de test)
- Tiempo/aleatoriedad
- Sistema de archivos (a veces)

No mockear:

- Tus propias clases/modulos
- Colaboradores internos
- Cualquier cosa que controles

## Disenar para facilitar el mockeo

En los limites del sistema, disenar interfaces que sean faciles de mockear:

**1. Usar inyeccion de dependencias**

Pasar dependencias externas en lugar de crearlas internamente:

```typescript
// Facil de mockear
function processPayment(order, paymentClient) {
  return paymentClient.charge(order.total);
}

// Dificil de mockear
function processPayment(order) {
  const client = new StripeClient(process.env.STRIPE_KEY);
  return client.charge(order.total);
}
```

**2. Preferir interfaces estilo SDK sobre fetchers genericos**

Crear funciones especificas para cada operacion externa en lugar de una funcion generica con logica condicional:

```typescript
// BIEN: Cada funcion es mockeable de forma independiente
const api = {
  getUser: (id) => fetch(`/users/${id}`),
  getOrders: (userId) => fetch(`/users/${userId}/orders`),
  createOrder: (data) => fetch('/orders', { method: 'POST', body: data }),
};

// MAL: Mockear requiere logica condicional dentro del mock
const api = {
  fetch: (endpoint, options) => fetch(endpoint, options),
};
```

El enfoque SDK significa:
- Cada mock retorna una forma especifica
- Sin logica condicional en la configuracion del test
- Mas facil de ver que endpoints ejercita un test
- Tipado seguro por endpoint
