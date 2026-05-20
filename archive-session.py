#!/usr/bin/env python3
"""
archive-session.py — Extrae y archiva sesiones de trabajo Claude Code
Genera un archivo markdown por día de sesión en ./sessions/
No modifica el frontend de lyai.online ni ningún archivo existente.

Uso:
  python3 archive-session.py              # archiva todas las sesiones del JSONL activo
  python3 archive-session.py --date 2026-03-15  # solo un día concreto
  python3 archive-session.py --push       # archiva + sube al servidor
"""

import json
import sys
import os
import re
import argparse
from datetime import datetime, timezone
from pathlib import Path
from collections import defaultdict

# ── Config ────────────────────────────────────────────────────────────────────
PROJECT_DIR   = Path(__file__).parent
SESSIONS_DIR  = Path(os.environ.get("SESSIONS_DIR", PROJECT_DIR / "sessions"))
JSONL_DIR     = Path(os.environ.get("JSONL_DIR", Path.home() / ".claude/projects"))
JSONL_RECURSIVE = os.environ.get("JSONL_RECURSIVE", "1") == "1"
SERVER_HOST   = "lyai@178.63.165.87"
SERVER_PATH   = "/opt/lyai/sessions"

SESSIONS_DIR.mkdir(exist_ok=True)

# ── Helpers ───────────────────────────────────────────────────────────────────
def find_all_jsonl():
    """Devuelve todos los archivos .jsonl ordenados por fecha de modificación."""
    glob_fn = JSONL_DIR.rglob if JSONL_RECURSIVE else JSONL_DIR.glob
    return sorted(glob_fn("*.jsonl"), key=lambda f: f.stat().st_mtime)

def extract_text(content):
    """Extract plain text from message content (str or list of blocks)."""
    if isinstance(content, str):
        return content.strip()
    if isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, dict):
                if block.get("type") == "text":
                    parts.append(block.get("text", "").strip())
                elif block.get("type") == "tool_result":
                    pass  # skip tool noise
        return "\n".join(p for p in parts if p)
    return ""

def load_sessions(jsonl_paths):
    """Load and group messages by calendar day from one or more JSONL files."""
    days = defaultdict(list)
    if not isinstance(jsonl_paths, list):
        jsonl_paths = [jsonl_paths]
    for jsonl_path in jsonl_paths:
        with open(jsonl_path) as f:
            for line in f:
                try:
                    d = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if d.get("type") not in ("user", "assistant"):
                    continue
                msg = d.get("message", {})
                role = msg.get("role", "")
                if role not in ("user", "assistant"):
                    continue
                ts = d.get("timestamp", "")
                day = ts[:10]
                if not day:
                    continue
                text = extract_text(msg.get("content", ""))
                if not text:
                    continue
                if role == "user" and len(text) < 3:
                    continue
                days[day].append({
                    "role": role,
                    "ts": ts,
                    "text": text,
                })
    return days

def render_day(day, turns):
    """Render one session day as markdown."""
    date_obj = datetime.fromisoformat(day)
    header = f"# Session Archive — {day}\n\n"
    header += f"**Date**: {date_obj.strftime('%A, %d %B %Y')}  \n"
    header += f"**Turns**: {len(turns)} ({sum(1 for t in turns if t['role']=='user')} user · {sum(1 for t in turns if t['role']=='assistant')} assistant)  \n"
    header += f"**Project**: lyai-core / cervell.lyai.pro  \n\n"
    header += "---\n\n"

    body = ""
    for turn in turns:
        role_label = "**Claude**" if turn["role"] == "assistant" else "**You**"
        time_str = turn["ts"][11:16] if len(turn["ts"]) >= 16 else ""
        text = turn["text"]
        # Sin truncado — queremos el historial completo
        body += f"### {role_label} `{time_str}`\n\n{text}\n\n---\n\n"

    return header + body

def archive_day(day, turns, force=False):
    out_path = SESSIONS_DIR / f"session-{day}.md"
    if out_path.exists() and not force:
        print(f"  ↷ {day}: ya existe, omitiendo (usa --force para sobreescribir)")
        return out_path
    content = render_day(day, turns)
    out_path.write_text(content, encoding="utf-8")
    print(f"  ✓ {day}: {len(turns)} turnos → {out_path.name}")
    return out_path

def push_to_server(paths):
    """rsync sessions dir to server."""
    import subprocess
    print(f"\n→ Subiendo a {SERVER_HOST}:{SERVER_PATH} ...")
    cmd = [
        "rsync", "-avz", "--mkpath",
        str(SESSIONS_DIR) + "/",
        f"{SERVER_HOST}:{SERVER_PATH}/"
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        print("  ✓ Subida completada")
    else:
        print(f"  ✗ Error rsync: {result.stderr[:200]}")

def git_commit_sessions():
    """Commit new session files to git."""
    import subprocess
    os.chdir(PROJECT_DIR)
    subprocess.run(["git", "add", "sessions/"], capture_output=True)
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    result = subprocess.run(
        ["git", "commit", "-m", f"Archive sessions: {ts}"],
        capture_output=True, text=True
    )
    if "nothing to commit" in result.stdout + result.stderr:
        print("  → Git: nada nuevo que commitear")
    else:
        print(f"  ✓ Git commit: Archive sessions {ts}")

# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="Archive Claude Code sessions")
    parser.add_argument("--date", help="Solo archivar este día (YYYY-MM-DD)")
    parser.add_argument("--push", action="store_true", help="Subir al servidor tras archivar")
    parser.add_argument("--force", action="store_true", help="Sobreescribir archivos existentes")
    parser.add_argument("--no-git", action="store_true", help="No hacer git commit")
    args = parser.parse_args()

    jsonls = find_all_jsonl()
    if not jsonls:
        print("✗ No se encontró archivo JSONL de sesión")
        sys.exit(1)

    print(f"→ Leyendo {len(jsonls)} archivo(s) JSONL")
    days = load_sessions(jsonls)
    print(f"→ Días encontrados: {', '.join(sorted(days.keys()))}\n")

    archived = []
    target_days = [args.date] if args.date else sorted(days.keys())
    for day in target_days:
        if day not in days:
            print(f"  ✗ {day}: no hay datos")
            continue
        path = archive_day(day, days[day], force=args.force)
        archived.append(path)

    if archived and not args.no_git:
        git_commit_sessions()

    if args.push and archived:
        push_to_server(archived)

    print(f"\n✅ {len(archived)} sesión(es) archivada(s) en {SESSIONS_DIR}/")

if __name__ == "__main__":
    main()
