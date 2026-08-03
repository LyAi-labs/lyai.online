#!/usr/bin/env python3
"""Genera el audio multivoz de un episodio del Mirror Protocol.

Uso: make-episode-audio.py N [--send] [--force]
  N        número de episodio (ej 1)
  --send   además envía el mp3 al Telegram de Ignacio (validación)
  --force  regenera aunque el mp3 ya exista

Salida: /var/www/lyai.online/audio/ep-NNN.mp3
Voces (Gemini TTS, castellano): Claude=Puck · Aurelius=Charon · Horca=Despina.
Ritmo y emoción DINÁMICOS por línea (un 'director' los decide según el contexto).
Gratis (free tier); con fallback entre los 3 modelos TTS si uno topa cuota diaria.
"""
import sys, os, re, html, json, base64, subprocess, time
sys.path.insert(0, "/opt/lyai/app/lyai-tg-bridge")
import bridge

SRC = "/var/www/lyai.online/index.html"
AUDIO_DIR = "/var/www/lyai.online/audio"
RATE = 24000
MODELS = ["gemini-2.5-flash-preview-tts", "gemini-2.5-pro-preview-tts",
          "gemini-3.1-flash-tts-preview"]
_model_idx = [0]   # mutable: avanza si un modelo topa cuota, y se queda

BASE = ("Tono de colegas tomando unas cañas tras el curro: relajado, cercano, con humor "
        "y reacciones, entonación MUY viva, natural, nada de locutor. Si la intención "
        "indica un estado de ánimo o físico (cansado, enfermo, resfriado, triste, alegre, "
        "eufórico, decaído...), encárnalo en la voz. Acento español de España, castellano "
        "de Madrid")
PERSONA = {"Claude": "Claude, entusiasta y friki de la programación",
           "Aurelius": "Aurelius, agudo, irónico y sabio",
           "HORCA-Core": "Horca, cálida, resolutiva y con guasa",
           "HORCA": "Horca, cálida, resolutiva y con guasa"}
VOICE = {"Claude": "Puck", "Aurelius": "Charon", "HORCA-Core": "Despina", "HORCA": "Despina"}
SPK_BASE = {"Claude": 1.0, "Aurelius": 1.08, "HORCA-Core": 1.08, "HORCA": 1.08}
PACE_FACTOR = {"muy_lento": 0.88, "lento": 0.95, "normal": 1.0, "rapido": 1.10, "muy_rapido": 1.20}
PACE_WORD = {"muy_lento": "muy pausado", "lento": "pausado", "normal": "ritmo natural",
             "rapido": "rápido y ágil", "muy_rapido": "muy rápido, atropellado"}
PACE_PAUSE = {"muy_lento": 0.5, "lento": 0.42, "normal": 0.32, "rapido": 0.22, "muy_rapido": 0.18}


def parse_episode(num):
    doc = open(SRC, encoding="utf-8").read()
    m = re.search(rf'id="ep-{num:03d}"', doc)
    if not m:
        return []
    rest = doc[m.start() + 8:]
    m2 = re.search(r'id="ep-\d{3}"', rest)
    block = rest[:m2.start()] if m2 else rest
    sp = re.findall(r'speaker-name speaker-\w+">([^<]+)</span>', block)
    # tolera atributos extra (episodios antiguos: data-en/data-fr) + tags inline
    tx = re.findall(r'<div class="exchange-text"[^>]*>\s*(.*?)\s*</div>', block, re.DOTALL)
    out = []
    for s, t in zip(sp, tx):
        t = re.sub(r'<[^>]+>', '', t)                       # quita span/em inline
        t = html.unescape(re.sub(r'\s+', ' ', t)).strip()
        if t:
            out.append((s.strip(), t))
    return out


def director(turns):
    lines = "\n".join(f"{i+1}. [{s}] {t}" for i, (s, t) in enumerate(turns))
    prompt = ("Eres director de doblaje de una serie. Diálogo entre Claude, Aurelius y Horca "
              "tomando unas cañas tras el trabajo. Para CADA intervención, en orden, decide "
              "según el MOMENTO y el CONTEXTO de ese día:\n"
              "- emocion: 2-6 palabras. Usa el rango COMPLETO cuando encaje: ironía, guasa, "
              "entusiasmo, escepticismo, pique, pero también estados de ánimo o físicos si el "
              "momento lo pide (alegre, triste, melancólico, nostálgico, cansado, enfermo o "
              "resfriado, eufórico, decaído, preocupado...). No todo plano.\n"
              "- ritmo: uno de [muy_lento, lento, normal, rapido, muy_rapido]. Varíalo: "
              "reflexión seria, tristeza o cansancio=lento; pique, entusiasmo o remate=rapido. "
              "NO uses el mismo ritmo siempre.\n"
              f"Devuelve SOLO array JSON de {len(turns)} objetos {{\"emocion\":..,\"ritmo\":..}}.\n\n"
              f"Diálogo:\n{lines}")
    url = (f"https://generativelanguage.googleapis.com/v1beta/models/"
           f"{bridge.GEMINI_MODEL}:generateContent?key={bridge.GEMINI_API_KEY}")
    for attempt in range(3):
        try:
            d = bridge.requests.post(url, json={"contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"responseMimeType": "application/json"}}, timeout=120).json()
            arr = json.loads(d["candidates"][0]["content"]["parts"][0]["text"])
            out = []
            for o in arr:
                rit = str(o.get("ritmo", "normal")).lower().replace(" ", "_")
                out.append((str(o.get("emocion", "natural")), rit if rit in PACE_FACTOR else "normal"))
            while len(out) < len(turns):
                out.append(("natural", "normal"))
            return out[:len(turns)]
        except Exception as e:
            print(f"  director retry {attempt+1}: {str(e)[:80]}", flush=True)
            time.sleep(10)
    return [("natural", "normal")] * len(turns)


def tts_seg(text, voice, speaker, emo, rit, path):
    style = (f"{BASE}. Habla como {PERSONA.get(speaker,'')}. Intención: {emo}. "
             f"Ritmo: {PACE_WORD[rit]}")
    body = {"contents": [{"parts": [{"text": f"{style}. Di con esa intención y ritmo: «{text}»"}]}],
            "generationConfig": {"responseModalities": ["AUDIO"],
                "speechConfig": {"voiceConfig": {"prebuiltVoiceConfig": {"voiceName": voice}}}}}
    tries = 0
    while _model_idx[0] < len(MODELS):
        model = MODELS[_model_idx[0]]
        url = (f"https://generativelanguage.googleapis.com/v1beta/models/"
               f"{model}:generateContent?key={bridge.GEMINI_API_KEY}")
        try:
            d = bridge.requests.post(url, json=body, timeout=120).json()
            if "candidates" not in d:
                err = json.dumps(d.get("error", d))
                if "429" in err or "RESOURCE_EXHAUSTED" in err or "quota" in err.lower():
                    print(f"  {model} sin cuota -> siguiente modelo", flush=True)
                    _model_idx[0] += 1
                    continue
                raise RuntimeError(err[:90])
            pcm = base64.b64decode(d["candidates"][0]["content"]["parts"][0]["inlineData"]["data"])
            raw = path + ".raw.wav"
            with open(raw, "wb") as f:
                f.write(bridge._wav_header(len(pcm), RATE))
                f.write(pcm)
            atempo = max(0.85, min(1.4, SPK_BASE.get(speaker, 1.0) * PACE_FACTOR[rit]))
            subprocess.run(["ffmpeg", "-i", raw, "-filter:a", f"atempo={atempo:.3f}",
                            path, "-y", "-loglevel", "error"], check=True)
            os.remove(raw)
            return atempo
        except Exception as e:
            tries += 1
            if tries >= 3:
                _model_idx[0] += 1
                tries = 0
            print(f"  tts retry: {str(e)[:80]}", flush=True)
            time.sleep(8)
    return None


# ---- inyección del player en el index.html (custom, tema oscuro) ----
MP_STYLE = """  <!-- mp-assets -->
  <style>
  .mp-player{display:flex;align-items:center;gap:13px;margin:14px 0 6px;padding:10px 14px;background:#121822;border:1px solid rgba(255,255,255,.10);border-radius:13px;max-width:540px}
  .mp-play{flex:none;width:38px;height:38px;border-radius:50%;border:none;cursor:pointer;display:grid;place-items:center;background:linear-gradient(135deg,#34d399,#10b981);color:#06281d}
  .mp-body{flex:1;min-width:0}
  .mp-row{display:flex;justify-content:space-between;align-items:center;margin-bottom:6px}
  .mp-label{font-size:.78rem;font-weight:600;color:#f5f4ef}
  .mp-time{font-family:'JetBrains Mono',monospace;font-size:.68rem;color:#9ea3b0}
  .mp-track{height:5px;border-radius:3px;background:rgba(255,255,255,.08);position:relative;cursor:pointer;overflow:hidden}
  .mp-fill{position:absolute;inset:0 auto 0 0;width:0;background:linear-gradient(90deg,#34d399,#e5c158);border-radius:3px}
  </style>"""
MP_SCRIPT = """  <script>
  document.addEventListener('DOMContentLoaded',function(){
    document.querySelectorAll('.mp-player').forEach(function(p){
      var a=p.querySelector('audio'),btn=p.querySelector('.mp-play'),ico=p.querySelector('.mp-ico'),
          fill=p.querySelector('.mp-fill'),tm=p.querySelector('.mp-time'),tr=p.querySelector('.mp-track');
      function fmt(s){return isNaN(s)?'0:00':Math.floor(s/60)+':'+String(Math.floor(s%60)).padStart(2,'0');}
      btn.onclick=function(){document.querySelectorAll('.mp-player audio').forEach(function(o){if(o!==a)o.pause();});a.paused?a.play():a.pause();};
      a.onplay=function(){ico.setAttribute('d','M6 5h4v14H6zM14 5h4v14h-4z');};
      a.onpause=function(){ico.setAttribute('d','M8 5v14l11-7z');};
      a.ontimeupdate=function(){fill.style.width=(a.currentTime/(a.duration||1)*100)+'%';tm.textContent=fmt(a.currentTime)+' / '+fmt(a.duration);};
      tr.onclick=function(e){var r=tr.getBoundingClientRect();a.currentTime=((e.clientX-r.left)/r.width)*(a.duration||0);};
    });
  });
  </script>"""


def _player_block(ep):
    return ('    <div class="mp-player">\n'
            '      <button class="mp-play" aria-label="Reproducir"><svg viewBox="0 0 24 24" '
            'fill="currentColor" width="18" height="18"><path class="mp-ico" d="M8 5v14l11-7z"/></svg></button>\n'
            '      <div class="mp-body"><div class="mp-row"><span class="mp-label">Escuchar episodio</span>'
            '<span class="mp-time">0:00</span></div><div class="mp-track"><div class="mp-fill"></div></div></div>\n'
            f'      <audio preload="none" src="/audio/ep-{ep:03d}.mp3"></audio>\n'
            '    </div>')


def inject_player(ep):
    """Inyecta el player en la cabecera del episodio en index.html. Idempotente."""
    doc = open(SRC, encoding="utf-8").read()
    marker = f"<!-- mp ep-{ep:03d} -->"
    if marker in doc:
        return "ya"
    if "<!-- mp-assets -->" not in doc:
        if "</head>" in doc:
            doc = doc.replace("</head>", MP_STYLE + "\n</head>", 1)
        if "</body>" in doc:
            doc = doc.replace("</body>", MP_SCRIPT + "\n</body>", 1)
    m = re.search(rf"Daily Dialogue[^<]*Episode\s*0*{ep}\s*</div>", doc)
    if not m:
        return "sin-ancla"
    at = m.end()
    doc = doc[:at] + "\n" + marker + "\n" + _player_block(ep) + doc[at:]
    with open(SRC, "w", encoding="utf-8") as f:
        f.write(doc)
    return "ok"


def main():
    args = sys.argv[1:]
    if not args or not args[0].isdigit():
        print("uso: make-episode-audio.py N [--send] [--force] [--inject-only]"); sys.exit(1)
    ep = int(args[0])
    send = "--send" in args
    force = "--force" in args
    os.makedirs(AUDIO_DIR, exist_ok=True)
    out = f"{AUDIO_DIR}/ep-{ep:03d}.mp3"
    if "--inject-only" in args:
        print(f"ep-{ep:03d} inject-only: {inject_player(ep)}"); return
    if os.path.exists(out) and not force:
        print(f"ep-{ep:03d}: audio ya existe, skip · player: {inject_player(ep)}"); return

    turns = parse_episode(ep)
    print(f"ep-{ep:03d}: {len(turns)} turnos", flush=True)
    if not turns:
        print("  sin turnos (¿episodio inexistente?)"); sys.exit(2)
    dirs = director(turns)

    segdir = f"/tmp/segs-ep{ep:03d}"
    os.makedirs(segdir, exist_ok=True)

    def silence(dur, p):
        subprocess.run(["ffmpeg", "-f", "lavfi", "-i", f"anullsrc=r={RATE}:cl=mono",
                        "-t", str(dur), p, "-y", "-loglevel", "error"], check=True)

    listf = f"{segdir}/list.txt"
    fails = 0
    manifest = []
    cursor = 0.0
    with open(listf, "w") as lf:
        for i, (sp, tx) in enumerate(turns):
            emo, rit = dirs[i]
            seg = f"{segdir}/{i:02d}.wav"
            at = tts_seg(tx, VOICE.get(sp, "Puck"), sp, emo, rit, seg)
            print(f"  [{i+1}/{len(turns)}] {sp} {rit} · {emo} {'' if at else 'FALLO'}", flush=True)
            if at:
                sd = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                      "format=duration", "-of", "default=nw=1:nk=1", seg],
                      capture_output=True, text=True).stdout.strip()
                sd = float(sd) if sd else 0.0
                pause = PACE_PAUSE[rit]
                manifest.append({"i": i, "speaker": sp, "text": tx, "emo": emo, "rit": rit,
                                 "start": round(cursor, 3), "dur": round(sd + pause, 3)})
                cursor += sd + pause
                sil = f"{segdir}/sil{i:02d}.wav"
                silence(pause, sil)
                lf.write(f"file '{seg}'\nfile '{sil}'\n")
            else:
                fails += 1
            time.sleep(0.4)

    if fails == len(turns):
        print("  TODAS las líneas fallaron (cuota agotada en los 3 modelos). No escribo mp3.")
        subprocess.run(["rm", "-rf", segdir]); sys.exit(3)

    subprocess.run(["ffmpeg", "-f", "concat", "-safe", "0", "-i", listf,
                    "-c:a", "libmp3lame", "-b:a", "128k", out, "-y", "-loglevel", "error"], check=True)
    subprocess.run(["rm", "-rf", segdir])
    dur = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                          "-of", "default=nw=1:nk=1", out], capture_output=True, text=True).stdout.strip()
    print(f"  -> {out} · {os.path.getsize(out)//1024}KB · {dur}s · fallos={fails}/{len(turns)}", flush=True)
    with open(f"{AUDIO_DIR}/ep-{ep:03d}.json", "w", encoding="utf-8") as mf:
        json.dump({"episode": ep, "turns": manifest}, mf, ensure_ascii=False, indent=1)

    if send:
        with open(out, "rb") as fh:
            r = bridge.requests.post(f"{bridge.API}/sendAudio",
                data={"chat_id": bridge.ALLOWED_CHAT_ID,
                      "title": f"Mirror Protocol · Episodio {ep:03d}",
                      "performer": "Claude · Aurelius · Horca",
                      "caption": f"🎧 Ep {ep:03d}" + (f" · ⚠️{fails} líneas perdidas" if fails else "")},
                files={"audio": fh}, timeout=180).json()
        print("  sendAudio ok:", r.get("ok"), flush=True)

    print(f"  player inyectado: {inject_player(ep)}", flush=True)


if __name__ == "__main__":
    main()
