# Solicitud de Proyecto - Sistema de Gestión de Rifas Digital

*De:* Cliente Final (Organizador de Rifas Tradicionales)  
*Para:* Equipo de Desarrollo  
*Fecha:* Mayo 2026

---

Hola equipo,

Actualmente organizamos rifas de manera tradicional y enfrentamos varios problemas que limitan nuestro alcance y generan mucho trabajo manual.

La forma actual de vender es mediante *talonarios físicos* que debemos llenar a mano y ofrecer *persona a persona. Esto hace que las ventas estén limitadas solo a las personas que conocemos o a las que podemos contactar directamente. No podemos llegar a más gente de la ciudad o ampliar el negocio. Además, todos los pagos se realizan **únicamente en efectivo*, lo que complica el seguimiento y genera riesgo de olvidos o boletas sin pagar.

Necesitamos modernizar este proceso creando una *aplicación web* que nos permita gestionar rifas de forma digital, manteniendo la simplicidad y confianza que requiere este tipo de actividad.

### Requerimientos principales:

*Usuarios del sistema:*
- *Admin / Vendedor*: Podrá crear cuenta, iniciar sesión y gestionar todo el sistema.
- *Comprador*: No necesita crear cuenta ni login. Accederá mediante un enlace público compartido por el admin.

*Funcionalidades para el Admin (Vendedor):*
- Crear una nueva rifa, donde podrá definir:
  - Tipo de lotería (o formato de rifa)
  - Cantidad de números totales
  - Valor de cada boleta
  - Cantidad y descripción detallada del premio
  - Fecha del sorteo
- Ver lista de todas sus rifas activas y finalizadas
- Ver listado de compradores con sus datos (nombre, celular, email, número comprado)
- Generar y compartir un *enlace público* para que los compradores accedan a la rifa
- Visualizar en tiempo real qué números están vendidos y cuáles están disponibles

*Funcionalidades para el Comprador:*
- Acceder al enlace de la rifa
- Ver la información completa de la rifa (premio, fecha, valor de boleta, etc.)
- Seleccionar un número disponible (al seleccionarlo, este debe quedar inmediatamente inhabilitado para otros)
- Llenar un formulario con sus datos: Nombre completo, número de celular y email (opcional)
- Realizar el pago mediante:
  - Pasarela de pagos (tarjeta de crédito)
  - Transferencia bancaria
  - PSE
  - Efectivo (opción manual que el admin marca como pagada)
- Una boleta solo participa en el sorteo si está *totalmente pagada*

*Reglas importantes del sistema:*
- Boleta sin pagar *no juega*
- El sistema debe enviar una *notificación por WhatsApp* al comprador 15 días antes del sorteo si aún no ha completado el pago
- Los números seleccionados pero no pagados deben volver a estar disponibles después de un tiempo límite (a definir)
- El sisteme debe notificar al comprador un plazo maximo de 5 dias para el pago de los numero separados para pagos en efectivo, despues de este plazo si no se ha pagado queda disponible nuevamente.
- A el comprador se le notificara el plazo en la pantalla de la compra
- Para los pago en efectivo al vendedor seleccionar que ya se hizo el pago, se generara una notificacion con la factura por whatsapp para el comprador, confirmando que se recibio su pago.

### Objetivos del proyecto:
- Reducir el trabajo manual de llenar talonarios
- Ampliar el alcance de las ventas más allá del círculo cercano
- Mejorar el control y seguimiento de pagos
- Ofrecer una experiencia más profesional y transparente tanto para organizadores como para compradores
- Mantener la sencillez y confianza característica de las rifas tradicionales

