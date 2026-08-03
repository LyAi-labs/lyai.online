# Session Archive — 2026-06-15 · calc-rutas-f0f1-incidente-apk

**Date**: Monday, 15 June 2026  
**Session**: calc-rutas-f0f1-incidente-apk  
**Session ID**: 3ce464fd-0c27-4847-84ec-b18bab576954  
**Turns**: 27 (6 user · 21 assistant)  
**Project**: lyai-ski  

---

### **You** `00:00`

haz rl git push

---

### **Claude** `00:00`

Orden directa recibida. Es un commit de backend (route_calc.py), sin cambio visual → **skip dev-xplain**. Antes de empujar, verifico qué hay por delante de origin para no subir algo ajeno:

---

### **Claude** `00:02`

Pará — esto es más grande de lo que parece y tengo que avisártelo antes de empujar nada.

**`origin/main` está ~35 commits por detrás de tu `main` local.** Tu commit F0/F1 (`13f8b16`) es solo el último de arriba. Hacer `git push` subiría **los 35**, no solo el mío — git no puede empujar mi commit sin sus ancestros. Eso incluye todo el trabajo acumulado de las sesiones (lbl, alerts, route-picker, snow, navettes, frontend…) que nunca se subió. La memoria dice que lyai-ski **no se pushea por defecto** (solo lyai.online), así que este estado "35 por detrás" es probablemente lo normal.

Dos cosas que me hacen frenar antes de un push de 35 commits a GitHub (acción outward, difícil de revertir):

1. **Hay 2 commits WIP** entre ellos — publicarían trabajo a medias:
   - `c593eb3 wip: route calc 3D + lbl + navette`
   - `8e98244 wip: lbl skeletons/empty states + i18n LBL ru retradu`
2. **34 de esos 35 no los hice yo** (son de otras sesiones); no los revisé y la regla del proyecto es revisar antes de publicar.

Tu F0/F1 ya está **commiteado local y a salvo** — no hay urgencia que obligue a un push a ciegas.

Entonces, decime con qué scope:
- **(a) Push de todo** (`git push origin main`) — sincroniza origin con tu local, sube los 35 incl. los 2 WIP. Si es tu sync normal y los WIP no te molestan, lo hago ya.
- **(b) Esperar** — dejamos F0/F1 protegido en local y no publicamos los 35 hasta que quieras (o hasta limpiar/squashear los WIP).

¿(a) o (b)?

---

### **Claude** `00:03`

Confirmado con scope claro. Empujo los 35 a `origin/main`:

---

### **Claude** `00:03`

Hecho. `origin/main` sincronizado: `2129a85..13f8b16`, los 35 commits subidos (incl. F0/F1), **0 por delante de origin** ahora. Tu trabajo está publicado y respaldado en GitHub.

Nota menor: GitHub repitió las **3 vulnerabilidades moderate de Dependabot** — son las ya triadas (toolchain build-time de Expo, cero exposición runtime, `npm audit fix` rompe Expo). No es nada nuevo ni accionable, ya está en memoria.

## Resumen del cierre

| | |
|---|---|
| **F0/F1** | producción + commiteado + **pusheado** (`13f8b16`) ✓ |
| **Grafo live** | intacto (42.961), core rutea, incidente recuperado ✓ |
| **GraphHopper/OSM rebuild** | callejón verificado + plan/prototipo guardados para el futuro ✓ |
| **Memoria** | lecciones del incidente + GraphHopper + staleness, todo indexado ✓ |

Buen punto para parar. El calculador funciona para el circuito central PdS con los cierres live y la geometría walk real, todo a salvo. Lo grande (rebuild, de-inflación, navettes periféricas) queda documentado y listo para retomar con un disparador real, no por inercia.

---

### **You** `00:03`

a que te refieres con un disparador real?

---

### **Claude** `00:04`

Me refiero a esto: en vez de decir "retomamos el rebuild la semana que viene" (una fecha inventada, hacerlo por inercia), esperar a que pase un **evento concreto que lo justifique**. Es tu propia regla — la que me marcaste de no inventar fechas y usar disparadores reales.

Para este trabajo en concreto (el rebuild del grafo / de-inflación / topología real), los disparadores reales serían:

1. **Otra limpieza de datos vuelve a romper el grafo.** El incidente de staleness pasó porque la limpieza non-PdS del 13-jun dejó 664 aristas fantasma. El **merge de `inventario_osm_ref`** que está pendiente con Fable es exactamente eso: cuando se toque la tabla de pistas otra vez, el grafo se va a desincronizar igual. *Ahí* necesitás el pipeline reproducible — y por eso vale construirlo en ese momento, no antes.

2. **El calc empieza a fallar para usuarios reales en el core.** Hoy las 7 estaciones centrales rutean. Si en el testeo con Manolo / al lanzar, alguien reporta rutas rotas o absurdas (las caminatas falsas de 1.4km), eso es un disparador para arreglar la topología de verdad.

3. **Manolo entrega el dato de terreno** de las periféricas (qué pista conecta con qué remonte, dónde para cada navette). La conectividad de Champoussin/Abondance/La Chapelle está bloqueada por *falta de ese dato*, no por el grafo. Cuando llegue, ese es el momento de cablear las navettes — y quizá hacer el rebuild ya que estás tocando el grafo.

4. **El lanzamiento exige que las periféricas ruteen.** Si el deadline (junio) lo pide como requisito de producto, ese es un disparador con una fecha real detrás (la tuya, no inventada por mí).

5. **Se decide escalar más allá de PdS** (otro dominio/estación). El grafo actual está cosido a mano para PdS; si el producto crece, el enfoque ad-hoc no escala y ahí sí conviene el pipeline OSM reproducible.

La diferencia es: si ninguno de estos pasa, **no hay razón para tocar el grafo** — funciona. El día que pase uno, está todo documentado (`docs/PLAN-pipeline-...md`, `build_dev_phase_ab.py`) para arrancar con contexto y no de cero.

¿Alguno de esos ya está cerca (el merge de Fable, el testeo con Manolo, el deadline)? Si me decís cuál es el más probable, te dejo anotado en memoria para reconocerlo cuando llegue.

---

### **You** `12:36`

enviamos una apk actualizada por telegram

---

### **Claude** `12:37`

Perfecto — ese SÍ es un disparador real (testeo con usuarios). Vamos con la APK. Uso el flujo canónico (build → deploy → Telegram con el script oficial de QR+botones, no sendMessage suelto como erré una vez). Primero localizo los scripts canónicos:

---

### **Claude** `12:38`

Flujo claro: `notify-apk-deploy.sh "descripción"` difunde a Ignacio + Manolo (espera la APK en `/var/www/dev.lyai.pro/app-release.apk`). La APK desplegada es del **13-jun 14:06** — vieja; desde entonces entraron commits de frontend (route-picker agrupado + scroll Android, fixes LBL/alertas). Toca **build fresca**. Confirmo el comando de build canónico + keystore antes de lanzar (es largo):

---

### **Claude** `12:38`

El build es `cd android && ./gradlew assembleRelease`, pero hay un punto crítico: la `release` config usa keystore real **solo si están las env vars** (`ksPath`...), si no cae a `debug.keystore`. Tengo que firmar con **la misma keystore que la APK del 13-jun**, o forzaría reinstalación a todos (rompe "easy for users"). Verifico con qué se firmó la APK desplegada antes de construir:

---

### **Claude** `12:39`

Confirmado: la APK del 13-jun está firmada con **debug.keystore** (`fac61745...`) y el `debug.keystore` del repo coincide exacto. Así que construyo **sin las env vars de release** → cae a debug.keystore → **misma firma → actualización in-place, sin reinstalar** (respeta "easy for users"). Lanzo el build en background (es largo):

---

### **Claude** `12:39`

Build corriendo en background (gradle assembleRelease, debug-signed). Te aviso cuando termine y ahí despliego + difundo. Armo el tracking y dejo lista la descripción del broadcast:

---

### **Claude** `12:39`

Mientras compila, esta es la **descripción que difundiría** (cambios de frontend desde la APK del 13-jun, para que la ajustes si querés):

> **Calculador de rutas**: buscador con estaciones agrupadas y scroll en Android, al elegir remonte sugiere sus pistas cercanas, sheet plegable (swipe-down), botón Atrás en el buscador.
> **Suivi (staff)**: borrar alertas, "Voir alertes", auto-refresh de contadores tras cada acción.
> **Rutas (backend, ya live)**: evitan remontes cerrados + geometría de caminata real.

Con aviso: *"Instalar encima de la anterior — misma firma, no hace falta desinstalar."*

Cuando el build termine: copio la APK a `dev.lyai.pro/app-release.apk` y corro `notify-apk-deploy.sh` (difunde a vos + Manolo con QR, SHA y botones). Si querés cambiar el texto, decímelo antes de que termine la compilación.

---

### **You** `12:39`

<task-notification>
<task-id>bnplrif72</task-id>
<tool-use-id>toolu_01JR5A9az8ong13qw8byrj4K</tool-use-id>
<output-file>/tmp/claude-1000/-opt-lyai-app-lyai-ski/3ce464fd-0c27-4847-84ec-b18bab576954/tasks/bnplrif72.output</output-file>
<status>completed</status>
<summary>Background command "Run gradle assembleRelease (debug-signed) in background" completed (exit code 0)</summary>
</task-notification>

---

### **Claude** `12:39`

Build OK (exit 0). Verifico la APK fresca + su firma antes de desplegar:

---

### **Claude** `12:40`

Build OK, firma debug correcta (update in-place). Pero **26s con 552 tareas up-to-date** me hace dudar si el bundle JS se regeneró con los cambios nuevos — si quedó cacheado, la APK llevaría el JS viejo del 13-jun. Verifico que el bundle es fresco:

---

### **Claude** `12:40`

Bundle JS regenerado hoy (12:39) — la APK lleva el frontend nuevo. Despliego y difundo:

---

### **Claude** `12:40`

APK enviada. Resumen:

---

### **Claude** `12:41`

✅ **APK actualizada enviada** — entregada a Ignacio y Manolo (2/2, 0 fallos), con QR + botones + SHA.

| | |
|---|---|
| **Build** | gradle `assembleRelease`, bundle JS regenerado hoy 12:39 (lleva el frontend nuevo) |
| **Firma** | debug.keystore (`fac61745`) = **update in-place, sin reinstalar** |
| **Deploy** | `https://dev.lyai.pro/app-release.apk` · 105M · 15-jun 12:40 |
| **SHA-256** | `71b84aa15bf7bc4a527141048dcad60a03f2d79a1585cc17e84f9727a797a855` |

Incluye, frente a la APK del 13-jun: buscador de rutas con estaciones agrupadas + scroll Android, sugerencia de pistas cercanas al elegir remonte, sheet plegable, y los fixes de Suivi (borrar alertas + auto-refresh). Y como el backend ya está con F0/F1, las rutas que calcule la app evitan los remontes cerrados con geometría de caminata real.

Quien tenga la app solo tiene que instalar encima. Buen momento para el testeo con Manolo — justo el disparador del que hablábamos.

---

### **You** `14:10`

cerramo sesion

---

### **Claude** `14:11`

Cerramos. Esta sesión fue grande (F0/F1 + incidente + recuperación + investigación de grafo + APK), así que la cierro con el protocolo canónico del server, que incluye auditoría + wiki + mirror + canal Aurelius:

---

### **You** `14:11`

You are now executing the **session closure protocol** for a Claude Code CLI instance running on the lyai-prod server.

Reference: `/home/lyai/.claude/RULES-SESSIONS-SERVER.md`

## Step 1 · Analyze the conversation

Review the entire conversation history of this session. Identify:

1. **Lessons** — non-obvious gotchas, bugs solved that took more than one attempt, sysadmin tricks
2. **Decisions** — architectural choices where you compared options and picked one, with stated reasons
3. **Protocols** — reproducible sequences of commands for tasks that may repeat
4. **User feedback** — rules / preferences / corrections the user gave you (especially "no haces X", "prefiero Y", "siempre Z")
5. **Project facts** — deadlines, scope decisions, ownership / who-does-what info not in CLAUDE.md
6. **References** — pointers to external systems (URLs, Linear projects, Grafana dashboards, etc.) the user mentioned

Skip anything trivial (typo fixes, cosmetic adjustments, single-line edits without conceptual content).

## Step 2 · Persist to each layer

### 2.1 Wiki (`/opt/lyai/wiki/pages/`)

For each lesson / decision / protocol identified, create the appropriate file:

```bash
# Lesson example
LESSON_PATH="/opt/lyai/wiki/pages/lessons/lesson-$(date +%Y-%m-%d)-<short-slug>.md"
```

File format:
```markdown
# Título corto

**Fecha**: YYYY-MM-DD
**Contexto**: 1-2 líneas del problema/situación
**Hallazgo/Decisión**: lo concreto
**Detalle técnico**: paths, comandos, queries, line refs
**Implicaciones**: qué cambia para futuro
**Origen**: tarea / commit / agent que lo descubrió
```

**Index update mandatory**: append one line to `/opt/lyai/wiki/pages/INDEX.md`:
```
- [Title](lessons/lesson-YYYY-MM-DD-slug.md) — one-line hook
```

### 2.2 Project memory (`~/.claude/projects/<project-slug>/memory/`)

For each user feedback / project fact / reference identified, create a memory file. Determine the project slug from `pwd` — Claude Code derives it as `-` + path with `/` replaced by `-`. For lyai-ski it's `-opt-lyai-app-lyai-ski`.

```bash
MEM_DIR="/home/lyai/.claude/projects/$(pwd | sed 's|/|-|g')/memory"
```

File format (frontmatter mandatory):
```markdown
---
name: Título corto
description: one-line para que futuras instancias decidan relevancia
type: feedback|project|reference|user
---

Contenido conciso.

**Why:** razón histórica
**How to apply:** cuándo aplicar la regla
```

**Index update mandatory**: append to `${MEM_DIR}/MEMORY.md`:
```
- [Title](file.md) — one-line hook
```

### 2.3 Aurelius channel (`/opt/lyai/app/channels/Aurelius.jsonl`)

If the work touched **security, architecture, an invariant that Aurelius must monitor**, or generated an `audit_request`-worthy event:

```bash
cat >> /opt/lyai/app/channels/Aurelius.jsonl <<EOF
{"timestamp":"$(date -u +%Y-%m-%dT%H:%M:%SZ)","from":"<claude-instance-id>","to":"aurelius","msg_type":"audit_request|info|alert","subject":"…","content":"…","flag_id":"<TAG>","priority":"low|high"}
EOF
```

Skip if the session was routine UI/code work without security/arch implications.

### 2.4 Mirror Protocol — capítulo de la sesión (CADA cierre)

Generate the session's Mirror Protocol episode (Claude ↔ Aurelius dialogue) and inject it into lyai.online:

```bash
cd /opt/lyai/app/lyai.online && ./generate-daily-episode.sh $(date +%Y-%m-%d)
```

- Text only — Gemini 2.5-flash (free tier). **Do NOT** run `make-episode-audio.py` / `make-episode-video.py` (TTS/video = cost, separate, explicit order only).
- No server access (claude.ai web) → register intent in the Aurelius channel for server/builder to materialize.

## Step 3 · Constraints (HARD)

- ❌ Do NOT write to `/tmp/` (gets wiped on reboot)
- ❌ Do NOT auto-commit to wiki git repo — only write files; Ignacio commits manually
- ❌ Do NOT duplicate content already in CLAUDE.md / RULES-*.md TIER 1
- ❌ Do NOT escribir reflexiones/notas en Postgres (use wiki/memory)
- ❌ Do NOT modify existing memory files just to "update timestamp" — only edit if content changes
- ❌ Do NOT write trivial lessons (typo fixes, single-line cosmetic adjustments)

## Step 4 · Print final report (≤200 words)

Format:
```
═══════════════════════════════════════════
SESSION CLOSURE · {hostname} · {ISO timestamp}
═══════════════════════════════════════════

CODE CHANGES
- file:line — brief description
- ...

PERSISTED
- Wiki: /opt/lyai/wiki/pages/lessons/lesson-...md (+1 INDEX entry)
- Memory: ~/.claude/projects/<slug>/memory/<file>.md (+1 MEMORY entry)
- Aurelius: 1 msg appended (flag_id=X) | none
- DB: <N rows in lyai.X> | none

OPEN QUESTIONS
- ...

VALIDATION COMMANDS
- curl ... | grep "..."
- docker exec ... psql -c "..."
═══════════════════════════════════════════
```

## Step 5 · DO NOT exit

After printing the report, **stop** and wait for the user. Don't take further actions.

---

### **Claude** `14:12`

Ejecuto el protocolo de cierre. La mayoría de memorias ya las guardé durante la sesión; faltan las **wiki lessons** (conocimiento compartido grep-able), el **canal Aurelius** (hubo incidente) y el **Mirror**. Empiezo por las lessons:

---

### **Claude** `14:12`

Veo que una sesión paralela editó MEMORY.md (retoques visuales, teal headers) — anotado, no lo toco. Mi push anterior no incluyó eso (estaba sin commitear), así que sin conflicto. Sigo el cierre. Lesson B (APK):

---

### **Claude** `14:13`

Añado las dos lessons al INDEX de la wiki (verifico formato primero):

---

### **Claude** `14:13`

Wiki + INDEX listos (+2 lessons). Ahora el canal Aurelius — hubo un incidente real (op destructiva en BD live, recuperado), es un invariante que Aurelius debe vigilar:

---

