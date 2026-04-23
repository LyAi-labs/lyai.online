#!/usr/bin/env python3
"""
Fast Mirror Protocol regeneration using qwen2.5:1.5b model.
Generates Aurelius/Claude dialogue for 23 historical sessions.
"""

import os
import json
import re
import subprocess
from datetime import datetime
from pathlib import Path

SESSIONS_BACKUP = "/opt/lyai/sesiones-backup"
MODEL = "qwen2.5:1.5b"  # Fast, lightweight
OLLAMA_API = "http://127.0.0.1:11434/api/generate"

def call_ollama(prompt, max_retries=2):
    """Call Ollama with timeout handling."""
    payload = {
        "model": MODEL,
        "prompt": prompt,
        "stream": False,
        "temperature": 0.7
    }

    for attempt in range(max_retries):
        try:
            response = subprocess.run(
                ['curl', '-s', '-X', 'POST', OLLAMA_API,
                 '-H', 'Content-Type: application/json',
                 '-d', json.dumps(payload)],
                capture_output=True,
                text=True,
                timeout=45
            )

            result = json.loads(response.stdout)
            text = result.get('response', '').strip()
            if text:
                return text[:300]  # Limit output
        except Exception as e:
            if attempt == max_retries - 1:
                return f"[Generated reflection pending]"

    return "[Generated reflection pending]"

def extract_work_from_session(session_file):
    """Extract work summary from session."""
    try:
        with open(session_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Find commits
        commits = re.findall(r'commit\s+([a-f0-9]{7})', content, re.IGNORECASE)
        # Find changes
        changes = re.findall(r'(actualiz|creat|modif|arregl|fix|implement)\w+', content, re.IGNORECASE)

        return {
            'commits': commits[:3] if commits else [],
            'changes': len(set(changes)),
            'preview': content[:500]
        }
    except:
        return {'commits': [], 'changes': 0, 'preview': ''}

def generate_dialogue(session_date, work):
    """Generate brief Aurelius/Claude dialogue."""

    work_desc = f"{work['changes']} changes, commits: {', '.join(work['commits'][:2])}"

    # Claude Turn 1
    prompt_c1 = f"""Session {session_date}: We made {work_desc}.
Summarize briefly (1 sentence) what was accomplished. Spanish."""

    claude_1 = call_ollama(prompt_c1)

    # Aurelius Turn 1
    prompt_a1 = f"""Claude said: "{claude_1}"
As Aurelius auditor, ask 1 critical question. Spanish, 1 sentence."""

    aurelius_1 = call_ollama(prompt_a1)

    # Claude Turn 2
    prompt_c2 = f"""Aurelius asked: "{aurelius_1}"
Respond briefly to concern (1 sentence). Spanish."""

    claude_2 = call_ollama(prompt_c2)

    return [
        {"speaker": "Claude", "text": claude_1},
        {"speaker": "Aurelius", "text": aurelius_1},
        {"speaker": "Claude", "text": claude_2}
    ]

def main():
    """Regenerate all 23 sessions."""

    sessions = sorted(Path(SESSIONS_BACKUP).glob('session-*.md'))

    print(f"🚀 Regenerating {len(sessions)} sessions")
    print(f"   Model: {MODEL}")
    print(f"   Timeout: 45s per turn")
    print()

    for i, session_file in enumerate(sessions, 1):
        date = session_file.stem.replace('session-', '')
        print(f"[{i:2d}/{len(sessions)}] {date}...", end=" ", flush=True)

        try:
            work = extract_work_from_session(session_file)
            dialogue = generate_dialogue(date, work)

            # Save dialogue
            dialogue_file = f"/home/lyai/.claude/projects/-opt-lyai-app-lyai-ski/memory/dialogue_{date}.json"
            with open(dialogue_file, 'w') as f:
                json.dump(dialogue, f, ensure_ascii=False, indent=2)

            print("✅")
        except Exception as e:
            print(f"❌ {str(e)[:30]}")

    print()
    print(f"✅ Regeneration complete")
    print(f"📖 Dialogues saved to memory/dialogue_YYYY-MM-DD.json")

if __name__ == "__main__":
    main()
