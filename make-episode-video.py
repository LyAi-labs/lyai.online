#!/usr/bin/env python3
"""Ensambla el VÍDEO de un episodio: clips de la librería + audio Gemini + subtítulos.

Uso: make-episode-video.py N [--send]
Lee:  /var/www/lyai.online/audio/ep-NNN.json   (manifest de turnos: speaker,text,dur)
      /var/www/lyai.online/audio/ep-NNN.mp3     (audio)
      $CLIPS_DIR/<id>.mp4                         (biblioteca de clips, shot-list)
Sale: /var/www/lyai.online/video/ep-NNN.mp4

Si falta un clip, usa un PLACEHOLDER (fondo + nombre + 'clip pendiente') para que el
pipeline corra end-to-end igual. Así se prueba antes de tener la librería.
"""
import sys, os, json, subprocess, textwrap

AUDIO_DIR = "/var/www/lyai.online/audio"
VIDEO_DIR = "/var/www/lyai.online/video"
CLIPS_DIR = os.environ.get("CLIPS_DIR", "/opt/lyai/app/lyai-ski/docs/Episodios Videos")
W, H, FPS = 1280, 720, 24
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
sys.path.insert(0, "/opt/lyai/app/lyai-tg-bridge")

NAME = {"Claude": "CLAUDE", "Aurelius": "AURELIUS", "HORCA-Core": "HORCA", "HORCA": "HORCA"}
COLOR = {"Claude": "0x60a5fa", "Aurelius": "0xfb923c", "HORCA-Core": "0x34d399", "HORCA": "0x34d399"}
SPEAKER_CLIPS = {
    "Claude": ["claude-talk-1", "claude-talk-2"],
    "Aurelius": ["aurelius-talk-1", "aurelius-talk-2"],
    "HORCA-Core": ["horca-talk-1", "horca-talk-2"],
    "HORCA": ["horca-talk-1", "horca-talk-2"],
}


def clip_for(speaker, counter):
    ids = SPEAKER_CLIPS.get(speaker, ["establishing"])
    for off in range(len(ids)):
        cid = ids[(counter + off) % len(ids)]
        p = f"{CLIPS_DIR}/{cid}.mp4"
        if os.path.exists(p):
            return p
    # fallback genérico
    for cid in ("establishing", ids[0]):
        p = f"{CLIPS_DIR}/{cid}.mp4"
        if os.path.exists(p):
            return p
    return None


def esc(t):
    return t.replace("\\", "").replace(":", "\\:").replace("'", "")


def drawtexts(speaker, text, subfile):
    name = NAME.get(speaker, speaker)
    col = COLOR.get(speaker, "0xffffff")
    wrapped = "\n".join(textwrap.wrap(text, 46)) or " "
    with open(subfile, "w", encoding="utf-8") as f:
        f.write(wrapped)
    nm = (f"drawtext=fontfile={FONT}:text='{esc(name)}':fontcolor={col}:fontsize=26:"
          f"box=1:boxcolor=black@0.45:boxborderw=10:x=40:y=h-180")
    sub = (f"drawtext=fontfile={FONT}:textfile={subfile}:fontcolor=white:fontsize=32:"
           f"box=1:boxcolor=black@0.55:boxborderw=16:x=(w-text_w)/2:y=h-text_h-48:line_spacing=8")
    return nm + "," + sub


def make_segment(turn, idx, counters, segdir):
    sp, text, dur = turn["speaker"], turn["text"], max(0.8, turn["dur"])
    subfile = f"{segdir}/sub{idx:03d}.txt"
    dt = drawtexts(sp, text, subfile)
    seg = f"{segdir}/seg{idx:03d}.mp4"
    clip = clip_for(sp, counters.get(sp, 0))
    counters[sp] = counters.get(sp, 0) + 1
    common_vf = f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},fps={FPS}"
    if clip:
        vf = f"{common_vf},{dt}"
        cmd = ["ffmpeg", "-stream_loop", "-1", "-i", clip, "-t", f"{dur:.3f}",
               "-vf", vf, "-an", "-r", str(FPS), "-c:v", "libx264", "-pix_fmt", "yuv420p",
               "-preset", "veryfast", seg, "-y", "-loglevel", "error"]
    else:
        pend = (f"drawtext=fontfile={FONT}:text='clip pendiente':fontcolor=0x4b5563:"
                f"fontsize=22:x=(w-text_w)/2:y=120")
        vf = f"fps={FPS},{dt},{pend}"
        cmd = ["ffmpeg", "-f", "lavfi", "-i", f"color=c=0x0b0e14:s={W}x{H}:d={dur:.3f}:r={FPS}",
               "-vf", vf, "-an", "-c:v", "libx264", "-pix_fmt", "yuv420p",
               "-preset", "veryfast", seg, "-y", "-loglevel", "error"]
    subprocess.run(cmd, check=True)
    return seg, bool(clip)


def encode_extra(path, segdir, tag):
    """Normaliza intro/outro a canvas."""
    out = f"{segdir}/{tag}.mp4"
    subprocess.run(["ffmpeg", "-i", path, "-vf",
                    f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},fps={FPS}",
                    "-an", "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "veryfast",
                    out, "-y", "-loglevel", "error"], check=True)
    return out


def main():
    args = sys.argv[1:]
    if not args or not args[0].isdigit():
        print("uso: make-episode-video.py N [--send]"); sys.exit(1)
    ep = int(args[0])
    send = "--send" in args
    man_path = f"{AUDIO_DIR}/ep-{ep:03d}.json"
    audio = f"{AUDIO_DIR}/ep-{ep:03d}.mp3"
    if not os.path.exists(man_path) or not os.path.exists(audio):
        print(f"falta manifest/audio de ep-{ep:03d} (regenera el audio para crear el .json)"); sys.exit(2)
    man = json.load(open(man_path, encoding="utf-8"))
    turns = man["turns"]
    os.makedirs(VIDEO_DIR, exist_ok=True)
    segdir = f"/tmp/vid-ep{ep:03d}"
    os.makedirs(segdir, exist_ok=True)

    segs, counters, have = [], {}, 0
    if os.path.exists(f"{CLIPS_DIR}/intro-title.mp4"):
        segs.append(encode_extra(f"{CLIPS_DIR}/intro-title.mp4", segdir, "intro"))
    for idx, t in enumerate(turns):
        seg, ok = make_segment(t, idx, counters, segdir)
        segs.append(seg)
        have += ok
        print(f"  turno {idx+1}/{len(turns)} {t['speaker']} {t['dur']}s {'clip' if ok else 'placeholder'}", flush=True)
    if os.path.exists(f"{CLIPS_DIR}/outro.mp4"):
        segs.append(encode_extra(f"{CLIPS_DIR}/outro.mp4", segdir, "outro"))

    listf = f"{segdir}/list.txt"
    with open(listf, "w") as lf:
        for s in segs:
            lf.write(f"file '{s}'\n")
    silent = f"{segdir}/silent.mp4"
    subprocess.run(["ffmpeg", "-f", "concat", "-safe", "0", "-i", listf,
                    "-c", "copy", silent, "-y", "-loglevel", "error"], check=True)

    out = f"{VIDEO_DIR}/ep-{ep:03d}.mp4"
    subprocess.run(["ffmpeg", "-i", silent, "-i", audio, "-map", "0:v", "-map", "1:a",
                    "-c:v", "copy", "-c:a", "aac", "-b:a", "160k", "-shortest",
                    out, "-y", "-loglevel", "error"], check=True)
    subprocess.run(["rm", "-rf", segdir])
    dur = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                          "-of", "default=nw=1:nk=1", out], capture_output=True, text=True).stdout.strip()
    print(f"  -> {out} · {os.path.getsize(out)//1024//1024}MB · {dur}s · clips={have}/{len(turns)}", flush=True)

    if send:
        import bridge
        with open(out, "rb") as fh:
            r = bridge.requests.post(f"{bridge.API}/sendVideo",
                data={"chat_id": bridge.ALLOWED_CHAT_ID,
                      "caption": f"🎬 Vídeo ep-{ep:03d} · clips reales {have}/{len(turns)}"
                                 + ("" if have == len(turns) else " (resto placeholder)")},
                files={"video": fh}, timeout=300).json()
        print("  sendVideo ok:", r.get("ok"), flush=True)


if __name__ == "__main__":
    main()
