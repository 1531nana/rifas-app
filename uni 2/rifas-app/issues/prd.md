# PRD - Sistema de Gestion de Rifas Digital

*Cliente:* Organizador de Rifas Tradicionales
*Fecha:* Mayo 2026
*Estado:* Aprobado

---

## Enunciado del problema

Los organizadores de rifas tradicionales gestionan todo su proceso de venta de forma manual: llenan talonarios fisicos a mano, cobran exclusivamente en efectivo y solo pueden vender a personas de su circulo cercano. Esto limita drasticamente el alcance de ventas, genera trabajo operativo repetitivo, dificulta el seguimiento de pagos pendientes y ofrece una experiencia poco profesional tanto para el organizador como para los compradores.

---

## Solucion

Una aplicacion web multi-organizador que digitaliza el ciclo completo de una rifa: desde su creacion y publicacion, pasando por la seleccion y pago de numeros, hasta el registro del ganador. Los compradores acceden mediante un enlace publico sin necesidad de crear cuenta, pueden pagar con tarjeta de credito o PSE, y reciben notificaciones por WhatsApp. El organizador tiene un panel de control para gestionar sus rifas, ver compradores, confirmar pagos en efectivo y registrar el resultado del sorteo.

---

## Historias de usuario

### Admin / Vendedor

1. Como admin, quiero registrarme con email y contrasena, para tener acceso a mi panel de control.
2. Como admin, quiero iniciar sesion con mis credenciales, para gestionar mis rifas de forma segura.
3. Como admin, quiero cerrar sesion, para proteger mi cuenta en dispositivos compartidos.
4. Como admin, quiero crear una nueva rifa con nombre, tipo de loteria, cantidad de numeros, valor de boleta, descripcion del premio, fecha del sorteo e imagen opcional del premio, para publicarla y comenzar a vender.
5. Como admin, quiero que al crear una rifa se genere automaticamente un enlace publico con token opaco, para compartirlo con compradores potenciales por WhatsApp u otros medios.
6. Como admin, quiero ver la lista de todas mis rifas activas y finalizadas, para tener un panorama general de mi negocio.
7. Como admin, quiero ver el detalle de una rifa con estadisticas (total recaudado, porcentaje de numeros vendidos, cantidad de pagos pendientes), para tomar decisiones informadas.
8. Como admin, quiero ver en tiempo real que numeros estan vendidos, reservados y disponibles en cada rifa, para monitorear el estado de las ventas.
9. Como admin, quiero ver el listado completo de compradores de una rifa con nombre, celular, email, numero comprado y estado de pago, para hacer seguimiento.
10. Como admin, quiero editar la descripcion, imagen, fecha del sorteo y tipo de loteria de una rifa existente, para corregir errores o actualizar informacion.
11. Como admin, quiero que el sistema me impida cambiar el precio de boleta o la cantidad total de numeros si ya existe al menos una reserva activa, para no perjudicar a compradores que ya separaron numeros.
12. Como admin, quiero confirmar manualmente el pago en efectivo de un comprador, para que su boleta quede activa en el sorteo.
13. Como admin, quiero que al confirmar un pago en efectivo el sistema envie automaticamente una notificacion de confirmacion por WhatsApp al comprador, para que tenga su comprobante.
14. Como admin, quiero registrar el numero ganador del sorteo y cerrar la rifa, para finalizar el proceso.
15. Como admin, quiero que al registrar el ganador el sistema notifique automaticamente al comprador ganador por WhatsApp, para informarle que gano.
16. Como admin, quiero subir una imagen opcional del premio al crear o editar una rifa, para que los compradores vean visualmente que pueden ganar.
17. Como admin, quiero que el sistema envie automaticamente recordatorios por WhatsApp a compradores con pagos pendientes 15 dias antes del sorteo, para reducir boletas sin pagar.

### Comprador

18. Como comprador, quiero acceder a la rifa mediante un enlace publico sin necesidad de crear una cuenta, para participar de forma rapida y sencilla.
19. Como comprador, quiero ver la informacion completa de la rifa (nombre, premio, imagen del premio, fecha del sorteo, valor de boleta, tipo de loteria), para decidir si quiero participar.
20. Como comprador, quiero ver una grilla visual de todos los numeros con colores que indiquen su estado (verde=disponible, rojo=vendido, amarillo=reservado), para elegir mi numero facilmente.
21. Como comprador, quiero seleccionar un numero disponible y que este quede inmediatamente inhabilitado para otros compradores, para asegurar que nadie mas lo tome mientras completo mi compra.
22. Como comprador, quiero ver claramente el plazo que tengo para completar el pago antes de que mi numero quede liberado, para saber cuanto tiempo tengo.
23. Como comprador, quiero llenar un formulario con mi nombre completo, numero de celular y email opcional, para que el organizador tenga mis datos de contacto.
24. Como comprador, quiero pagar mi boleta con tarjeta de credito a traves de Wompi, para completar mi compra de forma segura y rapida.
25. Como comprador, quiero pagar mi boleta via PSE a traves de Wompi, para usar mi cuenta bancaria.
26. Como comprador, quiero seleccionar pago en efectivo y recibir las instrucciones para coordinar el pago con el organizador, para participar aunque no tenga tarjeta.
27. Como comprador, quiero que si pago en efectivo el sistema me muestre que tengo 5 dias para completar el pago, para saber mi plazo.
28. Como comprador, quiero recibir un comprobante de pago en efectivo por WhatsApp cuando el organizador confirme mi pago, para tener mi constancia.
29. Como comprador, quiero que si no he pagado 15 dias antes del sorteo el sistema me recuerde por WhatsApp, para no olvidar completar mi pago.
30. Como comprador, quiero recibir una notificacion por WhatsApp si gano el sorteo, para enterarme de inmediato.
31. Como comprador, quiero que si no completo el pago en el plazo establecido mi numero quede liberado automaticamente, para entender que perdi la reserva.

---

## Decisiones de implementacion

### Arquitectura general

- *Backend:* Python + FastAPI, API REST
- *Frontend:* React + Vite + TailwindCSS, SPA
- *Base de datos:* PostgreSQL
- *Despliegue:* Railway (backend + BD), Vercel (frontend)
- *Modelo:* Multi-organizador (cada admin gestiona sus propias rifas de forma aislada)

### Autenticacion

- Email + contrasena con hashing bcrypt
- JWT con access token de vida corta y refresh token
- Solo los admins se autentican; los compradores acceden sin cuenta mediante token de rifa

### Modulo de Rifas

- Entidades: Admin, Raffle, Number, Reservation, Buyer
- Cada rifa tiene un public_token unico (token opaco corto) generado al crear
- Estados de rifa: active, closed
- Estados de numero: calculados dinamicamente segun reservas activas — disponible, reservado, vendido
- Edicion restringida: precio y cantidad de numeros no editables si existe alguna reserva activa
- Imagen del premio almacenada en Cloudinary (campo opcional)
- Tipo de loteria: campo de texto libre

### Modulo de Reservas
- Al seleccionar un numero se crea un registro Reservation con status=pending y expires_at
- Timeout: 48 horas para pagos digitales, 5 dias para pagos en efectivo
- La expiracion se verifica de forma lazy al consultar disponibilidad y mediante un job periodico que libera reservas vencidas
- Un numero se considera disponible si no tiene ninguna reserva activa (no expirada) o pago completado

### Modulo de Pagos

- *Wompi* como pasarela para tarjeta de credito y PSE
- Wompi notifica el resultado del pago via webhook; el backend actualiza el estado de la reserva a paid
- *Efectivo:* el admin confirma manualmente desde su panel; el backend marca la reserva como paid y dispara notificacion WhatsApp
- La transferencia bancaria se trata como PSE (mismo flujo Wompi)
- Una boleta solo participa en el sorteo si tiene status=paid

### Modulo de Notificaciones

- *Meta Cloud API (WhatsApp Business)* para todos los mensajes salientes
- Mensajes implementados con templates aprobados por Meta:
  1. Confirmacion de pago en efectivo (con datos de la boleta)
  2. Recordatorio de pago pendiente (15 dias antes del sorteo)
  3. Notificacion al ganador
- El recordatorio de 15 dias se dispara mediante un job programado diario que evalua todas las rifas activas
- El plazo de pago para efectivo (5 dias) se muestra en pantalla al comprador en el momento de la compra

### Modulo de Archivos

- Cloudinary para almacenamiento de imagenes de premios
- Subida desde el backend; se almacena la URL publica en la BD
- Campo opcional: la rifa puede existir sin imagen

### Frontend - Vista publica del comprador

- Acceso via /r/{public_token} sin autenticacion
- Grilla numerada responsive con codigo de colores: verde (disponible), rojo (vendido/pagado), amarillo (reservado/pendiente)
- Modal de compra al seleccionar numero: formulario de datos + seleccion de metodo de pago
- Countdown o mensaje de plazo visible durante el proceso de pago

### Frontend - Panel del admin

- Rutas protegidas por JWT
- Dashboard con lista de rifas y metricas resumidas por rifa
- Vista detalle de rifa: grilla en tiempo real + lista de compradores + boton para registrar ganador
- Formulario de creacion/edicion de rifa
- Boton de confirmacion de pago en efectivo por comprador

---

## Decisiones de testing

### Filosofia de testing

Los tests deben verificar comportamiento observable a traves de interfaces publicas (endpoints de la API, acciones del usuario en el frontend), no detalles internos de implementacion. Un buen test sobrevive una refactorizacion interna sin cambios.

### Modulos a probar

*Modulo de Reservas* (prioridad alta)
- Un numero disponible puede ser reservado
- Un numero reservado no puede ser tomado por otro comprador simultaneamente
- Una reserva expirada libera el numero correctamente
- El timeout correcto se asigna segun metodo de pago (48h vs 5 dias)

*Modulo de Pagos* (prioridad alta)
- El webhook de Wompi con estado approved marca la reserva como pagada
- El webhook de Wompi con estado declined libera la reserva
- La confirmacion manual de efectivo por el admin marca la reserva como pagada
- Una boleta con pago pendiente no aparece como participante del sorteo

*Modulo de Notificaciones* (prioridad media)
- El job de recordatorio solo notifica compradores con reservas activas sin pagar dentro del rango de 15 dias
- La confirmacion de efectivo dispara exactamente una notificacion WhatsApp al comprador correcto
- La notificacion de ganador se envia al comprador del numero ganador

*Modulo de Rifas* (prioridad media)
- No se puede cambiar precio ni cantidad de numeros con reservas activas
- El enlace publico generado es unico y opaco
- Solo el admin dueno puede editar o cerrar su rifa

---

## Fuera de alcance

- Generador automatico de numeros ganadores (el sorteo siempre es fisico y manual)
- Notificaciones por email (solo WhatsApp)
- Aplicacion movil nativa
- Sistema de planes o monetizacion de la plataforma
- Reportes avanzados o exportacion de datos
- Soporte para multiples ganadores por rifa
- Reventa o transferencia de boletas entre compradores
- Integracion con loterias oficiales para validacion automatica de resultados
- Confirmacion automatica de transferencias bancarias (se usan como PSE via Wompi)

---

## Notas adicionales

- El numero de telefono del comprador es el identificador clave para las notificaciones WhatsApp; debe validarse que tenga formato correcto al momento del registro
- Los templates de WhatsApp deben ser aprobados por Meta antes del lanzamiento; esto puede tomar varios dias habiles
- Wompi requiere cuenta verificada y configuracion de webhooks en su dashboard antes de poder procesar pagos reales
- La imagen del premio en Cloudinary debe tener un tamano maximo recomendado para no impactar el tiempo de carga en movil