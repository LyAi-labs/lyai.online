#!/usr/bin/env python3
"""
Extract REAL work summaries from JSONL sessions and generate lyai.online chapters.
No Ollama generation — pure extraction from actual conversations.
"""

import json
import re
from pathlib import Path
from datetime import datetime
from collections import defaultdict

SESSIONS_DIR = Path("/home/lyai/.claude/projects")
OUTPUT_FILE = Path("/var/www/lyai.online/index.html")

def extract_session_work(jsonl_file):
    """Extract actual work from JSONL conversation."""
    try:
        with open(jsonl_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        work_summary = {
            'commits': [],
            'changes': [],
            'commands': [],
            'files_edited': [],
            'endpoints': [],
            'errors_fixed': [],
            'conversation_snippets': []
        }

        for line in lines:
            try:
                msg = json.loads(line.strip())
                content = msg.get('content', '')

                # Extract commits
                commits = re.findall(r'commit\s+([a-f0-9]{7,})', content, re.I)
                work_summary['commits'].extend(commits)

                # Extract file changes (Python, JS, etc)
                files = re.findall(r'([a-zA-Z0-9_\-./]+\.(py|js|jsx|html|css|yml|yaml|json))', content)
                work_summary['files_edited'].extend([f[0] for f in files])

                # Extract endpoints
                endpoints = re.findall(r'/api/[\w\-/]+', content)
                work_summary['endpoints'].extend(endpoints)

                # Extract error fixes
                if 'error' in content.lower() or 'fix' in content.lower():
                    snippets = re.findall(r'(?:fix|error|problema)[^.!?]{20,100}', content, re.I)
                    work_summary['errors_fixed'].extend(snippets[:2])

                # Extract commands run
                commands = re.findall(r'(?:docker|git|npm|python3?|curl|kubectl|psql)\s+[^\n]{10,60}', content)
                work_summary['commands'].extend(commands[:3])

                # Save conversation snippets (first 150 chars of assistant messages)
                if msg.get('role') == 'assistant':
                    snippet = content[:120].replace('\n', ' ').strip()
                    if len(snippet) > 30:
                        work_summary['conversation_snippets'].append(snippet)
            except json.JSONDecodeError:
                continue

        return work_summary
    except Exception as e:
        return None

def find_session_date(jsonl_file):
    """Extract date from JSONL filename or content."""
    # Try to extract from filename
    match = re.search(r'(\d{4})-(\d{2})-(\d{2})', str(jsonl_file))
    if match:
        return f"2026-{match.group(2)}-{match.group(3)}"

    # Fallback: read first message for timestamp
    try:
        with open(jsonl_file, 'r') as f:
            first_line = f.readline()
            if first_line:
                msg = json.loads(first_line)
                ts = msg.get('timestamp', '')
                if ts:
                    return ts[:10]
    except:
        pass

    return "2026-04-22"

def generate_chapter_html(idx, date, work):
    """Generate HTML for a single chapter."""

    # Build description
    description_parts = []

    if work['files_edited']:
        unique_files = set(work['files_edited'][:5])
        description_parts.append(f"Modified: {', '.join(unique_files)}")

    if work['endpoints']:
        unique_endpoints = set(work['endpoints'][:3])
        description_parts.append(f"APIs: {', '.join(unique_endpoints)}")

    if work['errors_fixed']:
        description_parts.append(f"Fixed: {work['errors_fixed'][0][:80]}")

    description = " • ".join(description_parts) if description_parts else "Development work"

    # Get color
    colors = ["#60a5fa", "#fb923c", "#34d399", "#f472b6", "#fbbf24"]
    color = colors[idx % len(colors)]

    html = f'''
    <div class="chapter" style="border-left: 4px solid {color}; padding-left: 16px;">
      <div style="display: flex; align-items: baseline; gap: 12px; margin-bottom: 8px;">
        <span style="font-size: 2rem; font-weight: 600; color: {color};">#{idx:02d}</span>
        <span style="font-family: 'JetBrains Mono'; font-size: 0.85rem; color: #9ea3b0;">{date}</span>
      </div>
      <p style="font-size: 0.95rem; color: #f5f4ef; margin: 0; line-height: 1.5;">
        {description}
      </p>
      <div style="margin-top: 12px; font-size: 0.8rem; color: #4b5563;">
        {len(work['commits'])} commits • {len(work['files_edited'])} files • {len(work['endpoints'])} endpoints
      </div>
    </div>
    '''
    return html

def main():
    print("🔄 Regenerating lyai.online with REAL chapters from JSONL sessions...\n")

    # Collect all JSONL files
    jsonl_files = list(SESSIONS_DIR.glob("**/*.jsonl"))
    # Filter out subagents (only main sessions)
    main_sessions = [f for f in jsonl_files if '/subagents/' not in str(f)]
    main_sessions = sorted(main_sessions)[:50]  # Limit to 50

    print(f"📖 Found {len(main_sessions)} sessions\n")

    chapters = []
    for idx, session_file in enumerate(main_sessions, 1):
        date = find_session_date(session_file)
        work = extract_session_work(session_file)

        if work:
            print(f"   ✅ {date} — {len(work['files_edited'])} files, {len(work['commits'])} commits")
            chapter_html = generate_chapter_html(idx, date, work)
            chapters.append((date, chapter_html))

    # Generate HTML
    chapters_section = "\n".join([ch[1] for ch in sorted(chapters)])

    html_template = f'''<!DOCTYPE html>
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
      padding: 40px 20px;
    }}

    header {{
      max-width: 1200px;
      margin: 0 auto 60px;
      border-bottom: 1px solid rgba(255,255,255,0.1);
      padding-bottom: 40px;
    }}

    h1 {{
      font-size: 3rem;
      font-weight: 600;
      margin-bottom: 12px;
      background: linear-gradient(135deg, #60a5fa, #fb923c);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }}

    .subtitle {{
      font-size: 1.1rem;
      color: #9ea3b0;
      margin-bottom: 20px;
    }}

    .stats {{
      display: flex;
      gap: 40px;
      font-family: 'JetBrains Mono';
      font-size: 0.9rem;
    }}

    .chapters {{
      max-width: 1200px;
      margin: 0 auto;
      display: grid;
      gap: 32px;
    }}

    .chapter {{
      background: rgba(18, 24, 34, 0.8);
      padding: 20px;
      border-radius: 8px;
      backdrop-filter: blur(16px);
    }}

    .chapter:hover {{
      background: rgba(18, 24, 34, 1);
    }}
  </style>
</head>
<body>
  <header>
    <h1>Inuk Agents Therapy</h1>
    <p class="subtitle">Mirror Protocol — Real work, real conversations</p>
    <div class="stats">
      <div>📊 {len(chapters)} Chapters</div>
      <div>📅 2026-03-14 to 2026-04-22</div>
      <div>🔄 Mirror Protocol Active</div>
    </div>
  </header>

  <div class="chapters">
{chapters_section}
  </div>
</body>
</html>'''

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(html_template)

    print(f"\n✅ Regenerated lyai.online with {len(chapters)} REAL chapters")
    print(f"📁 File: {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
