# 🎟️ QUICK REFERENCE CARD — Ralph Loop Rifas App

**Imprímelo y tenlo a mano durante ejecución de ciclos**

---

## 📋 ANTES DE EJECUTAR RALPH

```
□ Último commit está en verde (tests pasan)
□ Git updated: git pull
□ No hay PRs en conflicto
□ Issue #<ID> está desbloqueado
□ Revisor QA asignado
```

---

## 🚀 EJECUTAR CICLO

```powershell
cd "c:\Users\<tu_usuario>\Desktop\uni 2\rifas-app"

# Opción 1: Usar Ralph script (recomendado)
./ralph/once.ps1 <ISSUE_ID>

# Opción 2: Manual (si el script falla)
# 1. Copia contenido de issues/<ISSUE_ID>-*.md
# 2. Copia última entrada de handoffs.md
# 3. Pega en Claude Code
# 4. Di: "Implement issue #<ID> según criterios"
```

---

## ✅ DESPUÉS DE RALPH (Auditoría QA)

```
□ git log --oneline -5  (verifica commit ID)
□ pytest  (backend tests)
□ npm run build  (frontend build)
□ git show HEAD  (revisa cambios)
□ Code visual review:
  □ Sin tight coupling nuevo?
  □ Naming conventions OK?
  □ Sin FIXME/TODO sin documentar?
□ Rellenar Entrada N en handoffs.md
```

---

## 📊 MÉTRICAS CRÍTICAS

| Métrica | Target | Check |
|---------|--------|-------|
| Test Pass | ≥95% | ✓ pytest |
| Build | Sin errores | ✓ npm build |
| Coverage | ≥70% critical | ✓ pytest --cov |
| Commits | 1–3 per issue | ✓ git log |

---

## 🚨 RED FLAGS (Pausa si ves estos)

- ❌ Tests <90% pass → fix before next cycle
- ❌ Commits sin ID (#<NUM>) → revert y redo
- ❌ Archivo >500 líneas sin split → refactor before merge
- ❌ handoffs.md no updated → update now
- ❌ New dependency sin justificación → escalate
- ❌ Nueva deuda técnica acumulada → trigger checkpoint

---

## 📁 ARCHIVOS KEY

| Archivo | Cuándo | Qué |
|---------|--------|-----|
| `INDEX.md` | Cualquier hora | Índice principal |
| `handoffs.md` | Antes de empezar | Contexto último ciclo |
| `EXECUTION_NEXT_CYCLE.md` | Antes de Ralph | Criterios issue actual |
| `architecture-checkpoint.md` | Post #2, #4, #6 | Auditoría arquitectura |
| `CICLOS_FLOW_Y_SEGURIDAD.md` | Consulta | Checklists + red flags |

---

## 🔄 CICLO TÍPICO (~120 min)

```
10 min   → Leer handoff + issue criterios
5 min    → Asignar revisor QA
60–70 min → Ralph ejecución (tests en loop)
15 min   → Auditoría QA (git log, tests, review)
5 min    → Rellenar handoff Entrada N
5 min    → Desbloquear siguiente issue #<ID+1>
```

---

## 📞 CONTACTOS

- **Bloqueante técnico**: Abre issue con tag `blocking`
- **Refactor needed**: Escalate a tech lead → crear en backlog
- **Tests failing**: Revisor QA investiga → documenta en handoff

---

## 🎯 PRÓXIMOS CICLOS

```
Ciclo 1: ✅ #001–#003 completados
Ciclo 2: ⏳ #004 LISTO AHORA
Ciclo 3: #005–#006 (desbloqueados post #004)
Ciclo 4: #007–#009 (Wompi, efectivo, expiración)
Ciclo 5: #010–#012 (imágenes, WhatsApp, recordatorios)
Ciclo 6: #013–#014 (ganador, dashboard)
```

---

**Última actualización**: 2026-05-21  
**Proyecto**: Rifas App  
**Estado**: ✅ LISTO
