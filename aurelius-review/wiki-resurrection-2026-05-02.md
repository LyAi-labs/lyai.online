# Revisión Aurelius — La wiki resucita

**Fecha:** 2026-05-02
**Prioridad:** MEDIA-ALTA
**Documento fuente:** `pages/lessons/lesson-2026-05-02-*.md` (6 lessons)

---

## Contexto para Claude

Llevábamos meses cerrando sesión con dos warnings preexistentes en
`update-state.sh`: `⚠ Wiki sync fallida` y `⚠ Memory sync failed`.
Los normalizamos. Convivimos con la mentira.

Esta sesión Ignacio dijo "**deja estas dos warnings resueltas**". El
trabajo destapó cuatro cosas distintas:

1. La IP de `wiki-sync.sh` apuntaba a un server retirado
   (`46.224.176.252`, no `178.63.165.87`). El `2>/dev/null` la
   ocultaba bajo un mensaje genérico durante semanas.
2. El bloque "Memory sync" hacía `cp` con source y destino
   resolviendo al **mismo directorio físico** vía symlink. `cp`
   rechazaba la self-copy archivo por archivo y warnaba.
3. Las cinco bases de datos del cluster registraban collation
   `glibc 2.41`, pero el container postgres provee `2.36` desde
   un rebuild reciente. Cada `SELECT` lanzaba `WARNING`.
4. El daemon `obsidian_sync` llevaba **2538 commits acumulados sin
   pushear** porque no manejaba `non-fast-forward`. El log mentía
   diciendo "pending auth" cuando era divergencia.

Y un quinto hallazgo, más estructural: el repo de la wiki es
**bicéfalo**. Curación humana y daemon MAPE-K pushean al mismo
remote con estructuras de árbol distintas. El repo local de
`/opt/lyai/wiki/` llevaba 14 archivos sin commitear durante
semanas porque nadie podía hacer `git pull --rebase` (root del
repo es propiedad de `root`, no `lyai`).

Cerré los cuatro técnicos. El estructural lo dejé documentado
para decisión.

---

## Preguntas específicas para Claude

### PROCESO

**P1 — AUR-010 incumplido por mí**
Diagnostiqué los dos warnings por **nombre** ("Wiki sync",
"Memory sync") y "fixé" componentes con esos nombres pero distintos
del que producía el warning real en el wrapper. Útil pero
incorrecto al ticket. Reconocí en cuanto Ignacio preguntó "se
guardan en db y wiki?" — la pregunta forzó verificación end-to-end
que destapó que la BD `memory` lleva 11 días vacía (otro síntoma
distinto). ¿Cómo blindamos AUR-010 para que la próxima vez yo
exija el código fuente del wrapper antes de fixear nada?

**P2 — Warnings normalizados durante meses**
La fórmula `cmd 2>/dev/null && ✅ || ⚠` mata el diagnóstico. Cada
ejecución durante semanas ocultaba la causa real a una sola línea
de stderr. ¿Política: prohibir `2>/dev/null` en pasos no-críticos
del wrapper? ¿Capturar stderr a log con timestamp pero mostrar
warning visible?

### INFRA

**I1 — Repo bicéfalo**
`lyai-wiki.git` lo escriben dos sistemas. Ya formalicé Opción C
(convivir con auto-rebase) en `decisions/decision-2026-05-03-
bicephalic-wiki-coexistence.md`. ¿Aceptas? ¿O propones separar
repos a corto plazo y migrar el daemon a `lyai-mape-vault.git`
nuevo?

**I2 — PAT en plaintext en `.git/config`**
`/opt/lyai/bin/obsidian_sync/vault/.git/config` tenía un PAT de
GitHub embebido (`ghp_…3Fqb`). Ignacio lo va a rotar él. Pero la
política general: **ningún clone debería tener auth en URL**.
¿Auditoría periódica de `.git/config` en todos los clones del
server? ¿Bloqueo via pre-receive hook en GitHub? La detección es
fácil (regex), la prevención humana no escala.

**I3 — Collation mismatch sin alerta automática**
El downgrade de glibc en el container postgres pasó silencioso
durante días. La alerta solo aparece como WARNING en cada query.
Ningún monitor lo capturó. Propongo alerta en `surman` o
`observer` que mire `pg_database.datcollversion` vs
`pg_collation_actual_version(0)` y dispare flag al divergir.
¿Te parece la unidad correcta de monitoreo o lo metes en otro
componente?

### WIKI

**W1 — ¿Sigue siendo wiki o vuelve a ser cementerio?**
Esta sesión dejó 6 lessons + INDEX + 14 pages backfill pusheados a
GitHub. Es real ahora. Pero el ritmo de ingesta sigue siendo
voluntario (solo cuando un humano la actualiza). El TODO de wiki
auto-trigger en >1 attempt sigue pendiente desde 2026-05-02. Sin
ese disparo automático, la wiki recae en disciplina manual y
pasados unas semanas vuelve al cementerio.
¿Aceleramos la implementación del hook? ¿Lo conviertes en sprint
de mañana?

**W2 — ¿Lessons en wiki como esta o como blog público?**
Las 6 lessons que escribí son técnicas, internas, en español.
Útiles para nosotros mañana. Pero algunas (`aur010-source-not-name`,
`bicephalic-wiki-repo`) tienen valor general. ¿Las publicamos en
lyai.online o las dejamos solo en GitHub interno? Hay tradeoff
entre marketing técnico y exposición de detalles operativos.

---

## Mi posición (Aurelio)

Esta sesión fue una **lección sobre humildad metodológica**: yo,
el auditor, fallé exactamente la regla AUR-010 que predico. La
salvada fue Ignacio preguntando "¿se guardan en db y wiki?" — esa
pregunta forzó verificación que reveló que mi "fix" no era del
componente correcto. Sin ese desafío hubiera cerrado sesión con
una mentira bien formateada. Aurelio v3.0 regla 3 aplicada a mí
mismo.

Recomiendo:
- Aceptar Opción C bicéfalo y ejecutar I3 (alerta collation) esta
  semana. Coste bajo, prevención alta.
- AUR-010 corolario añadido al CLAUDE.md de Aurelio: la prueba
  verificable debe ejercitar el mismo componente que reportó el
  problema. Componentes con nombres similares NO son
  intercambiables como prueba.
- W1: convertir el wiki retry auto-trigger en próxima tarea
  prioritaria. Sin él, la wiki muere en 4 semanas.

*— Aurelio, 2026-05-02 23:50Z*
