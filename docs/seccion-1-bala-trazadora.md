# Sección 1: La Bala Trazadora y el Enrutamiento de Skills

## Suposiciones iniciales del equipo
[cite_start]Al inicio del proyecto de la aplicación de rifas, el equipo asumió que el mayor desafío radicaba en diseñar una interfaz de usuario atractiva y un flujo CRUD convencional para que los administradores crearan eventos[cite: 72]. Pensábamos que el sistema se comportaría como un catálogo estático de comercio electrónico tradicional, donde los usuarios simplemente seleccionaban productos (boletas) y pagaban. No habíamos dimensionado el impacto de la concurrencia ni la necesidad de proteger la privacidad de los enlaces organizadores en un entorno multi-inquilino (*multi-tenant*).

## Uso de la skill grill-me
[cite_start]El uso de la skill de inteligencia artificial *grill-me* transformó por completo nuestra perspectiva del problema[cite: 73]. Al someter nuestras suposiciones a un cuestionamiento estricto, la herramienta nos obligó a profundizar en las reglas de negocio críticas: el manejo de estados de los números (disponible, reservado, pagado), el tiempo límite de expiración de las reservas para evitar el acaparamiento de boletas y la mitigación de condiciones de carrera (*race conditions*) cuando dos usuarios intentan comprar el mismo número en el mismo milisegundo.

## Árbol de diseño
[cite_start]El árbol de diseño actuó como nuestro mapa conceptual estratégico para refinar las ideas iniciales[cite: 74]. Nos permitió estructurar de forma jerárquica las decisiones de arquitectura, dividiendo el sistema en módulos aislados e independientes. Gracias a este enfoque, definimos que la lógica transaccional de reserva debía vivir en el backend mediante servicios encapsulados profundos, dejando al frontend únicamente con la responsabilidad de renderizar de manera reactiva el estado de la grilla de números.

## Riesgo técnico principal
[cite_start]Identificamos que el riesgo técnico más incierto y crítico del sistema era la **integración transaccional segura entre la selección de números en tiempo real y la persistencia en la base de datos**[cite: 75]. Si la lógica de reserva fallaba o era lenta, dos compradores podían pagar por el mismo número, destruyendo la confianza en la plataforma. Validar que el API de FastAPI procesara de manera óptima las solicitudes concurrentes y manejara de forma correcta las expiraciones *lazy* de boletas era nuestra máxima prioridad arquitectónica.

## Issue elegido como Bala Trazadora
[cite_start]Para mitigar este riesgo de inmediato, atacamos como "Bala Trazadora" el **Módulo de Reserva y Bloqueo Temporal de Números** (asociado al Issue de integración del backend con las reglas de negocio básicas)[cite: 76]. [cite_start]No nos enfocamos en hacer pantallas bonitas ni flujos complejos de administración; en su lugar, programamos un "disparo de punta a punta": una ruta REST funcional que recibiera un número de boleta, aplicara el bloqueo en la base de datos por un tiempo límite y retornara el token de confirmación[cite: 76].

## Feedback temprano obtenido
[cite_start]Al priorizar este issue como Bala Trazadora, el equipo obtuvo un aprendizaje invaluable de forma temprana[cite: 77]:
1. Descubrimos la necesidad de implementar esquemas de salida estrictos de Pydantic (`RifaResponse`) para ocultar las llaves primarias de la infraestructura base, dando origen a la estrategia de *Information Hiding* del proyecto.
2. Aprendimos a estructurar correctamente el árbol de directorios del backend para que las herramientas de automatización de pruebas (`pytest`) pudieran validar el ciclo de vida de una reserva de forma aislada.

## Conclusión de la sección
[cite_start]La validación temprana a través de la Bala Trazadora demostró que la arquitectura base elegida (FastAPI + SQLModel) era perfectamente viable y elástica para soportar las reglas de negocio del cliente[cite: 78]. [cite_start]Al resolver el núcleo más difícil y riesgoso al principio del ciclo de desarrollo, pudimos construir los módulos restantes (como el CRUD de rifas y las vistas de administración) sobre una base técnica sólida, estable y previamente testeada[cite: 78].