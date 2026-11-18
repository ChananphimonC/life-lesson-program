"""One narrator, few long Gemini requests, consistent voice (docs/REQUIREMENTS.md FR-11).

    python voice_story.py <story_dir> <script.json> <prefix> synth [Voice]   # one Gemini TTS request per chunk (script["chunks"]), voice default Fenrir
    python voice_story.py <story_dir> <script.json> <prefix> match            # equalise pitch (F0) and loudness across chunks
    python voice_story.py <story_dir> <script.json> <prefix> split            # cut the chunks into one wav per scene (audio/r<N>.wav) + audio/timing.json
    python voice_story.py <story_dir> <script.json> <prefix> marks            # when each beat phrase of each scene starts -> audio/marks.json
    python voice_story.py <story_dir> <script.json> <prefix> check            # transcribe every chunk back and compare with the script

Gemini free tier: 10 TTS requests/day (gemini_guard). Every chunk is cached by the shorts pipeline, so nothing is voiced twice.
"""
import difflib
import importlib
import json
import re
import shutil
import subprocess
import sys
import time
import wave
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
EXP = HERE.parents[2]
sys.path.insert(0, str(EXP / "shorts"))
sys.path.insert(0, str(EXP.parent / "src"))
sys.path.insert(0, str(HERE))

story, script, prefix, cmd = sys.argv[1:5]
VOICE = sys.argv[5] if len(sys.argv) > 5 else "Fenrir"
ROOT = HERE / story
AUD = ROOT / "audio"
AUD.mkdir(exist_ok=True)
doc = json.loads((ROOT / script).read_text(encoding="utf-8"))
texts = [" ".join(l["text"] for l in s["lines"]) for s in doc["scenes"]]
chunks = doc["chunks"]
SR = 24000
CACHE_ID = f"{doc['id']}_v{doc.get('version', 1)}"


def read(p):
    with wave.open(str(p), "rb") as w:
        return np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32) / 32768.0, w.getframerate()


def write(p, x):
    with wave.open(str(p), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((np.clip(x, -1, 1) * 32767).astype(np.int16).tobytes())


def f0_median(x, sr=SR):
    out, win = [], int(sr * 0.04)
    xi = x * 32768
    for i in range(0, len(xi) - win * 2, win):
        seg = xi[i:i + win * 2] - xi[i:i + win * 2].mean()
        if np.sqrt((seg ** 2).mean()) < 600:
            continue
        ac = np.correlate(seg, seg, "full")[len(seg) - 1:]
        lo, hi = int(sr / 400), int(sr / 70)
        k = lo + np.argmax(ac[lo:hi])
        if ac[k] / ac[0] > 0.35:
            out.append(sr / k)
    return float(np.median(out)), float(np.std(out))


def speech_rms(x):
    win = SR // 20
    r = np.array([np.sqrt(np.mean(x[i:i + win] ** 2)) for i in range(0, len(x) - win, win)])
    return float(np.sqrt(np.mean(r[r > 0.02] ** 2))) if (r > 0.02).any() else 0.05


if cmd == "synth":
    import tts
    from life_lesson.config import get_settings
    settings = get_settings()
    char = {"id": f"narrator_{VOICE.lower()}", "voice": {"gemini": VOICE, "edge": "th-TH-NiwatNeural", "edge_pitch": "+0Hz", "edge_rate": "+0%"}}
    for ci, scenes in enumerate(chunks, 1):
        text = " ".join(texts[s - 1] for s in scenes)
        try:
            if doc.get("voices"):                                    # dialogue story: one request per scene, two voices (multi_tts)
                import multi_tts
                sc = doc["scenes"][scenes[0] - 1]
                path, eng = multi_tts.dialogue(settings, CACHE_ID, ci, sc["lines"], doc["voices"], sc.get("direction", doc.get("style", "")))
            else:
                path, eng = tts.synth_line(settings, CACHE_ID, ci, char, f"{doc['style']}: {text}", mode="gemini")
        except Exception as exc:  # noqa: BLE001
            print(f"chunk {ci}: FAILED {str(exc)[:200]}", flush=True)
            continue
        shutil.copyfile(path, AUD / f"chunk{ci}_raw.wav")
        x, sr = read(path)
        print(f"chunk {ci}: {eng} scenes {scenes} {len(x) / sr:.1f}s ({len(text) / (len(x) / sr):.1f} chars/s)", flush=True)

elif cmd == "match":
    info = []
    for ci in range(1, len(chunks) + 1):
        x, _ = read(AUD / f"chunk{ci}_raw.wav")
        f0, sd = f0_median(x)
        info.append((ci, f0, sd, speech_rms(x), len(x) / SR))
        print(f"chunk {ci}: F0 median {f0:.0f} Hz (std {sd:.0f}), speech rms {info[-1][3]:.3f}, {info[-1][4]:.1f}s")
    target_f0 = float(__import__("os").environ.get("VOICE_F0") or np.median([i[1] for i in info]))
    print("target F0", target_f0)
    target_rms = float(np.median([i[3] for i in info]))
    for ci, f0, sd, rms, dur in info:
        raw = AUD / f"chunk{ci}_raw.wav"
        out = AUD / f"chunk{ci}.wav"
        r = target_f0 / f0
        if abs(r - 1) > 0.04 and not doc.get("voices"):                  # dialogue stories keep every voice at its own pitch (only loudness is levelled)
            subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(raw), "-af", f"asetrate={SR * r:.1f},aresample={SR},atempo={1 / r:.5f}", str(out)], check=True)
            print(f"chunk {ci}: pitch shifted by {r:.3f}")
        else:
            shutil.copyfile(raw, out)
        x, _ = read(out)
        g = target_rms / max(1e-4, speech_rms(x))
        write(out, x * g)
        # optional "more masculine" finish (no extra TTS quota): VOICE_RATIO=0.84 lowers pitch and formants without changing speed, VOICE_EQ=1 adds low-end body,
        # takes some nasal mid out and tames the top
        ratio = float(__import__("os").environ.get("VOICE_RATIO", "1"))
        if ratio != 1.0 or __import__("os").environ.get("VOICE_EQ") == "1":
            tmp = AUD / f"chunk{ci}_fx.wav"
            af = []
            if ratio != 1.0:
                af += [f"asetrate={SR * ratio:.1f}", f"aresample={SR}", f"atempo={1 / ratio:.5f}"]
            if __import__("os").environ.get("VOICE_EQ") == "1":
                af += ["bass=g=5:f=140:w=0.8", "equalizer=f=1000:t=q:w=1.1:g=-3.5", "equalizer=f=2600:t=q:w=1:g=-2", "acompressor=threshold=-24dB:ratio=2:attack=10:release=200"]
            subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", str(out), "-af", ",".join(af), str(tmp)], check=True)
            x3, _ = read(tmp)
            write(out, x3 * (target_rms / max(1e-4, speech_rms(x3))))
            tmp.unlink()
            print(f"chunk {ci}: voice fx applied (ratio {ratio}, eq {__import__('os').environ.get('VOICE_EQ')})")
        x2, _ = read(out)
        print(f"chunk {ci}: now F0 {f0_median(x2)[0]:.0f} Hz, speech rms {speech_rms(x2):.3f} (gain {g:.2f})")

elif cmd == "split":
    from google import genai
    from google.genai import types
    import gemini_guard
    from life_lesson.config import get_settings
    s = get_settings()
    client = genai.Client(api_key=s.gemini_api_key)
    timing = {}
    for ci, scenes in enumerate(chunks, 1):
        wavp = AUD / f"chunk{ci}.wav"
        x, _ = read(wavp)
        d = len(x) / SR
        p = subprocess.run(["ffmpeg", "-i", str(wavp), "-af", "silencedetect=noise=-30dB:d=0.10", "-f", "null", "-"], capture_output=True, text=True).stderr
        st = [float(v) for v in re.findall(r"silence_start: ([\d.]+)", p)]
        en = [float(v) for v in re.findall(r"silence_end: ([\d.]+)", p)]
        ends = [(a, b) for a, b in zip(st, en) if a > 0.3 and b < d - 0.3]
        starts = {scenes[0]: 0.0}
        tot = sum(len(texts[q - 1]) for q in scenes)
        for sn in scenes[1:]:
            head = texts[sn - 1][:28]
            est = d * sum(len(texts[q - 1]) for q in scenes[:scenes.index(sn)]) / tot          # proportional guess, only used to choose a 60 s window
            wa, wb = max(0.0, est - 30), min(d, est + 30)
            clip = AUD / "_clip.wav"
            subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", f"{wa:.2f}", "-t", f"{wb - wa:.2f}", "-i", str(wavp), "-ar", str(SR), "-ac", "1", str(clip)], check=True)
            prompt = ("นี่คือเสียงผู้เล่าเรื่องภาษาไทยความยาว {w:.1f} วินาที ผู้พูดเริ่มพูดวลี '{h}' ที่วินาทีเท่าไหร่นับจากต้นคลิปนี้ (ทศนิยม 1 ตำแหน่ง) "
                      "ถ้าไม่มีวลีนี้ในคลิปให้ตอบ -1 ตอบเป็น JSON ล้วนในรูป {{\"seconds\": ตัวเลข}}").format(w=wb - wa, h=head)
            res = None
            for attempt in range(3):
                try:
                    resp = gemini_guard.guarded("text", lambda: client.models.generate_content(
                        model=s.gemini_script_model, contents=[types.Part.from_bytes(data=clip.read_bytes(), mime_type="audio/wav"), prompt],
                        config=types.GenerateContentConfig(response_mime_type="application/json")))
                    res = float(json.loads(resp.text)["seconds"])
                    break
                except Exception as exc:  # noqa: BLE001
                    print("   locate retry:", str(exc)[:80])
                    time.sleep(3)
            got = wa + res if (res is not None and res >= 0) else None
            if got is None or abs(got - est) > 28:
                print(f"   scene {sn}: model answer unusable ({res}); using the proportional guess {est:.1f}s")
                got = est
            near = min(ends, key=lambda ab: abs(ab[1] - got)) if ends else (got, got)
            starts[sn] = near[1] if abs(near[1] - got) < 1.2 else got
            print(f"   scene {sn} starts at {starts[sn]:.1f}s (guess {est:.1f}, model {got:.1f})")
        bounds = [starts[sn] for sn in scenes] + [d]
        for j, sn in enumerate(scenes):
            a = max(0.0, bounds[j] - (0.0 if j == 0 else 0.12))
            b = min(d, bounds[j + 1] - 0.12) if j + 1 < len(scenes) else d
            seg = x[int(a * SR):int(b * SR)]
            write(AUD / f"r{sn}.wav", seg)
            print(f"scene {sn}: {len(seg) / SR:.1f}s (chunk {ci} {a:.1f}-{b:.1f})")
    for sn in range(1, len(texts) + 1):
        f = AUD / f"r{sn}.wav"
        x, _ = read(f)
        d = len(x) / SR
        p = subprocess.run(["ffmpeg", "-i", str(f), "-af", "silencedetect=noise=-30dB:d=0.10", "-f", "null", "-"], capture_output=True, text=True).stderr
        st = [float(v) for v in re.findall(r"silence_start: ([\d.]+)", p)]
        en = [float(v) for v in re.findall(r"silence_end: ([\d.]+)", p)]
        timing[str(sn)] = dict(dur=round(d, 2), pauses=[round(b, 2) for a, b in zip(st, en) if a > 0.3 and b < d - 0.3])
    (AUD / "timing.json").write_text(json.dumps(timing, indent=1), encoding="utf-8")
    print("timing.json written", {k: v["dur"] for k, v in timing.items()})

elif cmd == "marks":
    from google import genai
    from google.genai import types
    import gemini_guard
    from life_lesson.config import get_settings
    s = get_settings()
    client = genai.Client(api_key=s.gemini_api_key)
    timing = json.loads((AUD / "timing.json").read_text(encoding="utf-8"))
    only = {int(x) for x in __import__("os").environ.get("MARKS_ONLY", "").split(",") if x.strip()}      # MARKS_ONLY=4,5 redoes just those scenes and keeps the rest
    out = json.loads((AUD / "marks.json").read_text(encoding="utf-8")) if only and (AUD / "marks.json").is_file() else {}

    def secs(v):
        """Seconds from 12.5 or "12.5" or "0:12.5"."""
        if isinstance(v, str) and ":" in v:
            a, b = v.split(":")[-2:]
            return float(a) * 60 + float(b)
        return float(v)

    PROMPTS = [
        "นี่คือเสียงผู้เล่าเรื่องภาษาไทยความยาว {d:.1f} วินาที จงบอกว่าผู้พูดเริ่มพูดแต่ละวลีต่อไปนี้ที่วินาทีเท่าไหร่นับจากต้นไฟล์ "
        "(ทศนิยม 1 ตำแหน่ง) ตอบเป็น JSON ล้วนในรูป {{\"วลี\": วินาที}} ห้ามมีข้อความอื่น\nวลี: {ph}",
        "ไฟล์เสียงนี้ยาว {d:.1f} วินาที ผู้พูดเล่าเรื่องภาษาไทย วลีต่อไปนี้ถูกพูดตามลำดับ จงบอกเวลาเริ่มพูดของแต่ละวลีเป็น 'นาที:วินาที' เช่น 0:12.5 "
        "นับจากต้นไฟล์ (ค่าต้องเพิ่มขึ้นตามลำดับและไม่เกิน {d:.1f} วินาที) ตอบเป็น JSON ล้วน {{\"วลี\": \"นาที:วินาที\"}}\nวลี: {ph}",
    ]
    for i in range(1, len(texts) + 1):
        if only and i not in only:
            continue
        if prefix == "gs":                                   # data-driven story: the markers are the 'at' phrases of the stage beats
            markers = [b.get("at", "") for b in doc["scenes"][i - 1]["stage"][1:]]
        else:
            m = importlib.import_module(f"{prefix}{i}")
            markers = m.MARK[1:]
        if not markers:
            continue
        dur = timing[str(i)]["dur"]
        wav = (AUD / f"r{i}.wav").read_bytes()
        ends = timing[str(i)]["pauses"]
        res = {}
        all_ests = []
        for g0 in range(0, len(markers), 6):                       # a long scene is asked about in groups of six phrases: much more reliable than one list of seventeen
            group = markers[g0:g0 + 6]
            for variant in range(4):                               # a reply is accepted only when the times grow in order and stay inside the scene
                prompt = PROMPTS[min(variant, 1)].format(d=dur, ph=" | ".join(group))
                d = {}
                for attempt in range(5):                           # the model is sometimes "under high demand" (503): wait and retry
                    try:
                        resp = gemini_guard.guarded("text", lambda: client.models.generate_content(
                            model=s.gemini_script_model, contents=[types.Part.from_bytes(data=wav, mime_type="audio/wav"), prompt],
                            config=types.GenerateContentConfig(response_mime_type="application/json")))
                        d = json.loads(resp.text)
                        if isinstance(d, list):                      # sometimes a list of {phrase: time} objects or [phrase, time] pairs
                            flat = {}
                            for it in d:
                                if isinstance(it, dict):
                                    flat.update(it)
                                elif isinstance(it, (list, tuple)) and len(it) == 2:
                                    flat[str(it[0])] = it[1]
                            d = flat
                        if not isinstance(d, dict):
                            d = {}
                        break
                    except Exception as exc:  # noqa: BLE001
                        print(f"   marks scene {i}: retry {attempt + 1}/5 ({str(exc)[:70]})", flush=True)
                        time.sleep(8 * (attempt + 1))
                ests = []
                for mk in group:
                    est = None
                    best = 0
                    for k, v in d.items():
                        common = 0                                    # the key that shares the longest start with the phrase (two phrases can begin alike)
                        for a, b in zip(mk, k):
                            if a != b:
                                break
                            common += 1
                        if common >= 6 and common > best:
                            try:
                                est, best = secs(v), common
                            except (ValueError, TypeError):
                                pass
                    ests.append(est)
                good = all(e is not None and 0.5 < e < dur - 0.5 for e in ests) and all(b - a >= 1.0 for a, b in zip(ests, ests[1:]))
                if good or variant == 3:
                    break
                print(f"   marks scene {i}: implausible times {ests} (scene is {dur:.1f}s), asking again", flush=True)
            all_ests += ests
        last = 0.0
        for mk, est in zip(markers, all_ests):
            if est is None or not 0.5 < est < dur - 0.5 or est < last + 1.0:      # unusable or out of order: leave it out, the scene falls back to the text position
                continue
            last = est
            near = min(ends, key=lambda q: abs(q - est)) if ends else est
            res[mk] = dict(est=est, snapped=near if abs(near - est) <= 1.2 else est)
        out[str(i)] = res
        print(i, {k[:10]: (v["est"], v["snapped"]) for k, v in res.items()}, flush=True)
    (AUD / "marks.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")

elif cmd == "check":
    import verify_voice as V
    norm = lambda q: re.sub(r"[\s\"'“”.,!?…ๆ:;()\-]+", "", q)
    for ci, scenes in enumerate(chunks, 1):
        text = " ".join(texts[sn - 1] for sn in scenes)
        heard = V.transcribe(AUD / f"chunk{ci}_raw.wav")
        r = difflib.SequenceMatcher(None, norm(text), norm(heard)).ratio()
        style = norm(doc["style"])[:12] in norm(heard)
        print(f"chunk {ci}: similarity {r:.2f}; style read aloud: {style}\n  heard: {heard[:160]}")
