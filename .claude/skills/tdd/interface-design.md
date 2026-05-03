# Diseno de interfaces para testabilidad

Las buenas interfaces hacen que el testing sea natural:

1. **Aceptar dependencias, no crearlas**

   ```typescript
   // Testeable
   function processOrder(order, paymentGateway) {}

   // Dificil de probar
   function processOrder(order) {
     const gateway = new StripeGateway();
   }
   ```

2. **Retornar resultados, no producir efectos secundarios**

   ```typescript
   // Testeable
   function calculateDiscount(cart): Discount {}

   // Dificil de probar
   function applyDiscount(cart): void {
     cart.total -= discount;
   }
   ```

3. **Superficie pequena**
   - Menos metodos = menos tests necesarios
   - Menos parametros = configuracion de tests mas simple
