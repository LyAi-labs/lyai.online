#!/usr/bin/env python3
"""Ensambla el VÍDEO de un episodio en MODO DIÁLOGO (Veo native: clip por turno con
voz + lip-sync propios). Concatena los clips, quema subtítulos (transcritos del propio
audio del clip con Gemini) con nombre+color del personaje, y conserva el audio del clip.

Uso: assemble-dialogue.py N [--send]
Clips esperados: $CLIPS_DIR/ep{NNN}-t{1..}.mp4  (1 por turno, en orden)
Speaker por turno: de audio/ep-NNN.json (manifest) si existe.
Salida: /var/www/lyai.online/video/ep-NNN.mp4
"""
import sys, os, re, glob, json, base64, subprocess, textwrap
sys.path.insert(0, "/opt/lyai/app/lyai-tg-bridge")
import bridge

AUDIO_DIR = "/var/www/lyai.online/audio"
VIDEO_DIR = "/var/www/lyai.online/video"
CLIPS_DIR = os.environ.get("CLIPS_DIR", "/opt/lyai/app/lyai-ski/docs/Episodios Videos")
W, H, FPS = 1280, 720, 24
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
NAME = {"Claude": "CLAUDE", "Aurelius": "AURELIUS", "HORCA-Core": "HORCA", "HORCA": "HORCA"}
COLOR = {"Claude": "0x60a5fa", "Aurelius": "0xfb923c", "HORCA-Core": "0x34d399", "HORCA": "0x34d399"}


def transcribe(clip):
    """Extrae el audio del clip y lo transcribe con Gemini (subtítulo fiel)."""
    a = "/tmp/_dlg.ogg"
    subprocess.run(["ffmpeg", "-i", clip, "-vn", "-c:a", "libopus", a, "-y", "-loglevel", "error"])
    try:
        data = base64.b64encode(open(a, "rb").read()).decode()
        url = (f"https://generativelanguage.googleapis.com/v1beta/models/"
               f"{bridge.GEMINI_MODEL}:generateContent?key={bridge.GEMINI_API_KEY}")
        body = {"contents": [{"parts": [
            {"text": "Transcribe literalmente este audio. Devuelve SOLO la transcripción."},
            {"inline_data": {"mime_type": "audio/ogg", "data": data}}]}]}
        d = bridge.requests.post(url, json=body, timeout=90).json()
        return d["candidates"][0]["content"]["parts"][0]["text"].strip()
    except Exception as e:
        print("   transcribe fallo:", e); return ""


def esc(t):
    return t.replace("\\", "").replace(":", "\\:").replace("'", "")


def make_seg(clip, idx, speaker, segdir):
    sub = transcribe(clip)
    subfile = f"{segdir}/sub{idx:03d}.txt"
    with open(subfile, "w", encoding="utf-8") as f:
        f.write("\n".join(textwrap.wrap(sub, 46)) or " ")
    name = NAME.get(speaker, "")
    col = COLOR.get(speaker, "0xffffff")
    dt = (f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},fps={FPS},"
          f"drawtext=fontfile={FONT}:textfile={subfile}:fontcolor=white:fontsize=32:"
          f"box=1:boxcolor=black@0.55:boxborderw=16:x=(w-text_w)/2:y=h-text_h-48:line_spacing=8")
    if name:
        dt += (f",drawtext=fontfile={FONT}:text='{esc(name)}':fontcolor={col}:fontsize=26:"
               f"box=1:boxcolor=black@0.45:boxborderw=10:x=40:y=h-180")
    seg = f"{segdir}/seg{idx:03d}.mp4"
    subprocess.run(["ffmpeg", "-i", clip, "-vf", dt, "-r", str(FPS),
                    "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "veryfast",
                    "-c:a", "aac", "-b:a", "160k", "-ar", "48000", "-ac", "2",
                    seg, "-y", "-loglevel", "error"], check=True)
    print(f"  turno {idx} {speaker or '?'} · «{sub[:60]}»", flush=True)
    return seg


def main():
    args = sys.argv[1:]
    if not args or not args[0].isdigit():
        print("uso: assemble-dialogue.py N [--send]"); sys.exit(1)
    ep = int(args[0])
    send = "--send" in args
    clips = sorted(glob.glob(f"{CLIPS_DIR}/ep{ep:03d}-t*.mp4"),
                   key=lambda p: int(re.search(r"-t(\d+)", p).group(1)))
    if not clips:
        print(f"No hay clips ep{ep:03d}-t*.mp4 en {CLIPS_DIR}"); sys.exit(2)
    speakers = []
    mpath = f"{AUDIO_DIR}/ep-{ep:03d}.json"
    if os.path.exists(mpath):
        speakers = [t["speaker"] for t in json.load(open(mpath, encoding="utf-8"))["turns"]]
    os.makedirs(VIDEO_DIR, exist_ok=True)
    segdir = f"/tmp/dlg-ep{ep:03d}"
    os.makedirs(segdir, exist_ok=True)

    segs = []
    if os.path.exists(f"{CLIPS_DIR}/intro-title.mp4"):
        clips = [f"{CLIPS_DIR}/intro-title.mp4"] + clips
        speakers = [""] + speakers
    for i, clip in enumerate(clips):
        sp = speakers[i] if i < len(speakers) else ""
        segs.append(make_seg(clip, i, sp, segdir))

    listf = f"{segdir}/list.txt"
    with open(listf, "w") as lf:
        for s in segs:
            lf.write(f"file '{s}'\n")
    out = f"{VIDEO_DIR}/ep-{ep:03d}.mp4"
    subprocess.run(["ffmpeg", "-f", "concat", "-safe", "0", "-i", listf,
                    "-c", "copy", out, "-y", "-loglevel", "error"], check=True)
    subprocess.run(["rm", "-rf", segdir])
    dur = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                          "-of", "default=nw=1:nk=1", out], capture_output=True, text=True).stdout.strip()
    print(f"  -> {out} · {os.path.getsize(out)//1024//1024}MB · {dur}s · {len(clips)} clips", flush=True)
    if send:
        with open(out, "rb") as fh:
            r = bridge.requests.post(f"{bridge.API}/sendVideo",
                data={"chat_id": bridge.ALLOWED_CHAT_ID,
                      "caption": f"🎬 ep-{ep:03d} · MODO DIÁLOGO (Veo voz+lip-sync nativo) · {len(clips)} clips"},
                files={"video": fh}, timeout=300).json()
        print("  sendVideo ok:", r.get("ok"), flush=True)


if __name__ == "__main__":
    main()
