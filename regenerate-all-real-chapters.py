#!/usr/bin/env python3
"""
Generate REAL chapters from ALL JSONL sessions across all project directories.
Extracts real titles and work summaries from conversation content.
"""

import json
import re
from pathlib import Path
from collections import defaultdict

SESSIONS_DIR = Path("/home/lyai/.claude/projects")
OUTPUT_FILE = Path("/var/www/lyai.online/index.html")

def analyze_session(jsonl_file):
    """Extract work summary from session JSONL."""
    data = {
        'title': '',
        'timestamp': None,
        'user_prompts': 0,
        'assistant_responses': 0,
        'commits': [],
        'files': set(),
        'keywords': defaultdict(int),
    }

    try:
        with open(jsonl_file, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    msg = json.loads(line.strip())
                except:
                    continue

                msg_type = msg.get('type', '')
                ts = msg.get('timestamp')

                if ts and not data['timestamp']:
                    data['timestamp'] = ts[:10]

                # Extract title (highest priority)
                if msg_type == 'ai-title' and not data['title']:
                    title = msg.get('aiTitle', '').strip()
                    if title:
                        data['title'] = title

                # Count interactions
                elif msg_type == 'user':
                    data['user_prompts'] += 1

                elif msg_type == 'assistant':
                    data['assistant_responses'] += 1
                    content = msg.get('message', '')
                    if content:
                        # Find commits
                        commits = re.findall(r'commit\s+([a-f0-9]{7,})', content, re.I)
                        if commits:
                            data['commits'].extend(commits[:1])

                        # Find files
                        files = re.findall(r'\b([a-zA-Z0-9_\-./]+\.(py|js|tsx|sql|yaml|yml|json|md))\b', content)
                        if files:
                            data['files'].update([f[0] for f in files[:5]])

                        # Extract keywords
                        if re.search(r'(?i)fixed|resolved|corrected|error|bug', content):
                            data['keywords']['fix'] += 1
                        if re.search(r'(?i)added|created|implemented|new feature', content):
                            data['keywords']['feature'] += 1
                        if re.search(r'(?i)deployed|pushed|merged|released', content):
                            data['keywords']['deploy'] += 1
                        if re.search(r'(?i)tested|test|verification', content):
                            data['keywords']['test'] += 1
                        if re.search(r'(?i)refactored|cleanup|organized', content):
                            data['keywords']['refactor'] += 1

        return data

    except Exception as e:
        return data

def build_description(data):
    """Build chapter description from extracted data."""
    parts = []

    # Show title
    if data['title']:
        parts.append(f"📝 {data['title'][:70]}")
    else:
        parts.append("📝 Development session")

    # Show activities
    activities = []
    for activity in ['feature', 'fix', 'deploy', 'test', 'refactor']:
        if data['keywords'].get(activity, 0) > 0:
            activities.append(activity)

    if activities:
        parts.append(" · ".join(activities))

    # Show metrics
    metrics = []
    if data['commits']:
        metrics.append(f"{len(set(data['commits']))} commit{'s' if len(set(data['commits'])) > 1 else ''}")
    if data['files']:
        metrics.append(f"{len(data['files'])} files")
    if data['assistant_responses'] > 0:
        metrics.append(f"{data['assistant_responses']} responses")

    if metrics:
        parts.append(" | ".join(metrics))

    return " • ".join(parts)

def generate_chapter_html(idx, session_id, data):
    """Generate HTML for a chapter."""
    colors = ["#60a5fa", "#fb923c", "#34d399", "#f472b6", "#fbbf24", "#ec4899"]
    color = colors[idx % len(colors)]

    description = build_description(data)

    html = f'''
    <div class="chapter" style="border-left: 4px solid {color}; padding-left: 16px; margin-bottom: 24px;">
      <div style="display: flex; align-items: baseline; gap: 12px; margin-bottom: 8px;">
        <span style="font-size: 2rem; font-weight: 600; color: {color};">#{idx:02d}</span>
        <span style="font-family: 'JetBrains Mono'; font-size: 0.85rem; color: #9ea3b0;">{data['timestamp'] or '—'}</span>
        <span style="font-family: 'JetBrains Mono'; font-size: 0.75rem; color: #4b5563; margin-left: auto;">{session_id}</span>
      </div>
      <p style="font-size: 0.95rem; color: #f5f4ef; margin: 0; line-height: 1.5;">
        {description}
      </p>
    </div>
    '''
    return html

def main():
    print("🔄 Extracting REAL work from ALL sessions...\n")

    # Find ALL JSONL files (main sessions only, no subagents)
    all_files = list(SESSIONS_DIR.rglob("*.jsonl"))
    main_sessions = [f for f in all_files if '/subagents/' not in str(f)]

    # Sort by timestamp from earliest to latest
    def get_session_date(jsonl_file):
        try:
            with open(jsonl_file) as f:
                for line in f:
                    msg = json.loads(line.strip())
                    ts = msg.get('timestamp')
                    if ts:
                        return ts[:10]
        except:
            pass
        return "2099-12-31"  # Put undated at end

    main_sessions = sorted(main_sessions, key=get_session_date)

    print(f"📖 Found {len(main_sessions)} main sessions\n")

    chapters = []
    for idx, session_file in enumerate(main_sessions, 1):
        session_id = session_file.stem[:8]
        data = analyze_session(session_file)

        if data and (data['user_prompts'] > 0 or data['assistant_responses'] > 0):
            description = build_description(data)
            status = "✅" if data['title'] else "📊"
            ts_display = data['timestamp'] if data['timestamp'] else "—"
            print(f"   {status} [{idx:2d}] {ts_display} {session_id} — {description[:75]}")
            chapter = generate_chapter_html(idx, session_id, data)
            chapters.append(chapter)

    chapters_section = "\n".join(chapters)

    # Calculate date range
    first_date = "—"
    last_date = "—"
    if chapters:
        # Get first and last dates from chapters
        dates = []
        for i in range(len(main_sessions)):
            if i < len(main_sessions):
                data = analyze_session(main_sessions[i])
                if data and data['timestamp']:
                    dates.append(data['timestamp'])
        if dates:
            first_date = min(dates)
            last_date = max(dates)

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
    <p class="subtitle">Mirror Protocol — Complete Work Timeline</p>
    <div class="stats">
      <div>📊 {len(chapters)} Chapters</div>
      <div>🔄 Content-Analyzed</div>
      <div>📅 {first_date} to {last_date}</div>
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
