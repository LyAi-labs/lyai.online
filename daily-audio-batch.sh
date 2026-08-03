#!/bin/bash
# Mirror Protocol — genera el audio de los N episodios más antiguos sin audio.
# Free tier (3 modelos TTS con fallback). Idempotente. Cron: 1x/día.
set -u
COUNT="${1:-3}"
DIR=/opt/lyai/app/lyai.online
SRC=/var/www/lyai.online/index.html
AUDIO=/var/www/lyai.online/audio
mkdir -p "$AUDIO"

echo "=== $(date -u +%FT%TZ) daily-audio-batch (objetivo: $COUNT) ==="
done=0
for n in $(grep -oE 'id="ep-[0-9]{3}"' "$SRC" | grep -oE '[0-9]{3}' | sort -un); do
    [ "$done" -ge "$COUNT" ] && break
    [ -f "$AUDIO/ep-$n.mp3" ] && continue
    echo "--- generando ep-$n ---"
    if python3 "$DIR/make-episode-audio.py" "$((10#$n))"; then
        done=$((done + 1))
    else
        echo "ep-$n FALLO (rc=$?) — continúo"
    fi
done
echo "=== hecho: $done episodio(s) generado(s) ==="
