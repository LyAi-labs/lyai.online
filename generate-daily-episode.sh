#!/bin/bash
# generate-daily-episode.sh — Pipeline diario Mirror Protocol en server
# Reemplaza el update-state.sh de WSL (que mezclaba 10+ tareas WSL-only).
# Esto solo hace lo mínimo: archive session del día + generar episode + inyectar.

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET_DATE="${1:-$(date -u -d 'yesterday' +%Y-%m-%d)}"

cd "$SCRIPT_DIR"

echo "→ Mirror Protocol pipeline · fecha: $TARGET_DATE"

# 1. Archive session del día (extrae JSONL → markdown)
python3 archive-session.py --date "$TARGET_DATE" --force --no-git

# 2. Generar episode + inyectar en /var/www/lyai.online/index.html
python3 bridge-aurelius.py --date "$TARGET_DATE" --no-git

echo "✅ Pipeline completado para $TARGET_DATE"
