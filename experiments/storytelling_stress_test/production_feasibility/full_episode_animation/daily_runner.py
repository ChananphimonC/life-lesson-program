"""Overnight runner: makes ONE episode per run from the stories waiting in stories/ (each has a ready story.json, written in advance), files it in the library and appends to stories/DAILY_REPORT.md.

    python daily_runner.py              # take the next waiting story
    python daily_runner.py --dry        # only say what it would do
    python daily_runner.py --story ID   # a specific one

Why one per run: Gemini's free TTS allows ~10 requests per (Pacific) day and a 7-minute episode uses 4-6 of them; the render takes 30-60 minutes on this PC.
A story is 'waiting' when stories/<id>/story.json exists and stories/<id>/run_log.txt does not contain DONE. Order = stories/queue.txt (one id per line) then alphabetical.
Nothing is published anywhere: the episode is only filed in the local library for a human to review. Needs the PC awake and Gemini TTS quota left.
"""
import datetime
import json
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
STORIES = HERE / "stories"
REPORT = STORIES / "DAILY_REPORT.md"
LOCK = STORIES / ".runner.lock"
USAGE = HERE.parents[2] / "shorts" / "output" / "gemini_usage.json"
sys.path.insert(0, str(HERE))


def done(sid):
    lg = STORIES / sid / "run_log.txt"
    return lg.is_file() and "DONE" in lg.read_text(encoding="utf-8", errors="ignore")


def waiting():
    order = [l.strip() for l in (STORIES / "queue.txt").read_text(encoding="utf-8").splitlines() if l.strip() and not l.startswith("#")] if (STORIES / "queue.txt").is_file() else []
    allids = sorted(p.parent.name for p in STORIES.glob("*/story.json"))
    seq = [i for i in order if i in allids] + [i for i in allids if i not in order]
    return [i for i in seq if not done(i)]


def tts_left():
    try:
        from zoneinfo import ZoneInfo
        day = datetime.datetime.now(ZoneInfo("America/Los_Angeles")).strftime("%Y-%m-%d")
        used = json.loads(USAGE.read_text(encoding="utf-8")).get(day, {}).get("tts", 0)
    except Exception:  # noqa: BLE001
        used = 0
    return 10 - used


def main():
    STORIES.mkdir(exist_ok=True)
    dry = "--dry" in sys.argv
    sid = sys.argv[sys.argv.index("--story") + 1] if "--story" in sys.argv else None
    todo = waiting()
    print("waiting:", todo)
    if not todo and not sid:
        print("nothing waiting: add a stories/<id>/story.json")
        return 0
    sid = sid or todo[0]
    doc = json.loads((STORIES / sid / "story.json").read_text(encoding="utf-8"))
    need = len(doc["chunks"]) + 2                       # the chunks plus a couple of retries
    if tts_left() < need and not (STORIES / sid / "audio" / "chunk1_raw.wav").is_file():
        print(f"not enough Gemini TTS quota today ({tts_left()} left, {need} needed): try again after the Pacific-day reset")
        return 3
    if dry:
        print("would make:", sid, doc["title"])
        return 0
    if LOCK.is_file() and time.time() - LOCK.stat().st_mtime < 6 * 3600:
        print("another run is in progress")
        return 4
    LOCK.write_text(str(time.time()))
    t0 = time.time()
    try:
        p = subprocess.run([sys.executable, "-u", "auto_story.py", sid], cwd=HERE, capture_output=True, text=True, encoding="utf-8")
    finally:
        LOCK.unlink(missing_ok=True)
    ok = done(sid)
    lines = []
    asr = STORIES / sid / "asr_check.txt"
    low = [l for l in (asr.read_text(encoding="utf-8").splitlines() if asr.is_file() else []) if "ratio" in l and float(l.split("ratio")[1].split()[0]) < 0.8]
    mp4 = STORIES / sid / "renders" / f"{sid}.mp4"
    dur = ""
    if mp4.is_file():
        r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(mp4)], capture_output=True, text=True)
        try:
            dur = f"{float(r.stdout.strip()) / 60:.1f} นาที"
        except ValueError:
            pass
    lines.append(f"\n## {datetime.date.today()} — {doc['title']}  ({'สำเร็จ' if ok else 'ไม่สำเร็จ'})\n")
    lines.append(f"- เรื่อง: `{sid}` · ความยาว {dur or '-'} · ใช้เวลาทำ {int((time.time() - t0) / 60)} นาที")
    sh = STORIES / sid / "shorts"
    if sh.is_dir():
        lines.append(f"- Shorts แนวตั้ง {len(list(sh.glob('short_*.mp4')))} คลิป: `stories/{sid}/shorts/` (ชื่อ/คำอธิบาย/แท็กเสนอใน shorts.txt)")
    lines.append(f"- ไฟล์: ห้องสมุด → รู้หรือไม่ (ชื่อ EP ล่าสุด) · ต้นฉบับ `stories/{sid}/renders/{sid}.mp4`")
    lines.append("- ถอดเสียงกลับต่ำกว่า 0.80 ในฉาก: " + (", ".join(l.split(":")[0] for l in low) if low else "ไม่มี") + " (เลขอารบิกทำให้คะแนนต่ำลงได้)")
    srcs = doc.get("sources") or []
    if srcs:
        lines.append("- แหล่งข้อมูลที่ใช้ (ตรวจก่อนเผยแพร่): " + " · ".join(f"[{s['name']}]({s['url']})" for s in srcs[:6]))
    lines.append("- ต้องตรวจก่อนเผยแพร่: ฟังชื่อ/คำที่ออกเสียงเพี้ยน, ตัวเลขและแหล่งอ้างอิง, ข้อความ 'ไม่ใช่คำแนะนำการลงทุน' ต้องอยู่ในฉากสุดท้าย")
    if not ok:
        lg = STORIES / sid / "run_log.txt"
        lines.append("- สาเหตุที่ล้มเหลว (ท้ายล็อก): " + (lg.read_text(encoding="utf-8", errors="ignore")[-400:].replace("\n", " ") if lg.is_file() else (p.stderr or "")[-300:]))
    old = REPORT.read_text(encoding="utf-8") if REPORT.is_file() else "# รายงานคลิปรายวัน (ใหม่สุดอยู่ล่าง)\n"
    REPORT.write_text(old + "\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
