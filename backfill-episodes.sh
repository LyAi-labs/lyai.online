#!/bin/bash
# Backfill episodios desde 2026-05-03 a hoy
set -u
cd /opt/lyai/app/lyai.online

DATES=(2026-05-03 2026-05-04 2026-05-05 2026-05-06 2026-05-07
       2026-05-10 2026-05-11 2026-05-12 2026-05-14 2026-05-15
       2026-05-16 2026-05-17 2026-05-18 2026-05-19 2026-05-20)

TOTAL=${#DATES[@]}
i=0
for d in "${DATES[@]}"; do
    i=$((i+1))
    echo ""
    echo "================================================================"
    echo "[$i/$TOTAL] Generando episodio para $d ..."
    echo "================================================================"
    if python3 bridge-aurelius.py --date "$d" --no-git; then
        echo "  ✓ $d OK"
    else
        echo "  ✗ $d FAILED — continuando con siguientes"
    fi
done
echo ""
echo "================================================================"
echo "BACKFILL TERMINADO · $TOTAL fechas procesadas"
echo "================================================================"
grep -cE "Daily Dialogue · Episode" /var/www/lyai.online/index.html | xargs echo "Total episodios ahora en HTML:"
