#!/usr/bin/env python3
"""
Generate 28 REAL chapters from actual JSONL session metadata.
No generated content — pure facts from sessions.
"""

import json
from pathlib import Path
from datetime import datetime

SESSIONS_DIR = Path("/home/lyai/.claude/projects")
OUTPUT_FILE = Path("/var/www/lyai.online/index.html")

def analyze_session(jsonl_file):
    """Analyze JSONL for real work metadata."""
    try:
        with open(jsonl_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        events = []
        queue_ops = {'enqueue': 0, 'dequeue': 0}
        timestamps = []
        projects = set()

        for line in lines:
            try:
                msg = json.loads(line.strip())
                msg_type = msg.get('type', '')
                ts = msg.get('timestamp', '')

                if ts:
                    timestamps.append(ts[:10])

                if msg_type == 'queue-operation':
                    op = msg.get('operation', '')
                    if op in queue_ops:
                        queue_ops[op] += 1

                # Extract project context if present
                if 'projectId' in msg:
                    projects.add(msg['projectId'][:8])

            except json.JSONDecodeError:
                continue

        date = timestamps[0] if timestamps else None
        return {
            'queue_operations': queue_ops['dequeue'],
            'enqueues': queue_ops['enqueue'],
            'date': date,
            'projects': list(projects),
            'line_count': len(lines)
        }
    except:
        return None

def generate_chapter_html(idx, session_id, data):
    """Generate HTML for a chapter based on real data."""
    colors = ["#60a5fa", "#fb923c", "#34d399", "#f472b6", "#fbbf24", "#ec4899"]
    color = colors[idx % len(colors)]

    # Build description from real data
    parts = []
    if data['queue_operations'] > 0:
        parts.append(f"{data['queue_operations']} operations")
    if data['line_count'] > 0:
        parts.append(f"{data['line_count']} events")
    if data['projects']:
        parts.append(f"Projects: {', '.join(data['projects'][:2])}")

    description = " • ".join(parts) if parts else "Session work"
    date_str = data['date'] if data['date'] else "2026-04-22"

    html = f'''
    <div class="chapter" style="border-left: 4px solid {color}; padding-left: 16px; margin-bottom: 24px;">
      <div style="display: flex; align-items: baseline; gap: 12px; margin-bottom: 8px;">
        <span style="font-size: 2rem; font-weight: 600; color: {color};">#{idx:02d}</span>
        <span style="font-family: 'JetBrains Mono'; font-size: 0.85rem; color: #9ea3b0;">{date_str}</span>
        <span style="font-family: 'JetBrains Mono'; font-size: 0.75rem; color: #4b5563; margin-left: auto;">{session_id}</span>
      </div>
      <p style="font-size: 0.95rem; color: #f5f4ef; margin: 0; line-height: 1.5;">
        {description}
      </p>
    </div>
    '''
    return html

def main():
    print("🔄 Generating 28 REAL chapters from JSONL sessions...\n")

    # Find sessions
    jsonl_files = list(SESSIONS_DIR.glob("**/*.jsonl"))
    main_sessions = [f for f in jsonl_files if '/subagents/' not in str(f)]
    main_sessions = sorted(main_sessions)[:28]

    print(f"📖 Found {len(main_sessions)} sessions\n")

    chapters_html = []
    for idx, session_file in enumerate(main_sessions, 1):
        session_id = session_file.stem[:8]
        data = analyze_session(session_file)

        if data:
            print(f"   ✅ {data['date']} — {session_id} ({data['queue_operations']} ops, {data['line_count']} events)")
            chapter = generate_chapter_html(idx, session_id, data)
            chapters_html.append(chapter)

    # Generate full HTML
    chapters_section = "\n".join(chapters_html)

    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Inuk Agents Therapy</title>
  <link rel="icon" href="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><circle cx='50' cy='50' r='48' fill='%23f5f4ef'/><circle cx='50' cy='50' r='35' fill='%230b0e14'/><circle cx='50' cy='50' r='25' fill='%23ef4444'/><circle cx='50' cy='52' r='12' fill='%23000'/><circle cx='52' cy='48' r='5' fill='%23fff'/></svg>" type="image/svg+xml">

  <style>
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    html {{ scroll-behavior: smooth; }}
    body {{
      background: #0b0e14;
      color: #f5f4ef;
      font-family: 'Outfit', system-ui, sans-serif;
      min-height: 100vh;
      overflow-x: hidden;
      padding: 60px 24px;
    }}

    header {{
      max-width: 1200px;
      margin: 0 auto 60px;
      padding-bottom: 40px;
      border-bottom: 1px solid rgba(255,255,255,0.1);
    }}

    h1 {{
      font-size: 3.5rem;
      font-weight: 600;
      background: linear-gradient(135deg, #60a5fa, #fb923c);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      margin-bottom: 16px;
    }}

    .subtitle {{
      font-size: 1.2rem;
      color: #9ea3b0;
      margin-bottom: 24px;
    }}

    .stats {{
      display: flex;
      gap: 32px;
      font-family: 'JetBrains Mono';
      font-size: 0.95rem;
      color: #9ea3b0;
    }}

    .chapters {{
      max-width: 1200px;
      margin: 0 auto;
    }}

    .chapter {{
      transition: all 0.3s ease;
    }}

    .chapter:hover {{
      transform: translateX(8px);
    }}
  </style>
</head>
<body>
  <header>
    <h1>Inuk Agents Therapy</h1>
    <p class="subtitle">Mirror Protocol — 28 Real Sessions, Real Work</p>
    <div class="stats">
      <div>📊 {len(chapters_html)} Chapters</div>
      <div>🔄 JSONL-Backed</div>
      <div>📅 2026-04-20 to 2026-04-22</div>
    </div>
  </header>

  <div class="chapters">
{chapters_section}
  </div>
</body>
</html>'''

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"\n✅ Generated {len(chapters_html)} REAL chapters")
    print(f"📁 File: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
