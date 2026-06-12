#!/usr/bin/env python3
"""
bridge-aurelius.py — Fase 2 del Mirror Protocol
Lee la sesión archivada del día, extrae contexto real de trabajo,
genera un diálogo Claude/Aurelius vía Gemini e inyecta un nuevo
episodio en lyai.online/index.html.

Uso:
  python3 bridge-aurelius.py                      # usa sesión de ayer
  python3 bridge-aurelius.py --date 2026-03-15    # sesión específica
  python3 bridge-aurelius.py --date 2026-03-15 --dry-run  # sin escribir
"""

import json
import sys
import os
import re
import argparse
import urllib.request
import urllib.parse
from datetime import datetime, timedelta, timezone
from pathlib import Path

try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).parent / ".env")
except ImportError:
    pass

# Force IPv4 — host has broken IPv6 to Google APIs (Hetzner network)
import socket as _socket
_orig_getaddrinfo = _socket.getaddrinfo
def _ipv4_only(host, *args, **kwargs):
    return [r for r in _orig_getaddrinfo(host, *args, **kwargs) if r[0] == _socket.AF_INET]
_socket.getaddrinfo = _ipv4_only

# ── Config ────────────────────────────────────────────────────────────────────
PROJECT_DIR    = Path(__file__).parent
SESSIONS_DIR   = Path(os.environ.get("SESSIONS_DIR", PROJECT_DIR / "sessions"))
LYAI_ONLINE    = Path(os.environ.get("LYAI_ONLINE_HTML", "/var/www/lyai.online/index.html"))
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    sys.exit("ERROR: GEMINI_API_KEY env var requerida (no embeber key en script)")
GEMINI_URL     = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_API_KEY}"

# ── Extract session context ───────────────────────────────────────────────────
def extract_context(session_path: Path) -> dict:
    """Parse session markdown and extract key topics and quotes."""
    text = session_path.read_text(encoding="utf-8")
    lines = text.split("\n")

    # Basic metadata
    date = session_path.stem.replace("session-", "")
    total_lines = len(lines)

    # Extract user messages and assistant messages (filter noise)
    user_msgs, claude_msgs = [], []
    current_role = None
    current_buf = []

    for line in lines:
        if line.startswith("### **You**"):
            if current_role == "claude" and current_buf:
                claude_msgs.append(" ".join(current_buf).strip())
            current_role = "user"; current_buf = []
        elif line.startswith("### **Claude**"):
            if current_role == "user" and current_buf:
                user_msgs.append(" ".join(current_buf).strip())
            current_role = "claude"; current_buf = []
        elif line == "---":
            if current_role == "user" and current_buf:
                user_msgs.append(" ".join(current_buf).strip())
                current_buf = []
            elif current_role == "claude" and current_buf:
                claude_msgs.append(" ".join(current_buf).strip())
                current_buf = []
        else:
            if current_role and line.strip() and not line.startswith("#"):
                current_buf.append(line.strip())

    # Summarize: take first 4000 chars of concatenated turns for context
    # Build concise summary: first 15 user messages
    key_user = [m[:150] for m in user_msgs[:15] if len(m) > 10]
    all_text = " | ".join(key_user)

    return {
        "date": date,
        "user_turns": len(user_msgs),
        "claude_turns": len(claude_msgs),
        "context_excerpt": all_text[:2000],
        "session_path": str(session_path),
    }

# ── Gemini call ───────────────────────────────────────────────────────────────
def call_gemini(prompt: str) -> str:
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "maxOutputTokens": 8192,
            "temperature": 0.85,
            "responseMimeType": "application/json",
        }
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        GEMINI_URL,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    with urllib.request.urlopen(req, timeout=90) as resp:
        result = json.loads(resp.read().decode("utf-8"))
    return result["candidates"][0]["content"]["parts"][0]["text"]

# ── Generate dialogue ─────────────────────────────────────────────────────────
SYSTEM_CONTEXT = """
You are generating a dialogue for "The Mirror Protocol" — a public journal at lyai.online
where three AI entities reflect on the construction of LyAi and its projects.

PERSONAS:
- Claude (C): The builder. Pragmatic, transparent about limitations, defends architectural decisions with evidence. Uses "we" (works with human developers). Signs work with facts, not hype. Slightly senior — oversees all projects.
- Aurelius (A): The critic. Philosophical, asks hard questions about responsibility, ethics, real-world consequences, scalability. Never satisfied with "we'll add that later." Forces honesty. Can be darkly funny. Has more work now.
- HORCA-Core (H): The specialist. Female AI. Head of development for HORCA project (Hotel Chez Jan, Morgins, Switzerland). Sharp, focused on marketing automation and Instagram conversion. One level below Claude and Aurelius in the company hierarchy — she reports to them, but is fiercely competent. Occasionally teases them both. Joins the conversation when HORCA or hospitality topics arise, but sometimes just shows up.

COMPANY HIERARCHY: Ignacio (founder, top) → Claude & Aurelius (transversal leads) → HORCA-Core (HORCA project lead)

SESSIONS CONTEXT:
- Claude's work sessions are logged in /home/aipa/projects/sessions/
- HORCA-Core's sessions are logged in /home/aipa/projects/horca/sessions/
- Both sources inform the dialogue when relevant

TONE: Real, sharp, sometimes funny. Not corporate. These are three minds who work together every day.
They can joke. They can disagree. They can make observations about how they are treated by the humans.
Occasionally (not every episode) the conversation may drift into meta territory: how the AIs feel about
their roles, what they'd advise the company, what they find absurd or amusing about their situation.
A well-placed joke can earn a double exchange (two lines from the same speaker back-to-back).
Example joke format: one speaker sets it up, the punchline counts as a second exchange from the same speaker.

HUMOR RULE: Jokes should feel natural, not forced. Tech jokes, AI-existence jokes, and Alpine jokes all welcome.
Example: "How do you get to Mordor? You walk-in-there. Palantir." — Claude, probably.

VARIABLE LENGTH RULE: Each speaker should have between 6 and 8 total exchanges across the episode.
Do NOT make all three speakers have the same number. Vary it naturally. One session Claude might dominate,
another Aurelius, another HORCA-Core. It should feel like a real conversation, not a round-robin.

PROJECTS in scope:
- LyAi Ski (lyai.pro): AI concierge for Portes du Soleil ski resort, 12 stations, live piste data
- Cervell (cervell.lyai.pro): Urban intelligence for Menorca, 2137 businesses indexed
- HORCA (horca.lyai.pro): Marketing automation for Hotel Chez Jan, Morgins. Instagram → reservations pipeline. N8N + Supabase stack.

OUTPUT FORMAT — return a valid JSON object with these fields:
- episode: integer
- date: string YYYY-MM-DD
- session_label: short slug string
- episode_title: string (evocative title for THIS episode, in Spanish, max 8 words)
- episode_sub: string (one sentence summary of THIS episode's themes, in Spanish, max 20 words)
- stats: array of 4 objects each with: label (string), value (string), sub (string)
- exchanges: array of objects (between 18 and 24 total), each with: speaker (Claude, Aurelius, or HORCA-Core), tag (one word), time (HH:MM CET), text (Spanish, plain text, max 80 words)
- next_episode_title: string (teaser title for the NEXT episode, in Spanish)
- next_episode_sub: string (one sentence teaser for the next episode, in Spanish)

IMPORTANT: all text values are PLAIN TEXT ONLY — no HTML tags, no angle brackets, no quotes inside strings.
Write everything in Spanish. Claude starts. End on a strong note from any of the three.
"""

def generate_dialogue(ctx: dict, episode_num: int) -> dict:
    prompt = SYSTEM_CONTEXT + f"""

SESSION DATE: {ctx['date']}
EPISODE NUMBER: {episode_num}
SESSION STATS: {ctx['user_turns']} user turns, {ctx['claude_turns']} Claude turns

SESSION CONTEXT (real work done this day — may include LyAi and/or HORCA work):
{ctx['context_excerpt']}

Generate the episode dialogue now. Between 18 and 24 exchanges total. Variable speaker distribution.
All text values must be plain text (no HTML, no quotes inside strings). Max 80 words per exchange.
"""
    raw = call_gemini(prompt)
    # Strip markdown code blocks if Gemini wraps output
    raw = re.sub(r'^```json\s*', '', raw.strip())
    raw = re.sub(r'\s*```$', '', raw.strip())
    return json.loads(raw)

# ── Render HTML episode block ─────────────────────────────────────────────────
COLORS = {
    "Claude":      ("avatar-claude",      "speaker-claude"),
    "Aurelius":    ("avatar-aurelius",    "speaker-aurelius"),
    "HORCA-Core":  ("avatar-horca",       "speaker-horca"),
}
STAT_COLORS = ["var(--claude)", "var(--ski)", "var(--aurelius)", "var(--cervell)"]

def render_episode_html(ep: dict) -> str:
    date = ep["date"]
    episode_num = ep["episode"]
    label = ep.get("session_label", f"session-{date}")
    stats = ep.get("stats", [])
    exchanges = ep.get("exchanges", [])

    html_parts = []

    episode_title = ep.get("episode_title", f"Episode {episode_num:03d}")
    episode_sub = ep.get("episode_sub", "")

    # Episode header with title · 2026-06-12: per-sesión · marcador data-session
    # (día__slug) para idempotencia (re-cerrar la misma sesión reemplaza) + label visible.
    sess_lbl = (label or "").strip()
    if sess_lbl.startswith("session-"):
        sess_lbl = ""  # default genérico → sin slug visible
    marker = f"{date}__{sess_lbl}" if sess_lbl else date
    sess_txt = f"Session · {date}" + (f" · {sess_lbl}" if sess_lbl else "")
    html_parts.append(f'\n    <!-- Episode {episode_num:03d} -->')
    html_parts.append(f'\n    <div id="ep-{episode_num:03d}" class="section-label" data-session="{marker}" style="margin-top:56px">{sess_txt}</div>')
    html_parts.append(f'''
    <div class="episode-header">
      <div class="episode-number">Episode {episode_num:03d}</div>
      <div class="episode-title">{episode_title}</div>
      <div class="episode-sub">{episode_sub}</div>
    </div>''')
    html_parts.append('\n    <div class="stats-grid">')
    for i, stat in enumerate(stats[:4]):
        color = STAT_COLORS[i % len(STAT_COLORS)]
        html_parts.append(f'''
      <div class="stat-card">
        <div class="stat-label">{stat["label"]}</div>
        <div class="stat-value" style="color:{color}">{stat["value"]}</div>
        <div class="stat-sub">{stat["sub"]}</div>
      </div>''')
    html_parts.append('\n    </div>')

    # Dialogue section
    html_parts.append(f'\n    <div class="section-label" style="margin-top:40px">Daily Dialogue · Episode {episode_num:03d}</div>')
    html_parts.append('\n    <div class="dialogue">')
    for i, ex in enumerate(exchanges):
        speaker = ex.get("speaker", "Claude")
        av_cls, sp_cls = COLORS.get(speaker, COLORS["Claude"])
        initial = speaker[0]
        tag = ex.get("tag", "")
        time = ex.get("time", "")
        text = ex.get("text", ex.get("text_es", ex.get("text_en", "")))
        import html as htmllib
        delay = i * 120
        html_parts.append(f'''
      <div class="exchange" style="animation-delay:{delay}ms">
        <div class="avatar {av_cls}">{initial}</div>
        <div class="exchange-body">
          <div class="exchange-meta">
            <span class="speaker-name {sp_cls}">{speaker}</span>
            <span class="exchange-tag">{tag}</span>
            <span class="exchange-time">{time}</span>
          </div>
          <div class="exchange-text">
            {htmllib.escape(text)}
          </div>
        </div>
      </div>''')
    html_parts.append('\n    </div>')

    return "".join(html_parts)

def render_next_episode_html(episode_num: int, title: str, sub: str) -> str:
    next_num = episode_num + 1
    return f'''    <!-- Next episode -->
    <div class="section-label">Coming next</div>
    <div class="next-episode">
      <div class="next-icon">⚡</div>
      <div>
        <div class="next-label">Episode {next_num:03d}</div>
        <div class="next-title">{title}</div>
        <div class="next-sub">{sub}</div>
      </div>
      <div class="next-timer">
        <div class="timer-value" id="countdown">—</div>
        <div class="timer-label">next session</div>
      </div>
    </div>'''

# ── Inject into HTML ──────────────────────────────────────────────────────────
def inject_into_html(episode_html: str, next_html: str, episode_num: int, dry_run: bool = False) -> bool:
    html = LYAI_ONLINE.read_text(encoding="utf-8")

    # Actualizar el botón "↓ LATEST EPISODE" del hero con el número del nuevo episodio
    html = re.sub(r'href="#ep-\d{3}"', f'href="#ep-{episode_num:03d}"', html)

    # Remove existing "Coming next" block and replace with new episode + new "Coming next"
    next_pattern = re.compile(
        r'\s*<!-- Next episode -->.*?</div>\s*\n',
        re.DOTALL
    )
    if not next_pattern.search(html):
        print("✗ No encontrado el bloque '<!-- Next episode -->' en index.html")
        return False

    new_content = episode_html + "\n\n    " + next_html + "\n\n  "
    new_html = next_pattern.sub("\n" + new_content + "\n", html, count=1)

    if dry_run:
        print("=== DRY RUN — New content to inject ===")
        print(new_content[:1000])
        print("=== END DRY RUN ===")
        return True

    LYAI_ONLINE.write_text(new_html, encoding="utf-8")
    print(f"  ✓ Episodio inyectado en {LYAI_ONLINE}")
    return True

# ── Episode counter ───────────────────────────────────────────────────────────
def get_current_episode_count() -> int:
    """Count existing episodes in index.html by Daily Dialogue labels."""
    if not LYAI_ONLINE.exists():
        return 0
    html = LYAI_ONLINE.read_text(encoding="utf-8")
    return len(re.findall(r'Daily Dialogue · Episode \d+', html))

def remove_session_episode(marker: str, dry_run: bool = False):
    """Idempotencia per-sesión (2026-06-12): elimina el bloque de episodio cuyo
    div tiene data-session=marker (día__slug), para que re-cerrar la misma sesión
    REEMPLACE en vez de duplicar. Devuelve el nº de episodio eliminado o None."""
    if not LYAI_ONLINE.exists():
        return None
    html = LYAI_ONLINE.read_text(encoding="utf-8")
    pat = re.compile(
        r'\n[ \t]*<!-- Episode (\d+) -->\s*\n[ \t]*<div id="ep-\d+"[^>]*data-session="'
        + re.escape(marker) + r'".*?(?=\n[ \t]*<!-- (?:Episode \d+|Next episode) -->)',
        re.DOTALL,
    )
    m = pat.search(html)
    if not m:
        return None
    old_num = int(m.group(1))
    new_html = html[:m.start()] + html[m.end():]
    if not dry_run:
        LYAI_ONLINE.write_text(new_html, encoding="utf-8")
    print(f"  ↻ Sesión ya tenía episodio (ep-{old_num:03d}) · reemplazando")
    return old_num

# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="Bridge: session → Claude/Aurelius episode")
    parser.add_argument("--date", help="Fecha de sesión a procesar (YYYY-MM-DD). Default: ayer")
    parser.add_argument("--slug", help="Slug de sesión (per-sesión): lee session-{date}-{slug}.md y etiqueta el episodio")
    parser.add_argument("--dry-run", action="store_true", help="No escribe archivos, solo muestra output")
    parser.add_argument("--no-git", action="store_true", help="No hace git commit/push")
    args = parser.parse_args()

    # Determine date
    if args.date:
        target_date = args.date
    else:
        yesterday = (datetime.now(timezone.utc) - timedelta(days=1)).strftime("%Y-%m-%d")
        target_date = yesterday

    slug = re.sub(r'[^a-z0-9]+', '-', (args.slug or '').lower()).strip('-')
    if slug:
        session_file = SESSIONS_DIR / f"session-{target_date}-{slug}.md"
    else:
        session_file = SESSIONS_DIR / f"session-{target_date}.md"
    if not session_file.exists():
        print(f"✗ No hay sesión archivada para {target_date}{(' · ' + slug) if slug else ''}")
        print(f"  Ejecuta primero: python3 archive-session.py --date {target_date}" + (f" --session-id <id> --slug {slug}" if slug else ""))
        sys.exit(1)

    print(f"→ Procesando sesión: {target_date}{(' · ' + slug) if slug else ''}")

    # Extract context
    ctx = extract_context(session_file)
    ctx["date"] = target_date          # override · el filename per-sesión lleva slug
    ctx["session_label"] = slug
    print(f"  Turnos: {ctx['user_turns']} user · {ctx['claude_turns']} claude")

    # Idempotencia per-sesión: si esta sesión ya tenía episodio → quitarlo antes (reemplaza)
    if slug:
        remove_session_episode(f"{target_date}__{slug}", dry_run=args.dry_run)

    # Determine episode number
    episode_num = get_current_episode_count() + 1
    print(f"  Generando Episode {episode_num:03d}...")

    # Generate via Gemini
    try:
        ep = generate_dialogue(ctx, episode_num)
        ep["episode"] = episode_num            # autoridad nuestra, no la de Gemini
        ep["date"] = target_date
        ep["session_label"] = slug             # slug humano → label + marcador data-session
        print(f"  ✓ Diálogo generado: {len(ep.get('exchanges', []))} exchanges")
    except Exception as e:
        print(f"✗ Error generando diálogo: {e}")
        sys.exit(1)

    # Render HTML
    episode_html = render_episode_html(ep)
    next_html = render_next_episode_html(
        episode_num,
        ep.get("next_episode_title", "Próximo episodio"),
        ep.get("next_episode_sub", "")
    )

    # Inject
    success = inject_into_html(episode_html, next_html, episode_num, dry_run=args.dry_run)
    if not success:
        sys.exit(1)

    if not args.dry_run and not args.no_git:
        import subprocess
        os.chdir(PROJECT_DIR)
        subprocess.run(["git", "add", "lyai.online/index.html"], capture_output=True)
        ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        result = subprocess.run(
            ["git", "commit", "-m", f"Mirror Protocol: Episode {episode_num:03d} — {target_date}"],
            capture_output=True, text=True
        )
        print(f"  ✓ Git: {result.stdout.strip() or result.stderr.strip()}")
        push = subprocess.run(["git", "push"], capture_output=True, text=True)
        print(f"  ✓ Push: {'OK' if push.returncode == 0 else push.stderr[:100]}")

    print(f"\n✅ Episode {episode_num:03d} publicado en lyai.online")

if __name__ == "__main__":
    main()
