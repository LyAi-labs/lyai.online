#!/usr/bin/env python3
"""
Generate REAL chapters from JSONL — using titles and assistant message analysis.
"""

import json
import re
from pathlib import Path
from collections import defaultdict

SESSIONS_DIR = Path("/home/lyai/.claude/projects")
OUTPUT_FILE = Path("/var/www/lyai.online/index.html")

def analyze_session(jsonl_file):
    """Extract work summary from session JSONL."""
    try:
        with open(jsonl_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        data = {
            'title': '',
            'timestamp': None,
            'user_prompts': 0,
            'assistant_responses': 0,
            'commits': [],
            'files': set(),
            'keywords': defaultdict(int)
        }

        for line in lines:
            try:
                msg = json.loads(line.strip())
                msg_type = msg.get('type', '')
                ts = msg.get('timestamp')

                if ts and not data['timestamp']:
                    data['timestamp'] = ts[:10]

                # Extract title
                if msg_type == 'ai-title':
                    data['title'] = msg.get('aiTitle', '').strip()

                # Count user prompts
                elif msg_type == 'user':
                    data['user_prompts'] += 1

                # Analyze assistant messages for work done
                elif msg_type == 'assistant':
                    content = msg.get('message', '')
                    data['assistant_responses'] += 1

                    # Find commits
                    commits = re.findall(r'commit\s+([a-f0-9]{7,})', content, re.I)
                    data['commits'].extend(commits[:1])

                    # Find files
                    files = re.findall(r'\b([a-zA-Z0-9_\-./]+\.(py|js|tsx|sql|yaml|yml|json|md))\b', content)
                    data['files'].update([f[0] for f in files])

                    # Keywords for work categorization
                    keywords = {
                        'fixed': re.findall(r'(?i)fixed|resolved|corrected', content),
                        'added': re.findall(r'(?i)added|created|implemented', content),
                        'deployed': re.findall(r'(?i)deployed|pushed|merged', content),
                        'tested': re.findall(r'(?i)tested|verified|checked', content),
                        'refactored': re.findall(r'(?i)refactored|cleaned|reorganized', content),
                        'debugged': re.findall(r'(?i)debug|trace|investigate', content)
                    }
                    for kw, matches in keywords.items():
                        if matches:
                            data['keywords'][kw] += 1

            except json.JSONDecodeError:
                pass

        return data

    except Exception as e:
        return None

def build_description(data):
    """Build chapter description from extracted data."""
    parts = []

    # Add title if exists
    if data['title']:
        parts.append(f"📝 {data['title'][:60]}")

    # Add key activities
    activities = []
    if data['keywords'].get('added'):
        activities.append("feature")
    if data['keywords'].get('fixed'):
        activities.append("fix")
    if data['keywords'].get('refactored'):
        activities.append("refactor")
    if data['keywords'].get('deployed'):
        activities.append("deploy")
    if data['keywords'].get('tested'):
        activities.append("testing")

    if activities:
        parts.append(" · ".join(activities))

    # Add metrics
    metrics = []
    if data['commits']:
        metrics.append(f"{len(data['commits'])} commit{'s' if len(data['commits']) > 1 else ''}")
    if data['files']:
        metrics.append(f"{len(data['files'])} files")
    if data['user_prompts'] > 0:
        metrics.append(f"{data['user_prompts']} exchanges")

    if metrics:
        parts.append(" | ".join(metrics))

    return " • ".join(parts) if parts else "Development work"

def generate_chapter_html(idx, session_id, data):
    """Generate HTML for a chapter."""
    colors = ["#60a5fa", "#fb923c", "#34d399", "#f472b6", "#fbbf24", "#ec4899"]
    color = colors[idx % len(colors)]

    description = build_description(data)

    html = f'''
    <div class="chapter" style="border-left: 4px solid {color}; padding-left: 16px; margin-bottom: 24px;">
      <div style="display: flex; align-items: baseline; gap: 12px; margin-bottom: 8px;">
        <span style="font-size: 2rem; font-weight: 600; color: {color};">#{idx:02d}</span>
        <span style="font-family: 'JetBrains Mono'; font-size: 0.85rem; color: #9ea3b0;">{data['timestamp'] or '2026-04-22'}</span>
        <span style="font-family: 'JetBrains Mono'; font-size: 0.75rem; color: #4b5563; margin-left: auto;">{session_id}</span>
      </div>
      <p style="font-size: 0.95rem; color: #f5f4ef; margin: 0; line-height: 1.5;">
        {description}
      </p>
    </div>
    '''
    return html

def main():
    print("🔄 Extracting REAL work from session conversations...\n")

    jsonl_files = list(SESSIONS_DIR.glob("**/*.jsonl"))
    main_sessions = [f for f in jsonl_files if '/subagents/' not in str(f)]
    main_sessions = sorted(main_sessions)

    print(f"📖 Found {len(main_sessions)} sessions\n")

    chapters = []
    for idx, session_file in enumerate(main_sessions, 1):
        session_id = session_file.stem[:8]
        data = analyze_session(session_file)

        if data:
            description = build_description(data)
            print(f"   [{idx:2d}] {session_id} ({data['timestamp']}) — {description[:80]}")
            chapter = generate_chapter_html(idx, session_id, data)
            chapters.append(chapter)

    chapters_section = "\n".join(chapters)

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
    <p class="subtitle">Mirror Protocol — Real Sessions, Real Work</p>
    <div class="stats">
      <div>📊 {len(chapters)} Chapters</div>
      <div>🔄 Work-Extracted</div>
      <div>📅 2026-04-18 to 2026-04-22</div>
    </div>
  </header>

  <div class="chapters">
{chapters_section}
  </div>
</body>
</html>'''

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"\n✅ Generated {len(chapters)} REAL chapters")
    print(f"📁 {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
