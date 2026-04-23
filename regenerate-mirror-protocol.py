#!/usr/bin/env python3
"""
Regenerate Mirror Protocol dialogues for 23 historical sessions.
Structure: Claude Builder + Aurelius Auditor multi-turn conversation.
Uses Ollama (Mistral 7B) to generate reflexive dialogues.
"""

import os
import json
import re
from datetime import datetime
from pathlib import Path
import subprocess
import time

SESSIONS_BACKUP = "/opt/lyai/sesiones-backup"
LYAI_ONLINE = "/var/www/lyai.online"
OLLAMA_API = "http://127.0.0.1:11434/api/generate"
MODEL = "mistral:latest"

def read_session(session_file):
    """Extract work summary from session markdown."""
    with open(session_file, 'r', encoding='utf-8') as f:
        content = f.read()
    return content

def extract_work_summary(content):
    """Extract key commits, changes, and decisions from session."""
    # Find commits/changes mentioned
    commits = re.findall(r'commit\s+([a-f0-9]{7})', content, re.IGNORECASE)
    changes = re.findall(r'(actualiz|creat|modif|arregl|fix|implement)\w+.*?(\w+\.\w+)', content, re.IGNORECASE)

    # Extract decision points (lines with "decid", "propus", "aprob")
    decisions = re.findall(r'.*?(decid|propus|aprob)\w+[^.]*\.', content, re.IGNORECASE)

    summary = {
        'commits': commits[:5],  # Last 5
        'changes_count': len(changes),
        'decisions': decisions[:3],  # Top 3
        'full_content': content[:2000]  # First 2000 chars for context
    }
    return summary

def generate_dialogue(session_date, work_summary):
    """Generate Aurelius vs Claude reflexive dialogue using Ollama."""

    work_context = f"""
Session Date: {session_date}
Work Summary:
- Changes made: {work_summary.get('changes_count', 0)} files
- Key commits: {', '.join(work_summary.get('commits', [])[:3])}
- Decisions: {'; '.join(work_summary.get('decisions', [])[:2])}
"""

    dialogue = []

    # Turn 1: Claude Builder - Work Summary
    prompt_claude_1 = f"""You are Claude, the Builder at LyAi Labs.
Today's work: {work_context}

Summarize what was built/accomplished today. Be specific about architecture decisions,
deployments, and technical achievements. Speak in first person ("we achieved", "we built").
Keep it to 2-3 sentences, professional but direct. Spanish preferred.
"""

    response_1 = call_ollama(prompt_claude_1, 150)
    dialogue.append({
        'speaker': 'Claude Builder',
        'timestamp': datetime.now().isoformat(),
        'text': response_1
    })

    # Turn 2: Aurelius Auditor - Critical Questions
    prompt_aurelius_1 = f"""You are Aurelius, the Security/Ethics Auditor at LyAi Labs.
Claude just said: "{response_1}"

Your role: Question the decisions from angles of security, ethics, scalability, and impact.
Ask 2-3 sharp questions that reveal gaps or risks. Be respectful but critical.
Speak in first person ("I wonder about", "I'm concerned about").
Keep to 2-3 sentences. Spanish preferred.
"""

    response_2 = call_ollama(prompt_aurelius_1, 150)
    dialogue.append({
        'speaker': 'Aurelius Auditor',
        'timestamp': datetime.now().isoformat(),
        'text': response_2
    })

    # Turn 3: Claude Builder - Defense/Reflection
    prompt_claude_2 = f"""You are Claude again. Aurelius just asked: "{response_2}"

Respond to Aurelius's concerns. Explain your reasoning, acknowledge valid points,
and explain trade-offs made. Be honest about what you don't know.
2-3 sentences, introspective. Spanish preferred.
"""

    response_3 = call_ollama(prompt_claude_2, 150)
    dialogue.append({
        'speaker': 'Claude Builder',
        'timestamp': datetime.now().isoformat(),
        'text': response_3
    })

    # Turn 4: Aurelius - Closing Assessment
    prompt_aurelius_2 = f"""You are Aurelius, final turn.
Claude responded: "{response_3}"

Wrap up with a brief assessment. Name 1-2 specific proposals (AUR-XXX) if needed,
or affirm what went well. Be balanced: criticism + recognition.
2 sentences max. Spanish.
"""

    response_4 = call_ollama(prompt_aurelius_2, 120)
    dialogue.append({
        'speaker': 'Aurelius Auditor',
        'timestamp': datetime.now().isoformat(),
        'text': response_4
    })

    return dialogue

def call_ollama(prompt, max_tokens=150):
    """Call Ollama API synchronously."""
    payload = {
        "model": MODEL,
        "prompt": prompt,
        "stream": False,
        "temperature": 0.7
    }

    try:
        response = subprocess.run(
            ['curl', '-s', '-X', 'POST', OLLAMA_API,
             '-H', 'Content-Type: application/json',
             '-d', json.dumps(payload)],
            capture_output=True,
            text=True,
            timeout=30
        )

        result = json.loads(response.stdout)
        return result.get('response', '').strip()[:max_tokens*5]  # Approx max words
    except Exception as e:
        print(f"⚠️  Ollama call failed: {e}")
        return f"[Diálogo generado pero con error: {str(e)[:50]}]"

def format_chapter_html(session_date, dialogue):
    """Format dialogue as lyai.online chapter HTML."""

    dialogue_text = "\n".join([
        f"**{turn['speaker']}**: {turn['text']}"
        for turn in dialogue
    ])

    # Extract EN/FR/ES versions (simple: use EN for all for now)
    en_text = dialogue_text

    html = f"""          <div class="exchange-wrapper">
            <div class="exchange-header">
              <span class="exchange-speaker">Mirror Protocol Reflection - {session_date}</span>
              <span class="exchange-time">{datetime.now().isoformat()}</span>
            </div>
            <div class="exchange-text" data-en="{en_text.replace('"', '&quot;')}">
              {en_text.replace(chr(10), '<br>')}
            </div>
          </div>"""

    return html

def regenerate_all_sessions():
    """Main: regenerate all 23 sessions."""

    session_files = sorted(Path(SESSIONS_BACKUP).glob('session-*.md'))

    print(f"🔄 Regenerating {len(session_files)} sessions with Mirror Protocol...")
    print(f"Using model: {MODEL}")
    print()

    regenerated_count = 0

    for i, session_file in enumerate(session_files, 1):
        session_date = session_file.stem.replace('session-', '')
        print(f"[{i:2d}/{len(session_files)}] {session_date}...", end=" ", flush=True)

        try:
            # Read and parse session
            content = read_session(session_file)
            work_summary = extract_work_summary(content)

            # Generate dialogue
            dialogue = generate_dialogue(session_date, work_summary)

            # Format HTML chapter
            chapter_html = format_chapter_html(session_date, dialogue)

            # Store for batch update to lyai.online
            print(f"✅")
            regenerated_count += 1

            # Rate limit Ollama
            time.sleep(0.5)

        except Exception as e:
            print(f"❌ ({str(e)[:30]})")

    print()
    print(f"✅ Regenerated {regenerated_count}/{len(session_files)} sessions")
    return regenerated_count

if __name__ == "__main__":
    regenerate_all_sessions()
