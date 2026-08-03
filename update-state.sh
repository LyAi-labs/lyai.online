#!/bin/bash
# update-state.sh — Auto-updates STATE.json and SESSION_LOG.md
# Run this at the end of each work session to persist state for agents

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

STATE_FILE="$SCRIPT_DIR/STATE.json"
SESSION_LOG="$SCRIPT_DIR/SESSION_LOG.md"
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
HOSTNAME=$(hostname)
USER_NAME=$(whoami)

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}🔄 Updating infrastructure state...${NC}"

# ──────────────────────────────────────────────────────────
# 1. Get git status for both repos
# ──────────────────────────────────────────────────────────
get_git_status() {
    local repo_path=$1
    if [ -d "$repo_path/.git" ]; then
        cd "$repo_path"
        local branch=$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo "unknown")
        local status=$(git status --porcelain 2>/dev/null | wc -l)
        if [ "$status" -eq 0 ]; then
            echo "clean"
        else
            echo "dirty"
        fi
        cd - > /dev/null
    else
        echo "not_found"
    fi
}

# ──────────────────────────────────────────────────────────
# 2. Check docker services health
# ──────────────────────────────────────────────────────────
get_docker_status() {
    if command -v docker &> /dev/null; then
        if docker compose -f "$SCRIPT_DIR/docker-compose.master.yml" ps 2>/dev/null | grep -q "Up"; then
            echo "running"
        else
            echo "stopped"
        fi
    else
        echo "docker_not_installed"
    fi
}

# ──────────────────────────────────────────────────────────
# 3. Update STATE.json with current status
# ──────────────────────────────────────────────────────────
echo -e "${YELLOW}  → Scanning repositories...${NC}"

LYAI_STATUS=$(get_git_status "$SCRIPT_DIR/lyai-core")
CERVELL_STATUS=$(get_git_status "$SCRIPT_DIR/cervell.lyai.pro")
HORCA_STATUS=$(get_git_status "$SCRIPT_DIR/horca")
DOCKER_STATUS=$(get_docker_status)

# Update JSON (simple sed replacements for key fields)
sed -i "s/\"last_updated\": \"[^\"]*\"/\"last_updated\": \"$TIMESTAMP\"/g" "$STATE_FILE"
sed -i "s/\"last_sync\": \"[^\"]*\" *\(.*mesa\)/\"last_sync\": \"$TIMESTAMP\" \1/g" "$STATE_FILE"

echo -e "${YELLOW}  → Docker status: ${GREEN}$DOCKER_STATUS${NC}"
echo -e "${YELLOW}  → lyai-core: ${GREEN}$LYAI_STATUS${NC}"
echo -e "${YELLOW}  → cervell.lyai.pro: ${GREEN}$CERVELL_STATUS${NC}"
echo -e "${YELLOW}  → horca: ${GREEN}$HORCA_STATUS${NC}"

# ──────────────────────────────────────────────────────────
# 4. Append to SESSION_LOG.md with new entry
# ──────────────────────────────────────────────────────────
echo -e "${YELLOW}  → Recording session...${NC}"

cat >> "$SESSION_LOG" << EOF

### 📌 Auto-Update: $TIMESTAMP
- **Machine**: $HOSTNAME ($USER_NAME)
- **Docker Status**: $DOCKER_STATUS
- **lyai-core**: $LYAI_STATUS
- **cervell.lyai.pro**: $CERVELL_STATUS
- **horca**: $HORCA_STATUS
- **Files Updated**: STATE.json, SESSION_LOG.md

EOF

# ──────────────────────────────────────────────────────────
# 5. Git commit the updated state files
# ──────────────────────────────────────────────────────────
echo -e "${YELLOW}  → Archiving session...${NC}"
python3 "$SCRIPT_DIR/archive-session.py" --force --no-git 2>/dev/null && echo -e "${GREEN}  ✅ Session archived${NC}" || echo -e "${YELLOW}  ⚠ Session archive failed${NC}"

# Mirror Protocol — generar episodio del dia + auto-commit+push + auto-deploy
# v3 2026-05-03: bridge-aurelius.py auto-commit es poco fiable (traga errores en pipe),
# por eso el wrapper se encarga de commit+push tras la inyeccion. Y empuja deploy al server.
MIRROR_GEMINI_KEY=$(grep "^GEMINI_API_KEY=" "$SCRIPT_DIR/.env" 2>/dev/null | tail -1 | cut -d= -f2-)
if [ -n "$MIRROR_GEMINI_KEY" ]; then
    # Capturar output del bridge sin pipe que trague errores criticos
    bridge_log=$(GEMINI_API_KEY="$MIRROR_GEMINI_KEY" python3 "$SCRIPT_DIR/bridge-aurelius.py" 2>&1)
    bridge_rc=$?
    echo "$bridge_log" | tail -5
    if [ "$bridge_rc" -eq 0 ] && echo "$bridge_log" | grep -q "Episodio inyectado"; then
        echo -e "${GREEN}  ✅ Mirror Protocol episode injected${NC}"
        # Auto-commit + push del cambio en lyai.online (bridge no lo hace fiable)
        if (cd "$SCRIPT_DIR/lyai.online" && [ -n "$(git status --porcelain index.html 2>/dev/null)" ]); then
            ep_num=$(echo "$bridge_log" | grep -oE "Episode [0-9]+" | head -1)
            if (cd "$SCRIPT_DIR/lyai.online" \
                && git add index.html \
                && git commit -m "Mirror Protocol: ${ep_num:-Episode auto} ($(date -u +%Y-%m-%d))" >/dev/null \
                && git pull --rebase origin main >/dev/null 2>&1 \
                && git push origin main >/dev/null 2>&1); then
                echo -e "${GREEN}  ✅ Mirror Protocol commit + push (${ep_num})${NC}"
                # Auto-deploy: pull en server + sync a /var/www/lyai.online/
                ssh -o BatchMode=yes -o ConnectTimeout=10 lyai-prod \
                    "cd /opt/lyai/app/lyai.online \
                     && git stash push -u -m auto-deploy >/dev/null 2>&1; \
                     git pull --rebase origin main >/dev/null 2>&1 \
                     && git stash pop >/dev/null 2>&1; \
                     cp index.html /var/www/lyai.online/index.html" 2>/dev/null \
                    && echo -e "${GREEN}  ✅ Mirror Protocol deployed to /var/www/lyai.online${NC}" \
                    || echo -e "${YELLOW}  ⚠ Mirror Protocol deploy al server fallo (push OK, pendiente sync manual)${NC}"
            else
                echo -e "${YELLOW}  ⚠ Mirror Protocol commit/push fallo (cambios locales en lyai.online sin pushear)${NC}"
            fi
        else
            echo -e "${BLUE}  → Mirror Protocol: index.html sin cambios (episodio idempotente)${NC}"
        fi
    else
        echo -e "${YELLOW}  ⚠ Mirror Protocol generation failed (rc=$bridge_rc)${NC}"
    fi
else
    echo -e "${YELLOW}  ⚠ GEMINI_API_KEY no en .env — skipping Mirror Protocol${NC}"
fi


# Persistir sesión del día en lyai.sessions (BD) + lyai.session_embeddings (RAG)
# SEC-LEAK-1 FASE 3 — sustituye bridge-aurelius.py + HORCA sync (eliminados 2026-05-02)
# Ejecuta vía SSH+docker: el script vive en WSL pero la BD está en docker network del server
TODAY=$(date -u +"%Y-%m-%d")
SESSION_FILE="$SCRIPT_DIR/sessions/session-$TODAY.md"
if [ -f "$SESSION_FILE" ]; then
    echo -e "${YELLOW}  → Persistiendo sesión del día en BD + embeddings (vía lyai_mcp)...${NC}"
    NEW_PW=$(grep '^POSTGRES_LYAI_PASSWORD=' "$SCRIPT_DIR/.env" 2>/dev/null | cut -d= -f2-)
    if [ -z "$NEW_PW" ]; then
        echo -e "${YELLOW}  ⚠ POSTGRES_LYAI_PASSWORD no en .env, skipping persist${NC}"
    else
        scp -q "$SCRIPT_DIR/scripts/persist-session.py" lyai-prod:/tmp/persist-session.py 2>/dev/null
        scp -q "$SESSION_FILE" "lyai-prod:/tmp/session-$TODAY.md" 2>/dev/null
        ssh lyai-prod "docker cp /tmp/persist-session.py lyai_mcp:/tmp/ && docker cp /tmp/session-$TODAY.md lyai_mcp:/tmp/" 2>/dev/null
        GEMINI_KEY=$(ssh lyai-prod 'grep ^GEMINI_API_KEY= /opt/lyai/app/lyai-ski/backend/.env 2>/dev/null | cut -d= -f2- | tr -d "\""')
        ssh lyai-prod "docker exec \
            -e DB_DSN='postgresql://lyai:$NEW_PW@lyai_postgres:5432/lyai_db' \
            -e GEMINI_API_KEY='$GEMINI_KEY' \
            lyai_mcp python3 /tmp/persist-session.py --file /tmp/session-$TODAY.md --agente claude 2>&1" \
            | tail -10 \
            && echo -e "${GREEN}  ✅ Sesión persistida en lyai.sessions + lyai.session_embeddings${NC}" \
            || echo -e "${YELLOW}  ⚠ Persistencia falló — revisar logs${NC}"
    fi
else
    echo -e "${YELLOW}  ⚠ No session-$TODAY.md, skipping persist${NC}"
fi

# Sync wiki desde Hetzner prod → local para Obsidian
echo -e "${YELLOW}  → Sincronizando wiki desde Hetzner prod...${NC}"
bash "$SCRIPT_DIR/scripts/wiki-sync.sh" 2>/dev/null \
    && echo -e "${GREEN}  ✅ Wiki sincronizada${NC}" \
    || echo -e "${YELLOW}  ⚠ Wiki sync fallida${NC}"

# Procesar entradas pendientes de wiki (de agentes sin acceso directo a prod)
if [ -d "/tmp/wiki-pending" ] && [ "$(ls -A /tmp/wiki-pending 2>/dev/null)" ]; then
    echo -e "${YELLOW}  → Procesando wiki pendientes...${NC}"
    python3 "$SCRIPT_DIR/scripts/wiki-add.py" --flush-pending 2>/dev/null \
        && echo -e "${GREEN}  ✅ Wiki pendientes procesadas${NC}" \
        || echo -e "${YELLOW}  ⚠ Wiki pending flush fallido${NC}"
fi

# Sync agent memory files to project repo
MEMORY_SRC="/home/aipa/.claude/projects/-home-aipa-projects/memory"
MEMORY_DST="$SCRIPT_DIR/memory"
if [ -d "$MEMORY_SRC" ]; then
    mkdir -p "$MEMORY_DST"
    cp "$MEMORY_SRC"/*.md "$MEMORY_DST/" 2>/dev/null && echo -e "${GREEN}  ✅ Memory files synced${NC}" || echo -e "${YELLOW}  ⚠ Memory sync failed${NC}"
fi

echo -e "${YELLOW}  → Committing state files to git...${NC}"

cd "$SCRIPT_DIR"

# Check if state files have changes
if git diff --quiet STATE.json SESSION_LOG.md 2>/dev/null || [ ! -f "$SCRIPT_DIR/.git/HEAD" ]; then
    echo -e "${YELLOW}  → No changes to commit${NC}"
else
    git add STATE.json SESSION_LOG.md AGENT_MEMORY.md sessions/ memory/ lyai.online/
    # horca es un repo git separado (LyAi-labs/horca) — no se añade aquí
    git commit -m "State Update: $TIMESTAMP - $HOSTNAME" 2>/dev/null || true
    echo -e "${GREEN}  ✅ Committed state files${NC}"
    echo -e "${YELLOW}  → Pushing to origin...${NC}"
    # Auth: usa gh CLI (gh auth login) o ~/.netrc — no embebemos PAT en el script
    git pull origin main --rebase -q 2>/dev/null
    git push origin main 2>/dev/null \
        && echo -e "${GREEN}  ✅ Pushed to origin${NC}" \
        || echo -e "${YELLOW}  ⚠ Push failed — comprueba 'gh auth status' o ~/.netrc${NC}"
fi

# ──────────────────────────────────────────────────────────
# 6. Summary
# ──────────────────────────────────────────────────────────
echo ""
echo -e "${GREEN}✅ State update complete!${NC}"
echo ""
echo -e "${BLUE}Current State:${NC}"
echo "  Last Updated: $TIMESTAMP"
echo "  Machine: $HOSTNAME"
echo "  Docker: $DOCKER_STATUS"
echo "  lyai-core: $LYAI_STATUS"
echo "  cervell.lyai.pro: $CERVELL_STATUS"
echo "  horca: $HORCA_STATUS"
echo ""
echo -e "${BLUE}Files Updated:${NC}"
echo "  ✓ STATE.json"
echo "  ✓ SESSION_LOG.md"
echo "  ✓ AGENT_MEMORY.md"
echo ""
echo -e "${BLUE}For Agents:${NC}"
echo "  📖 Read: agents-context.md"
echo "  📊 Check: STATE.json"
echo "  📝 History: SESSION_LOG.md"
echo ""

