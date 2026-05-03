## PRD padre

`issues/prd.md`

## Que construir

Flujo completo de autenticacion para admins: registro con email y contrasena, inicio de sesion con JWT, cierre de sesion, y proteccion de rutas en el frontend. Un admin puede crear su cuenta, iniciar sesion y acceder a un dashboard vacio protegido.

## Criterios de aceptacion

- [ ] `POST /auth/register` crea un admin con contrasena hasheada (bcrypt)
- [ ] `POST /auth/login` retorna access token JWT y refresh token con credenciales validas
- [ ] `POST /auth/login` retorna 401 con credenciales invalidas
- [ ] `POST /auth/refresh` retorna nuevo access token con refresh token valido
- [ ] Las rutas de admin en el backend rechazan peticiones sin token valido (401)
- [ ] El frontend tiene paginas de registro e inicio de sesion funcionales
- [ ] Tras login exitoso el usuario es redirigido al dashboard
- [ ] El boton de cerrar sesion elimina los tokens y redirige al login
- [ ] Las rutas protegidas del frontend redirigen al login si no hay sesion activa

## Bloqueado por

- Bloqueado por `issues/001-scaffold-proyecto.md`

## Historias de usuario abordadas

- Historia de usuario 1
- Historia de usuario 2
- Historia de usuario 3
