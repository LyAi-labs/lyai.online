#!/bin/bash
# generate-daily-episode.sh — Pipeline Mirror Protocol en server
# 2026-06-12: PER-SESIÓN. Un episodio por sesión (ventana Claude Code), no por día.
#   Uso (cierre de sesión): ./generate-daily-episode.sh <YYYY-MM-DD> <slug>
#   slug = nombre humano de la ventana (work-on-suiv, build-telegram, diagnose-chatel…)
#   La sesión que cierra se identifica por $CLAUDE_CODE_SESSION_ID (su JSONL).
#   Idempotente: re-cerrar la misma sesión REEMPLAZA su episodio (no duplica).
#   Sin slug/sid → modo legacy por-día (backfill manual).

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET_DATE="${1:-$(date -u +%Y-%m-%d)}"
SLUG="${2:-}"
SESSION_ID="${CLAUDE_CODE_SESSION_ID:-}"

cd "$SCRIPT_DIR"

if [ -n "$SLUG" ] && [ -n "$SESSION_ID" ]; then
  echo "→ Mirror Protocol · per-sesión · $TARGET_DATE · slug=$SLUG · sid=${SESSION_ID:0:8}"
  # 1. Archive SOLO esta sesión (su JSONL) → markdown
  python3 archive-session.py --date "$TARGET_DATE" --session-id "$SESSION_ID" --slug "$SLUG" --force --no-git
  # 2. Generar episode etiquetado (día · slug) + inyectar (reemplaza si ya existía)
  python3 bridge-aurelius.py --date "$TARGET_DATE" --slug "$SLUG" --no-git
else
  echo "→ Mirror Protocol · LEGACY por-día · $TARGET_DATE (sin slug/CLAUDE_CODE_SESSION_ID)"
  python3 archive-session.py --date "$TARGET_DATE" --force --no-git
  python3 bridge-aurelius.py --date "$TARGET_DATE" --no-git
fi

# Redacción de secretos antes de publicar/commitear (SEC-MIRROR-SECRETS-2026-06-25)
# El pipeline archiva JSONL→.md; sin esto, cualquier token tecleado en la sesión
# quedaría en claro en sessions/*.md (incidente 2026-06-25: 99 secretos en 18 ficheros).
sed -i -E '
 s/ghp_[A-Za-z0-9]{20,}/ghp_[REDACTED]/g;
 s/github_pat_[A-Za-z0-9_]{20,}/github_pat_[REDACTED]/g;
 s/gh[oprsu]_[A-Za-z0-9]{20,}/gh_[REDACTED]/g;
 s/(sk|pk)\.eyJ[A-Za-z0-9._-]{20,}/\1.[REDACTED-MAPBOX]/g;
 s/AKIA[0-9A-Z]{16}/[REDACTED-AWS]/g;
 s/AIza[0-9A-Za-z_-]{30,}/[REDACTED-GOOGLE]/g;
 s/sk-[A-Za-z0-9]{20,}/sk-[REDACTED]/g;
 s/xox[baprs]-[A-Za-z0-9-]{10,}/xox-[REDACTED]/g;
 # 2026-08-03 · DSN y contraseñas. El bloque de arriba solo cubría TOKENS con prefijo
 # reconocible; al ir a versionar sessions/ aparecieron 56 credenciales reales en 17 de
 # 121 ficheros: 30 DSN "postgresql://lyai:<pass>@" y varios "password=". La web publicada
 # estaba limpia (Gemini resume, no copia), pero los .md son la ENTRADA y se iban a GitHub.
 s#(postgres(ql)?://[^:/ ]+):[^@ ]+@#\1:[REDACTED-DSN]@#g;
 s#(password|passwd|PGPASSWORD|POSTGRES_PASSWORD)([[:space:]]*[:=][[:space:]]*)["'"'"']?[A-Za-z0-9!@#$%^&*_.-]{8,}["'"'"']?#\1\2[REDACTED]#gI;
 # 2026-08-03 (2ª tanda) · lo que el push protection de GitHub cazo y estas reglas NO:
 #   · sk-ant-…  el patron viejo era sk-[A-Za-z0-9]{20,} y el GUION de "sk-ant-" lo cortaba
 #   · gsk_…     Groq, sin patron ninguno
 #   · AQ.…      claves GCP del formato nuevo, sin prefijo AIza
 # Leccion: la lista de prefijos SIEMPRE va por detras. El push protection de GitHub es
 # la red de verdad; estas reglas solo evitan llegar hasta alli con el secreto en la mano.
 s/sk-ant-[A-Za-z0-9_-]{20,}/sk-ant-[REDACTED]/g;
 s/gsk_[A-Za-z0-9]{20,}/gsk_[REDACTED]/g;
 s/AQ\.[A-Za-z0-9_-]{20,}/AQ.[REDACTED-GCP]/g;
 s/(GOOGLE_API_KEY|GEMINI_API_KEY|GROQ_API_KEY|ANTHROPIC_API_KEY)([[:space:]]*[:=][[:space:]]*)["'"'"']?[A-Za-z0-9_-]{20,}["'"'"']?/\1\2[REDACTED]/gI
' sessions/*.md 2>/dev/null || true
echo "🔒 redacción de secretos aplicada a sessions/*.md"

# --- Sync-back al repo (2026-08-03) -------------------------------------------------
# POR QUÉ: bridge-aurelius.py escribe DIRECTAMENTE en /var/www/lyai.online/index.html.
# Durante meses eso significó que el fichero servido era el ORIGINAL y el repo se quedaba
# atrás: 2,29 MB servidos frente a 695 KB versionados, o sea 1,6 MB de episodios que solo
# existían en un disco. Este paso cierra el círculo.
#
# Es ADITIVO y no puede romper el pipeline: cuando llega aquí el episodio YA está publicado.
# Por eso todo va con `|| true` y el sitio nunca depende de que esto funcione.
LIVE_HTML="${LYAI_ONLINE_HTML:-/var/www/lyai.online/index.html}"
if [ -f "$LIVE_HTML" ] && [ -d "$SCRIPT_DIR/.git" ]; then
  if ! cmp -s "$LIVE_HTML" "$SCRIPT_DIR/index.html"; then
    cp "$LIVE_HTML" "$SCRIPT_DIR/index.html" 2>/dev/null || true
    git -C "$SCRIPT_DIR" add index.html 2>/dev/null || true
    git -C "$SCRIPT_DIR" commit -q -m "site: episodio del $TARGET_DATE (sync-back automatico)" 2>/dev/null || true
    if git -C "$SCRIPT_DIR" push -q origin HEAD 2>/dev/null; then
      echo "📦 index.html sincronizado al repo y pusheado"
    else
      echo "⚠️  index.html commiteado pero SIN push (el sitio no se ve afectado)"
    fi
  else
    echo "📦 index.html ya estaba en sync con el repo"
  fi
fi

echo "✅ Pipeline completado para $TARGET_DATE${SLUG:+ · $SLUG}"
