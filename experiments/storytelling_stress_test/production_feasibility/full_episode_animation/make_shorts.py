"""Cut vertical YouTube Shorts (1080x1920, <= 58 s) out of a finished episode: the best-hook scenes, cut at a narration pause, 16:9 picture centred over a blurred copy of itself,
a short end card "ดูตอนเต็มในช่องได้เลย". No subtitles (house rule). Also writes shorts.txt with a suggested title / description / hashtags for each clip.

    python make_shorts.py <mp4> <timing.json> [--title "ชื่อตอน"] [--texts know.json] [--n 3] [--out DIR]

Scene boundaries come from the narration timing the episode was built with (scene length = narration + 0.7 s lead + 1.0 s tail, the same constants as the story engine).
Picks (n=3): the opening scene (the hook), a scene about 40 % in, a scene about 75 % in. Edit the printed times by hand if you prefer other moments.
"""
import json
import subprocess
import sys
from pathlib import Path

LEAD, TAIL = 0.7, 1.0
MAXLEN, MINLEN = 58.0, 22.0
HERE = Path(__file__).resolve().parent


def end_card(path, line1="ดูตอนเต็มในช่องได้เลย", line2="กดติดตามไว้ ไม่พลาดตอนใหม่"):
    """A 1080x1920 transparent PNG with a rounded banner and two lines of Thai text (tone marks handled by thai_text.draw_line)."""
    sys.path.insert(0, str(HERE.parents[2] / "cartoon_storyboard"))
    from PIL import Image, ImageDraw, ImageFont
    import thai_text
    img = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((90, 1480, 990, 1700), radius=48, fill=(20, 24, 56, 215), outline=(255, 214, 90, 255), width=6)
    for text, y, size, col in ((line1, 1590, 76, (255, 244, 200)), (line2, 1660, 46, (255, 214, 90))):
        font = ImageFont.truetype("LeelaUIb.ttf", size)
        thai_text.draw_line(d, (540, y), text, font, col, anchor="ms")
    img.save(path)


def pick_scenes(n_scenes, n):
    picks = [1, max(2, round(n_scenes * 0.4)), max(3, round(n_scenes * 0.75))]
    out = []
    for p in picks[:n]:
        p = min(p, n_scenes)
        if p not in out:
            out.append(p)
    return out


def main():
    mp4 = Path(sys.argv[1])
    timing = json.loads(Path(sys.argv[2]).read_text(encoding="utf-8"))
    arg = lambda k, d=None: sys.argv[sys.argv.index(k) + 1] if k in sys.argv else d
    title = arg("--title", mp4.stem)
    n = int(arg("--n", 3))
    out = Path(arg("--out", str(mp4.parent / "shorts")))
    texts = None
    if arg("--texts"):
        doc = json.loads(Path(arg("--texts")).read_text(encoding="utf-8"))
        texts = [s["lines"][0]["text"] for s in doc["scenes"]]
    out.mkdir(parents=True, exist_ok=True)
    k_scenes = len(timing)
    starts, t = {}, 0.0
    for i in range(1, k_scenes + 1):
        starts[i] = t
        t += timing[str(i)]["dur"] + LEAD + TAIL
    card = out / "end_card.png"
    end_card(card)
    meta = []
    for idx, sc in enumerate(pick_scenes(k_scenes, n), 1):
        tm = timing[str(sc)]
        dur = tm["dur"]
        pauses = [p for p in tm.get("pauses", []) if MINLEN <= p <= MAXLEN - 3]
        rel_end = max(pauses) if pauses and dur > MAXLEN - 3 else min(dur, MAXLEN - 3)
        t0 = starts[sc] + LEAD - 0.3
        length = rel_end + 0.3 + 1.2
        dest = out / f"short_{idx}_scene{sc}.mp4"
        vf = ("[0:v]split[a][b];[a]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=28:6,eq=brightness=-0.12[bg];"
              "[b]scale=1350:-2,crop=1080:ih:(iw-1080)/2:0[fg];[bg][fg]overlay=(W-w)/2:(H-h)/2[v0];"
              f"[v0][1:v]overlay=0:0:enable='gte(t,{max(0.0, length - 3.2):.2f})'[v1];[v1]fade=t=in:d=0.25,fade=t=out:st={length - 0.3:.2f}:d=0.3[v]")
        subprocess.run(["ffmpeg", "-nostdin", "-y", "-v", "error", "-ss", f"{t0:.2f}", "-t", f"{length:.2f}", "-i", str(mp4), "-loop", "1", "-i", str(card),
                        "-filter_complex", vf, "-map", "[v]", "-map", "0:a", "-af", f"afade=t=in:d=0.2,afade=t=out:st={length - 0.4:.2f}:d=0.4",
                        "-c:v", "libx264", "-crf", "20", "-preset", "medium", "-pix_fmt", "yuv420p", "-r", "24", "-c:a", "aac", "-b:a", "160k", "-shortest", "-movflags", "+faststart", str(dest)], check=True)
        first = (texts[sc - 1].split(" ")[:14] if texts else [])
        meta.append(f"{dest.name}  ({t0:.0f}s-{t0 + length:.0f}s of the episode)\n  ชื่อเสนอ: {title} #{idx}\n  คำอธิบาย: {' '.join(first)}... ดูตอนเต็มในช่อง\n  แท็ก: #การ์ตูน #เรื่องเล่า #ตลก #shorts\n")
        print("made", dest.name, round(length, 1), "s")
    (out / "shorts.txt").write_text("\n".join(meta), encoding="utf-8")


if __name__ == "__main__":
    main()
