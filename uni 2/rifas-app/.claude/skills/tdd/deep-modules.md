# Modulos Profundos

De "A Philosophy of Software Design":

**Modulo profundo** = interfaz pequena + mucha implementacion

```
┌─────────────────────┐
│  Interfaz pequena   │  ← Pocos metodos, parametros simples
├─────────────────────┤
│                     │
│                     │
│ Implementacion      │  ← Logica compleja oculta
│ profunda            │
│                     │
└─────────────────────┘
```

**Modulo superficial** = interfaz grande + poca implementacion (evitar)

```
┌─────────────────────────────────┐
│       Interfaz grande           │  ← Muchos metodos, parametros complejos
├─────────────────────────────────┤
│  Implementacion delgada         │  ← Solo pasa los datos
└─────────────────────────────────┘
```

Al disenar interfaces, preguntar:

- ¿Puedo reducir el numero de metodos?
- ¿Puedo simplificar los parametros?
- ¿Puedo ocultar mas complejidad adentro?
