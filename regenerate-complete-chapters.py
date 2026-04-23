#!/usr/bin/env python3
"""
Generate COMPLETE chapters from BOTH markdown session docs + JSONL sessions.
Creates unified timeline from 2026-03-14 to 2026-04-22.
"""

import json
import re
from pathlib import Path
from collections import defaultdict

DOCS_DIR = Path("/home/lyai/docs/media")
SESSIONS_DIR = Path("/home/lyai/.claude/projects")
OUTPUT_FILE = Path("/var/www/lyai.online/index.html")

def extract_md_session(md_file):
    """Extract session info from markdown file."""
    data = {
        'source': 'markdown',
        'timestamp': None,
        'title': '',
        'turns': 0,
        'project': '',
        'content_preview': '',
    }

    try:
        with open(md_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Extract date from filename or header
        match = re.search(r'session-(\d{4})-(\d{2})-(\d{2})', md_file.name)
        if match:
            data['timestamp'] = f"{match.group(1)}-{match.group(2)}-{match.group(3)}"

        # Extract metadata from header
        metadata_match = re.search(r'\*\*Date\*\*:.*?(\d+\s+\w+\s+\d+).*?\n.*?\*\*Turns\*\*:.*?(\d+).*?\n.*?\*\*Project\*\*:([^\n]+)', content)
        if metadata_match:
            data['turns'] = int(metadata_match.group(2))
            data['project'] = metadata_match.group(3).strip()

        # Extract first meaningful user message as preview
        user_matches = re.findall(r'### \*\*You\*\*.*?\n\n(.*?)\n\n---', content, re.DOTALL)
        if user_matches:
            preview = user_matches[0][:100].replace('\n', ' ').strip()
            if len(preview) > 20:
                data['content_preview'] = preview

        return data

    except Exception as e:
        return None

def extract_jsonl_session(jsonl_file):
    """Extract session info from JSONL file."""
    data = {
        'source': 'jsonl',
        'timestamp': None,
        'title': '',
        'turns': 0,
        'project': '',
        'content_preview': '',
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

                # Extract title
                if msg_type == 'ai-title' and not data['title']:
                    title = msg.get('aiTitle', '').strip()
                    if title:
                        data['title'] = title

                # Count interactions
                elif msg_type == 'user':
                    data['turns'] += 1
                elif msg_type == 'assistant':
                    data['turns'] += 1

        return data

    except Exception as e:
        return None

def build_description(data):
    """Build chapter description."""
    parts = []

    # Show title/project
    if data.get('title'):
        parts.append(f"📝 {data['title'][:70]}")
    elif data.get('project'):
        parts.append(f"📂 {data['project'][:70]}")
    else:
        parts.append("📝 Development session")

    # Show metrics
    if data.get('turns'):
        parts.append(f"{data['turns']} turns")

    return " • ".join(parts)

def generate_chapter_html(idx, session_id, data):
    """Generate HTML for a chapter."""
    colors = ["#60a5fa", "#fb923c", "#34d399", "#f472b6", "#fbbf24", "#ec4899"]
    color = colors[idx % len(colors)]

    description = build_description(data)
    timestamp = data.get('timestamp') or '—'

    html = f'''
    <div class="chapter" style="border-left: 4px solid {color}; padding-left: 16px; margin-bottom: 24px;">
      <div style="display: flex; align-items: baseline; gap: 12px; margin-bottom: 8px;">
        <span style="font-size: 2rem; font-weight: 600; color: {color};">#{idx:02d}</span>
        <span style="font-family: 'JetBrains Mono'; font-size: 0.85rem; color: #9ea3b0;">{timestamp}</span>
        <span style="font-family: 'JetBrains Mono'; font-size: 0.75rem; color: #4b5563; margin-left: auto;">{session_id}</span>
      </div>
      <p style="font-size: 0.95rem; color: #f5f4ef; margin: 0; line-height: 1.5;">
        {description}
      </p>
    </div>
    '''
    return html

def main():
    print("🔄 Generating COMPLETE chapter timeline...\n")

    all_chapters = []

    # 1. Load markdown sessions
    md_files = sorted(DOCS_DIR.glob("session-*.md"))
    print(f"📄 Found {len(md_files)} markdown session docs")

    for md_file in md_files:
        data = extract_md_session(md_file)
        if data and data['timestamp']:
            session_id = md_file.stem.replace('session-', '')
            all_chapters.append({
                'timestamp': data['timestamp'],
                'session_id': session_id,
                'data': data,
                'source': 'md'
            })
            print(f"   ✅ {data['timestamp']} — {session_id}")

    # 2. Load JSONL sessions
    jsonl_files = list(SESSIONS_DIR.rglob("*.jsonl"))
    main_sessions = [f for f in jsonl_files if '/subagents/' not in str(f)]

    print(f"\n💾 Found {len(main_sessions)} JSONL sessions")

    for jsonl_file in main_sessions:
        data = extract_jsonl_session(jsonl_file)
        if data and data['timestamp']:
            session_id = jsonl_file.stem[:8]
            # Check if this session already exists in markdown
            exists = any(ch['timestamp'] == data['timestamp'] and ch['session_id'].startswith(session_id) for ch in all_chapters)
            if not exists:
                all_chapters.append({
                    'timestamp': data['timestamp'],
                    'session_id': session_id,
                    'data': data,
                    'source': 'jsonl'
                })
                print(f"   ✅ {data['timestamp']} — {session_id}")

    # 3. Sort by timestamp
    all_chapters.sort(key=lambda x: x['timestamp'])

    print(f"\n📊 Total: {len(all_chapters)} chapters\n")

    # 4. Generate HTML
    chapters_html = []
    for idx, chapter in enumerate(all_chapters, 1):
        html = generate_chapter_html(idx, chapter['session_id'], chapter['data'])
        chapters_html.append(html)
        print(f"   [{idx:2d}] {chapter['timestamp']} — {chapter['session_id']} ({chapter['source']})")

    chapters_section = "\n".join(chapters_html)

    # Get date range
    first_date = all_chapters[0]['timestamp'] if all_chapters else "—"
    last_date = all_chapters[-1]['timestamp'] if all_chapters else "—"

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
      <div>📊 {len(all_chapters)} Chapters</div>
      <div>🔄 Real Sessions</div>
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

    print(f"\n✅ Generated {len(all_chapters)} REAL chapters")
    print(f"📁 {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
