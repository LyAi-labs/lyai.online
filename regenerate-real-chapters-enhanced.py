#!/usr/bin/env python3
"""
Generate REAL chapters from JSONL sessions with actual work summaries.
Extracts: session title, user prompts, key accomplishments, commits, changes.
"""

import json
import re
from pathlib import Path
from datetime import datetime

SESSIONS_DIR = Path("/home/lyai/.claude/projects")
OUTPUT_FILE = Path("/var/www/lyai.online/index.html")

def analyze_session_content(jsonl_file):
    """Extract real work summaries from JSONL conversation."""
    try:
        with open(jsonl_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        title = None
        first_user_msg = None
        work_items = []
        commits = []
        files_changed = []
        errors_fixed = []
        tools_used = set()
        timestamp = None

        for line in lines:
            try:
                msg = json.loads(line.strip())
                msg_type = msg.get('type', '')
                ts = msg.get('timestamp', '')

                if ts and not timestamp:
                    timestamp = ts[:10]

                # Extract session title
                if msg_type == 'ai-title' and not title:
                    title = msg.get('aiTitle', '')

                # Extract first user message
                if msg_type == 'user' and not first_user_msg:
                    user_msg = msg.get('message', '')
                    if user_msg and len(user_msg) > 20:
                        first_user_msg = user_msg[:150]

                # Extract work from assistant messages
                if msg_type == 'assistant':
                    content = msg.get('message', '')

                    # Look for commits
                    commit_matches = re.findall(r'commit\s+([a-f0-9]{7,})', content, re.I)
                    commits.extend(commit_matches[:1])

                    # Look for file changes
                    file_matches = re.findall(r'(src/\S+|app/\S+|[a-zA-Z0-9_\-./]+\.(py|js|jsx|tsx|sql|yml))\b', content)
                    files_changed.extend([f[0] if isinstance(f, tuple) else f for f in file_matches[:3]])

                    # Look for errors fixed
                    if any(kw in content.lower() for kw in ['fixed', 'error', 'bug', 'issue']):
                        error_match = re.search(r'(fixed|error|bug).*?([a-z\s]{10,80}?)[\n.]', content, re.I)
                        if error_match:
                            errors_fixed.append(error_match.group(2).strip()[:60])

                    # Track key accomplishments
                    if any(kw in content.lower() for kw in ['created', 'implemented', 'deployed', 'added', 'completed']):
                        work_items.append('✓ ' + (content.split('\n')[0][:60]))

            except json.JSONDecodeError:
                continue

        # Build summary
        summary = []

        if title:
            summary.append(f"📝 {title}")

        if commits:
            summary.append(f"💾 {len(commits)} commit{'s' if len(commits) > 1 else ''}")

        if files_changed:
            unique_files = list(set(files_changed))[:2]
            summary.append(f"📄 {', '.join(unique_files)}")

        if errors_fixed:
            summary.append(f"🐛 Fixed: {errors_fixed[0]}")

        if first_user_msg and not summary:
            summary.append(first_user_msg[:80])

        description = " • ".join(summary) if summary else "Development session"

        return {
            'title': title or "Development Work",
            'description': description,
            'timestamp': timestamp,
            'commits': len(commits),
            'files': len(set(files_changed)),
            'work_items': len(work_items)
        }
    except Exception as e:
        return None

def generate_chapter_html(idx, session_id, data):
    """Generate HTML for a single chapter."""
    colors = ["#60a5fa", "#fb923c", "#34d399", "#f472b6", "#fbbf24", "#ec4899"]
    color = colors[idx % len(colors)]

    html = f'''
    <div class="chapter" style="border-left: 4px solid {color}; padding-left: 16px; margin-bottom: 24px;">
      <div style="display: flex; align-items: baseline; gap: 12px; margin-bottom: 8px;">
        <span style="font-size: 2rem; font-weight: 600; color: {color};">#{idx:02d}</span>
        <span style="font-family: 'JetBrains Mono'; font-size: 0.85rem; color: #9ea3b0;">{data['timestamp'] or '2026-04-22'}</span>
        <span style="font-family: 'JetBrains Mono'; font-size: 0.75rem; color: #4b5563; margin-left: auto;">{session_id}</span>
      </div>
      <p style="font-size: 0.95rem; color: #f5f4ef; margin: 0; line-height: 1.5;">
        {data['description']}
      </p>
    </div>
    '''
    return html

def main():
    print("🔄 Generating REAL chapters from conversation content...\n")

    # Find all JSONL files
    jsonl_files = list(SESSIONS_DIR.glob("**/*.jsonl"))
    main_sessions = [f for f in jsonl_files if '/subagents/' not in str(f)]
    main_sessions = sorted(main_sessions)

    print(f"📖 Found {len(main_sessions)} sessions\n")

    chapters_html = []
    for idx, session_file in enumerate(main_sessions, 1):
        session_id = session_file.stem[:8]
        data = analyze_session_content(session_file)

        if data:
            print(f"   ✅ {data['timestamp']} — {session_id}")
            print(f"      → {data['description'][:100]}")
            chapter = generate_chapter_html(idx, session_id, data)
            chapters_html.append(chapter)
        else:
            print(f"   ⚠️  {session_id} — could not analyze")

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
    <p class="subtitle">Mirror Protocol — Real Sessions, Real Conversations</p>
    <div class="stats">
      <div>📊 {len(chapters_html)} Chapters</div>
      <div>🔄 Content-Backed</div>
      <div>📅 Sessions 2026-04-18 to 2026-04-22</div>
    </div>
  </header>

  <div class="chapters">
{chapters_section}
  </div>
</body>
</html>'''

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"\n✅ Generated {len(chapters_html)} REAL chapters with conversation content")
    print(f"📁 File: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
