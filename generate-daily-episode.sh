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

echo "✅ Pipeline completado para $TARGET_DATE${SLUG:+ · $SLUG}"
