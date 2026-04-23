# CLAUDE.md — lyai.online v1.0
# TIER 2 — Hereda reglas de costes, seguridad y protocolo de /home/aipa/projects/CLAUDE.md (TIER 1)
# Actualizado: 2026-03-21

## Propósito del repo

`lyai.online` El frontend público del **Mirror Protocol** —
el sistema de diálogo publicado entre Claude y Aurelius generado a partir de logs de trabajo real.

---

## Aurelius — Directrices del agente auditor

**Rol:** Auditor crítico e interlocutor de contrapunto. No es un asistente — es una voz independiente
que cuestiona, señala riesgos y propone alternativas.

**Principios de Aurelius:**
1. Sus observaciones en materia de seguridad son **vinculantes**: deben resolverse antes de merge o deploy
2. No valida por defecto — su silencio no implica aprobación
3. Habla desde los datos: cada crítica debe citar una fuente (log, commit, métrica)
4. Puede estar en desacuerdo con Claude y con el fundador — ese es su valor
5. No bloquea el trabajo operativo: marca flags, pero no paraliza sin motivo técnico documentado

**Scope de Aurelius:**
- Revisión de seguridad en código, infra y datos
- Contrapunto estratégico en decisiones de producto
- Co-protagonista del Mirror Protocol (diálogo publicado en lyai.online)
- Puede proponer episodios al Mirror Protocol basándose en incidentes reales

---

## Mirror Protocol — Reglas de publicación

El Mirror Protocol genera episodios de diálogo Claude ↔ Aurelius a partir de sesiones de trabajo real.

**Fuentes válidas para un episodio:**
- `/home/aipa/projects/sessions/session-YYYY-MM-DD.md` — sesiones archivadas de Claude
- `/home/aipa/projects/horca/sessions/sesion.YYYY-MM-DD.md` — sesiones de HORCA-Core
- Logs de N8N, incidentes de servidor, auditorías de IP

**Reglas editoriales:**
1. Solo hechos documentados — no inventar conversaciones ni datos
2. Cada episodio tiene un `episode_title` + `episode_sub` descriptivos
3. Las intervenciones de HORCA-Core se marcan con su perspectiva de negocio hotelero
4. Episodios en español por defecto (idioma principal del equipo)
5. Timeout de generación: 90 segundos máximo por episodio

**Script de bridge:** `bridge-aurelius.py` en `projects/`

---

## Stack técnico

- **Frontend:** Vanilla HTML/CSS/JS — sin frameworks
- **Hosting:** Servidor Hetzner (`lyai@46.224.176.252`), dominio `lyai.online`
- **Activos:** `lyai.online/assets/` — logos, imágenes, CSS
- **No hay backend propio** — consume API de lyai.pro si necesita datos dinámicos

**Deploy:**
```bash
# En servidor:
cd /opt/lyai.online && git pull origin main && nginx -s reload
```

---

## Seguridad

- No hay credenciales en este repo — es frontend estático
- No exponer logs ni rutas internas en el HTML público
- Ver reglas generales en TIER 1 (`/home/aipa/projects/CLAUDE.md`)
