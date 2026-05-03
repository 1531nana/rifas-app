# Tests buenos y malos

## Tests buenos

**Estilo integracion**: Probar a traves de interfaces reales, no mocks de partes internas.

```typescript
// BIEN: Prueba comportamiento observable
test("el usuario puede hacer checkout con un carrito valido", async () => {
  const cart = createCart();
  cart.add(product);
  const result = await checkout(cart, paymentMethod);
  expect(result.status).toBe("confirmed");
});
```

Caracteristicas:

- Prueba comportamiento que les importa a los usuarios/llamadores
- Usa solo la API publica
- Sobrevive refactorizaciones internas
- Describe QUE, no COMO
- Una afirmacion logica por test

## Tests malos

**Tests acoplados a detalles de implementacion**: Acoplados a la estructura interna.

```typescript
// MAL: Prueba detalles de implementacion
test("checkout llama a paymentService.process", async () => {
  const mockPayment = jest.mock(paymentService);
  await checkout(cart, payment);
  expect(mockPayment.process).toHaveBeenCalledWith(cart.total);
});
```

Senales de alerta:

- Mockear colaboradores internos
- Probar metodos privados
- Afirmar sobre conteos/orden de llamadas
- El test falla al refactorizar sin cambio de comportamiento
- El nombre del test describe COMO no QUE
- Verificar a traves de medios externos en lugar de la interfaz

```typescript
// MAL: Omite la interfaz para verificar
test("createUser guarda en la base de datos", async () => {
  await createUser({ name: "Alice" });
  const row = await db.query("SELECT * FROM users WHERE name = ?", ["Alice"]);
  expect(row).toBeDefined();
});

// BIEN: Verifica a traves de la interfaz
test("createUser hace al usuario recuperable", async () => {
  const user = await createUser({ name: "Alice" });
  const retrieved = await getUser(user.id);
  expect(retrieved.name).toBe("Alice");
});
```
