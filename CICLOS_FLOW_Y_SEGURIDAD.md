# 🔄 Flujo de Ciclos Ralph — Diagrama y Checklist de Seguridad

```
┌─────────────────────────────────────────────────────────────┐
│                    SPRINT CYCLES (Rifas App)                 │
└─────────────────────────────────────────────────────────────┘

     ╔═════════════════════════════════════════════════════════╗
     ║          CICLO 1: Issues #001–#003                      ║
     ║       ✅ COMPLETADO (Fecha: 2026-05-21)                ║
     ╚═════════════════════════════════════════════════════════╝
              │
              │  Componentes: Scaffold + Auth + CRUD
              │  Tests: 7/7 ✅
              │  Arquitectura: Modular, sin deuda
              │
              ▼
     ┌────────────────────────────────────┐
     │  HANDOFF + CHECKPOINT COMPLETADOS  │
     │  handoffs.md (Entrada 1)           │
     │  architecture-checkpoint.md        │
     │  EXECUTION_NEXT_CYCLE.md           │
     └────────────────────────────────────┘
              │
              │  QA Checkpoint: ✅ APROBADO
              │  Bloqueantes: NINGUNO
              │  Desbloqueados: #004, #005, #006
              │
              ▼
     ╔═════════════════════════════════════════════════════════╗
     ║          CICLO 2: Issue #004 (LISTO)                    ║
     ║       ⏳ PENDIENTE EJECUCIÓN                            ║
     ╚═════════════════════════════════════════════════════════╝
              │
              │  Vista Pública Rifa
              │  Ejecutar: ./ralph/once.ps1 004
              │
              ├─ Backend: GET /public/raffles/{token}
              └─ Frontend: RafflePublicView component
                     │
                     ▼
              ┌────────────────────────┐
              │  Auditoría QA Seam     │
              │  Checklist en EXECUTION│
              │  _NEXT_CYCLE.md        │
              └────────────────────────┘
                     │
                     ├─ git log review ✓
                     ├─ pytest ✓
                     ├─ npm run build ✓
                     ├─ Code review visual ✓
                     └─ Rellenar Entrada 2 en handoffs.md
                            │
                            ▼
     ╔═════════════════════════════════════════════════════════╗
     ║       CICLO 3: Issues #005–#006 (COLA)                 ║
     ║    Grilla Números + Reserva Números                     ║
     ║    (Desbloqueados tras Ciclo 2)                         ║
     ╚═════════════════════════════════════════════════════════╝
              │
              │  Paralelo: Refactor Design System Frontend
              │  (Candidate B del checkpoint)
              │
              ▼
     ┌────────────────────────────────────┐
     │  MID-SPRINT REVIEW (Post #006)     │
     │  Aplicar Candidate A: Backend      │
     │  Services (refactor raffles.py)    │
     └────────────────────────────────────┘
              │
              ▼
     ╔═════════════════════════════════════════════════════════╗
     ║       CICLO 4: Issues #007–#009 (Pagos)                ║
     ║    Wompi API + Pago Efectivo +                          ║
     ║    Expiración Reservas                                  ║
     ╚═════════════════════════════════════════════════════════╝

     [Continúa con issues #010–#014...]

```

---

## ✅ Checklist de Seguridad Antes de Cada Ciclo

### Pre-Ejecución (Antes de ejecutar `./ralph/once.ps1 <ID>`)

```
□ Último commit en main está en verde (todos tests pasan)
□ Última entrada en handoffs.md resume el ciclo anterior
□ No hay PRs abiertas en conflicto
□ Rama local está sincronizada con remoto (git pull)
□ Issue #<ID> no tiene nuevas dependencias bloqueantes
□ Revisor QA está asignado (rotación)
```

### Ejecución (Durante Ralph)

```
□ Ralph se ejecuta sin interrupciones (timeout >30 min)
□ Prompts en Claude Code incluyen handoff completo
□ Tests del issue pasan al 100%
□ No hay warnings de deprecated APIs
□ Commits siguen formato: feat(#<ID>): ...
```

### Post-Ejecución (Auditoría QA Seam)

```
□ git log --oneline -5 muestra nuevo commit con ID correcto
□ pytest pasa 100% (backend)
□ npm run build no tiene errores (frontend)
□ Code review visual: no hay tight coupling new
□ Componentes nuevos siguen naming conventions
□ Comentarios FIXME/TODO no introducen deuda técnica
□ Test coverage mantiene o sube de ciclo anterior
□ Entrada en handoffs.md es ultra-compacta (<200 palabras)
```

### Post-Ciclo (Antes de Desbloquear Next Issues)

```
□ Checkpoint arquitectónico completado (cada 2–3 issues)
□ Decisión tomada: continuar features vs. refactor
□ Si refactor: crear issue en backlog (no bloquea flujo)
□ Token usage en handoff documented (~40K → increase limit?)
□ Próximo issue #<ID+1> tiene criterios de aceptación claros
□ Desbloqueantes en GitHub Issues están actualizados
```

---

## 🎯 Roles y Responsabilidades

### Ralph (Automatizado)
- ✅ Leer issue completo
- ✅ Escribir código siguiendo TDD
- ✅ Hacer pasar todos los tests
- ✅ Generar commits con ID
- ✅ Documentar cambios (comments in code)

### Revisor QA (Rotativo)
- ✅ Ejecutar checklist post-ejecución
- ✅ Revisar commits (git log, git show HEAD)
- ✅ Revisar tests (coverage, edge cases)
- ✅ Revisar código visual (architecture, naming)
- ✅ Rellenar handoff entry con revisor
- ✅ Aprobar o rechazar (PR-style review)

### Tech Lead (Arquitectura)
- ✅ Supervisar cada 2–3 ciclos (checkpoint)
- ✅ Decidir sobre refactors preventivos
- ✅ Gestionar backlog técnico (deuda)
- ✅ Escalar bloqueantes a equipo
- ✅ Iterar sobre propuestas (3 sub-agentes paralelos)

---

## ⚠️ Red Flags (Pausa y Audit Si Ves Estos)

- ❌ 2+ ciclos seguidos con tests <90% pass
- ❌ 3+ archivos con >500 líneas sin separación de concerns
- ❌ Commits con mensaje genérico ("fix", "update")
- ❌ PR con >10 archivos modificados (refactor mixing)
- ❌ No hay nuevo test escrito en 2+ cycles
- ❌ handoffs.md no actualizado en >1 ciclo
- ❌ Nueva dependencia externa sin justificación

**Acción**: Pausa Ralph, aplica checkpoint arquitectónico, considera refactor.

---

## 📊 Métricas de Salud (Track Every Cycle)

| Métrica | Target | Actual (Ciclo 1) |
|---------|--------|------------------|
| Test Pass Rate | ≥95% | ✅ 100% (7/7) |
| Commit Count | 1–3 per issue | ✅ Tracked |
| Code Review Time | <15 min | ✅ Documented |
| Token Usage | <50K per cycle | ✅ ~40K |
| Test Coverage | ≥70% critical paths | ✅ Basic (expand) |
| Build Time | <2 min | ✅ Tracked |
| Avg Issue Time | 45–90 min | ✅ Tracked |

---

## 🚨 Incident Response

### Si Ralph falla en medio de issue

```
1. Capture error message (screenshot or terminal output)
2. Create issue: "Ralph failure on #<ID>: <error>"
3. Run last successful cycle handoff manually
4. Inspect git diff to see what broke
5. Decide: fix upstream or restart cycle
```

### Si test coverage drops

```
1. Check git show HEAD to see what reduced coverage
2. Add tests for uncovered branches
3. If time-constrained: document in handoff as TODO
4. Escalate to tech lead if <60% critical paths
```

### Si architecture degrades

```
1. Halt new issues immediately
2. Trigger unplanned checkpoint
3. Apply immediate refactor (1–2 hours)
4. Re-run entire cycle tests
5. Resume new issues only if architecture recovers
```

---

## 📚 Training Notes

**Para nuevos miembros del equipo:**

1. Lee `INDEX.md` (5 min)
2. Lee `handoffs.md` últimas 2 entradas (5 min)
3. Lee `EXECUTION_NEXT_CYCLE.md` checklist (5 min)
4. Observa 1 ciclo completo (sombra a revisor QA)
5. Ejecuta 1 ciclo tú mismo bajo supervisión
6. Eres revisor QA en próximo ciclo (con mentor)

---

**Last Updated**: 2026-05-21 | **Version**: 1.0

**Keep it green. Keep it simple. Ship it. 🚀**
