# Guía de Ejecución del Siguiente Ciclo Ralph

**Fecha**: 2026-05-21  
**Estado**: Issues #001–#003 completados. Ready for #004.

---

## Resumen Actual

✅ **Completados**:
- #001 Scaffold proyecto (backend + frontend + DB)
- #002 Autenticación admin (JWT + bcrypt)
- #003 CRUD rifas (endpoints API básicos)

⏳ **Bloqueados**:
- #004 Vista pública rifa → Desbloqueado (depende de #001, ya completado)
- #005 Grilla números → Desbloqueado (depende de #004, listo cuando #004 termine)
- #006 Reserva números → Desbloqueado (depende de #005)
- #007+ → Dependen de cadena #005→#006

---

## Próximo Ticket: #004 (Vista Pública Rifa)

### Qué construir
Página pública sin autenticación donde compradores ven detalles de una rifa (nombre, premio, imagen, grilla de números).

### Criterios de aceptación (desde `issues/004-vista-publica-rifa.md`)
- [ ] GET `/public/raffles/{token}` retorna detalles de rifa (público, sin auth)
- [ ] Frontend renderiza página con nombre, descripción, imagen, fecha sorteo
- [ ] Si rifa no existe → 404
- [ ] Estilos con TailwindCSS (responsive)

### Dependencias resueltas
- ✅ Backend scaffold (FastAPI funcional)
- ✅ Frontend base (React + Vite + Tailwind)
- ✅ Database schema (admin + raffle tables)

---

## Cómo Ejecutar

### Opción 1: Usar Ralph CLI (recomendado)

```powershell
cd "c:\Users\<tu_usuario>\Desktop\uni 2\rifas-app"

# Ejecutar el script Ralph para el issue #004
./ralph/once.ps1 004
```

El script automáticamente:
1. Lee `issues/004-vista-publica-rifa.md`
2. Consulta los últimos 5 commits
3. Prepara un prompt ultra-contextualizado
4. Abre Claude Code (o imprime el prompt si no tienes `claude` CLI instalado)

### Opción 2: Manual (si Ralph CLI no funciona)

1. Copia el contenido de `issues/004-vista-publica-rifa.md`
2. Copia el último snippet del `handoffs.md` (Entrada 1)
3. Abre una nueva sesión de Claude Code con ambos textos
4. Pega el contexto y di: "Implement issue #004 según los criterios de aceptación"

---

## Auditoría Post-Ejecución (QA en el Seam)

Después de que Ralph termine issue #004 (todos los tests en verde), **haz lo siguiente como equipo senior**:

1. **Revisar commits**:
   ```powershell
   cd rifas-app
   git log --oneline -5  # Verify commit messages format: feat(#004): ...
   git show HEAD  # Review code changes
   ```

2. **Correr tests localmente**:
   ```powershell
   cd backend
   pytest  # Python required
   ```

   ```powershell
   cd ../frontend
   npm run build  # Verify frontend builds
   ```

3. **Revisar visualmente el código**:
   - Checkpoints: ¿hay acoplamientos nuevos?
   - ¿El endpoint `/public/raffles/{token}` está protegido contra SQL injection?
   - ¿El componente React es reutilizable (candidato para design system)?

4. **Rellenar la siguiente entrada en `handoffs.md`**:
   ```
   Fecha: YYYY-MM-DD
   Autor: Ralph (issue #004)
   Issues: #004
   Componentes: PublicRaffleView (frontend), GET /public/raffles/{token} (backend)
   Decisiones: 1) Token opaco para acceso sin auth. 2) Response include premio details.
   Pendientes: - Integrar imagen del premio (issue #010). - Performance en grilla (issue #005).
   Notas: Vista pública lista. Próximo: grilla números (issue #005, desbloqueado).
   ```

---

## Issues Desbloqueados Tras #004

✅ **#005 Grilla números** (depende #004 → completado)
✅ **#006 Reserva números** (depende #005 → se abrirá tras #005)
✅ **#007 Pago Wompi** (depende #006 → se abrirá tras #006)

---

## Checklist de Entregables Completos

- [x] `handoffs.md`: bitácora de transferencias con entrada realista
- [x] `architecture-checkpoint.md`: checkpoint mid-sprint con 3 propuestas paralelas
- [x] `README_PREPARE.md`: instrucciones locales para setup
- [x] **Este documento**: guía de ejecución del próximo ciclo
- [x] Historial de commits: disponible en `.git` (si localmente clonaste repo)
- [x] Issues listos para Ralph: #004 desbloqueado, criterios claros

---

## Tips para Mantener la Calidad

1. **Rota el revisor** en cada ciclo (QA en el Seam): evita fatiga de revisión
2. **Si 3+ PRs/commits rompen tests**, pausa y aplica `architecture-checkpoint.md` antes de continuar
3. **Mantén `handoffs.md` actualizado**: cada entrada debe tomar <5 min de lectura
4. **Archive old handoff entries**: después de 5 ciclos, mueve entradas a `docs/handoffs-archive.md`

Happy shipping! 🚀
