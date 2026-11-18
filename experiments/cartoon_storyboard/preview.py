"""Video library manager in the browser (no VLC, no installs).

    python preview.py

Starts a local-only web server (127.0.0.1) listing every episode in
output/videos/: watch, save as MP4, rename, delete, and make/edit/download
each episode's cover image (covers.py). Ctrl+C to stop.
"""

from __future__ import annotations

import html
import json
import sys
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import quote, unquote, urlparse

import covers
import library
import playlists
import shorts_lib

CHUNK = 1 << 16


def _move_select(key: str, current: str, pls: list[dict]) -> str:
    opts = "".join(f'<option value="{html.escape(p["id"], quote=True)}"{" selected" if p["id"] == current else ""}>'
                   f'{html.escape(p["name"])}</option>' for p in pls)
    return f'<label class="move">ย้ายไป <select data-move="{html.escape(key, quote=True)}">{opts}</select></label>'


def _card(e, pid: str, pls: list[dict]) -> str:
    folder = html.escape(e["folder"], quote=True)
    meta = [f"{e['duration'] // 60:.0f}:{e['duration'] % 60:02.0f} นาที"]
    if e["video"]:
        meta.append(f"{e['video'].stat().st_size / 1e6:.1f} MB")
    meta.append("เรนเดอร์ " + e.get("rendered_at", "").replace("T", " ")[:16])
    if e["video"]:
        src = "/video/" + quote(e["folder"])
        player = f'<video controls preload="metadata" src="{src}"></video>'
        save = (f'<a class="btn primary" href="{src}?download=1" '
                f'download="{html.escape(e["video"].name, quote=True)}">บันทึกเป็น MP4</a>')
    else:
        player, save = '<div class="missing">ไม่พบไฟล์วิดีโอในโฟลเดอร์นี้</div>', ""
    theme = f'<span class="tag">{html.escape(e["theme"])}</span>' if e.get("theme") else ""
    return f"""
      <section data-folder="{folder}">
        <div class="head">
          <span class="ep">EP{e['ep']:02d}</span>
          <h2 class="title">{html.escape(e['title'])}</h2>
          {theme}
        </div>
        <p class="topic">หัวข้อ: {html.escape(e.get('topic') or '-')}</p>
        {player}
        <div class="row">
          {save}
          <button class="btn" data-act="rename">เปลี่ยนชื่อ</button>
          <button class="btn danger" data-act="delete">ลบ</button>
          {_move_select("ep:" + e["episode_id"], pid, pls)}
          <span class="meta">{' · '.join(meta)}</span>
        </div>
        {_cover_block(e["folder"], e["title"], "16:9")}
        <p class="path">output/videos/{html.escape(e['folder'])}/</p>
      </section>"""


def _note_box(data) -> str:
    """Optional "จุดที่อยากแก้" box for the AI cover buttons, plus this episode's past notes."""
    items = "".join(
        f'<li><button class="chip" data-reuse="{html.escape(h["note"], quote=True)}">ใช้ซ้ำ</button>'
        f'<span>{html.escape(h["note"])}</span><span class="when">{html.escape(h["at"][:16].replace("T", " "))}</span></li>'
        for h in (data or {}).get("history", []))
    history = f'<ul class="history">{items}</ul>' if items else ""
    return f"""
          <label class="notebox">จุดที่อยากแก้ (พิมพ์แล้วกด "ให้ AI แก้ตามที่พิมพ์" = แก้เฉพาะจุดนี้ คำบนปกคงเดิม)
            <input class="note" type="text" maxlength="300"
                   placeholder="เช่น อยากให้เน้นเรื่องเงิน / ใช้ฉากกลางคืน / คำบนปกสั้นกว่านี้">
          </label>{history}"""


def _cover_block(key: str, title: str, aspect: str) -> str:
    """Cover tools for any clip: `key` is an episode folder or "short:<id>"."""
    data = covers.load(key)
    jpg = covers.cover_path(key)
    if data is None or not jpg.is_file():
        return f"""
        <div class="cover">
          <h3>รูปปกคลิป</h3>
          <div class="nocover">ยังไม่มีรูปปก</div>{_note_box(data)}
          <div class="row"><button class="btn primary" data-act="cover-generate">สร้างรูปปก (AI)</button></div>
        </div>"""
    src = "/cover/" + quote(key)
    stamp = int(jpg.stat().st_mtime)
    fname = html.escape(covers.download_name(key), quote=True)
    styles = "".join(
        f'<button class="chip{" on" if i == data["choice"] else ""}" data-act="cover-choose" data-i="{i}" '
        f'title="{html.escape(c.get("visual_hook", ""), quote=True)}">แบบ {i + 1}: {html.escape(c["name"])}</button>'
        for i, c in enumerate(data["concepts"]))
    note = f'<p class="warn">{html.escape(data["error"])}</p>' if data.get("error") else ""
    done = (f'<p class="hint">ผลที่ AI แก้ล่าสุด: {html.escape(data["last_edit_note"])}</p>'
            if data.get("last_edit_note") else "")
    hook = (f'<p class="hint">คำถามที่ปกชวนให้สงสัย: {html.escape(data["hook_question"])}</p>'
            if data.get("hook_question") else "")
    shape = "tall" if aspect == "9:16" else ""
    use_base_btn = (chr(10) + '            <button class="btn" data-act="cover-base">ใช้ภาพจากตอน</button>'
                    if covers.has_base(key) and not data.get("base") else "")
    return f"""
        <div class="cover" data-text="{html.escape(data['text'], quote=True)}" data-base="{1 if data.get('base') else 0}">
          <h3>รูปปกคลิป</h3>
          <img class="{shape}" src="{src}?v={stamp}" alt="รูปปก {html.escape(title, quote=True)}">
          <div class="chips">{styles}</div>
          {hook}{done}{note}{_note_box(data)}
          <div class="row">
            <a class="btn primary" href="{src}?download=1&v={stamp}" download="{fname}">ดาวน์โหลดรูปปก</a>
            <button class="btn primary" data-act="cover-edit">ให้ AI แก้ตามที่พิมพ์</button>
            <button class="btn" data-act="cover-text">แก้ข้อความบนปก</button>
            <button class="btn" data-act="cover-rewrite">ให้ AI เขียนคำใหม่</button>
            <button class="btn" data-act="cover-generate">สร้างแบบใหม่ทั้งหมด (AI)</button>{use_base_btn}
          </div>
        </div>"""


def _short_card(sh, pid: str, pls: list[dict]) -> str:
    sid = html.escape(sh["id"], quote=True)
    key = "short:" + sh["id"]
    src = "/short/" + quote(sh["id"])
    meta = [f"{sh['duration'] // 60:.0f}:{sh['duration'] % 60:02.0f} นาที", f"{sh['size'] / 1e6:.1f} MB",
            "เรนเดอร์ " + sh["rendered_at"].replace("T", " ")]
    vclass = "vertical" if sh["aspect"] == "9:16" else ""
    return f"""
      <section class="short" data-short="{sid}" data-folder="{html.escape(key, quote=True)}">
        <div class="head">
          <span class="ep short-tag">{html.escape(sh['aspect'])}</span>
          <h2 class="title">{html.escape(sh['title'])}</h2>
        </div>
        <video class="{vclass}" controls preload="metadata" src="{src}"></video>
        <div class="row">
          <a class="btn primary" href="{src}?download=1" download="{html.escape(shorts_lib.download_name(sh), quote=True)}">ดาวน์โหลด MP4</a>
          <button class="btn" data-sact="rename">แก้ชื่อเรื่อง</button>
          <button class="btn danger" data-sact="delete">ลบ</button>
          {_move_select(key, pid, pls)}
          <span class="meta">{' · '.join(meta)}</span>
        </div>
        {_cover_block(key, sh["title"], sh["aspect"])}
      </section>"""


def _page() -> bytes:
    groups = playlists.grouped()
    pls = [p for p, _ in groups]
    total = sum(len(its) for _, its in groups)
    sections = []
    for pl, its in groups:
        cards = "".join(_card(it["entry"], pl["id"], pls) if it["kind"] == "ep" else _short_card(it["entry"], pl["id"], pls)
                        for it in its) or '<p class="empty">ยังไม่มีคลิปในเพลย์ลิสต์นี้</p>'
        locked = ' disabled title="ย้ายคลิปออกก่อน"' if its else ""
        delete_btn = ("" if pl.get("builtin") else
                      f'<button class="btn danger small" data-pact="delete"{locked}>ลบเพลย์ลิสต์</button>')
        sections.append(f"""
<div class="playlist" data-pl="{html.escape(pl['id'], quote=True)}">
  <h2 class="playlist"><span class="plname">{html.escape(pl['name'])}</span>
    <span class="count">{html.escape(pl['aspect'])} · {len(its)} คลิป</span>
    <button class="btn small" data-pact="rename">เปลี่ยนชื่อ</button>{delete_btn}</h2>
  {cards}
</div>""")
    body = "".join(sections)
    manage = """
<div class="manage">
  <input id="plName" type="text" maxlength="60" placeholder="ชื่อเพลย์ลิสต์ใหม่ เช่น เรื่องผี / เศรษฐกิจ">
  <select id="plAspect"><option value="16:9">16:9 แนวนอน</option><option value="9:16">9:16 แนวตั้ง</option><option value="1:1">1:1</option></select>
  <button class="btn primary" data-pact="add">เพิ่มเพลย์ลิสต์</button>
</div>"""
    return f"""<!doctype html>
<html lang="th"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Episode Library</title>
<style>
  :root {{ --bg:#f6f4ef; --fg:#2b2735; --muted:#6d6878; --card:#fff; --line:#e6e1d8;
          --accent:#e0a043; --danger:#c8553d; }}
  @media (prefers-color-scheme: dark) {{ :root:not([data-theme="light"]) {{ --bg:#1d1b24; --fg:#ece8f2;
          --muted:#a59fb2; --card:#2a2733; --line:#3a3644; }} }}
  :root[data-theme="dark"] {{ --bg:#1d1b24; --fg:#ece8f2; --muted:#a59fb2; --card:#2a2733; --line:#3a3644; }}
  * {{ box-sizing:border-box; }}
  body {{ margin:0; padding:24px 16px; background:var(--bg); color:var(--fg);
         font-family:"Leelawadee UI","Segoe UI",sans-serif; }}
  main {{ max-width:980px; margin:0 auto; }}
  header {{ display:flex; align-items:baseline; gap:12px; margin-bottom:18px; flex-wrap:wrap; }}
  h1 {{ font-size:1.4rem; margin:0; }}
  .count {{ color:var(--muted); }}
  section {{ background:var(--card); border-radius:14px; padding:16px; margin-bottom:20px;
            box-shadow:0 2px 10px rgba(0,0,0,.08); }}
  .head {{ display:flex; align-items:center; gap:10px; flex-wrap:wrap; margin-bottom:4px; }}
  .ep {{ background:var(--accent); color:#2b2014; font-weight:800; border-radius:8px; padding:3px 9px; }}
  h2 {{ font-size:1.1rem; margin:0; }}
  .tag {{ border:1px solid var(--line); color:var(--muted); border-radius:999px; padding:2px 10px; font-size:.85rem; }}
  .topic, .path {{ color:var(--muted); font-size:.9rem; margin:4px 0 10px; }}
  .path {{ margin:10px 0 0; font-family:Consolas,monospace; font-size:.8rem; word-break:break-all; }}
  video {{ width:100%; border-radius:10px; background:#000; display:block; }}
  .missing {{ padding:40px; text-align:center; border:1px dashed var(--line); border-radius:10px; color:var(--muted); }}
  .row {{ display:flex; align-items:center; gap:10px; margin-top:12px; flex-wrap:wrap; }}
  .btn {{ font:inherit; font-weight:700; padding:9px 16px; border-radius:10px; cursor:pointer;
          border:1px solid var(--line); background:transparent; color:var(--fg); text-decoration:none; }}
  .btn.primary {{ background:var(--accent); border-color:var(--accent); color:#2b2014; }}
  .btn.danger {{ color:var(--danger); border-color:var(--danger); }}
  .meta {{ color:var(--muted); font-size:.9rem; margin-left:auto; }}
  .empty {{ color:var(--muted); }}
  .cover {{ border-top:1px solid var(--line); margin-top:16px; padding-top:12px; }}
  .cover h3 {{ font-size:1rem; margin:0 0 8px; }}
  .cover img {{ width:100%; max-width:640px; aspect-ratio:16/9; border-radius:10px; display:block; }}
  .nocover {{ padding:24px; text-align:center; border:1px dashed var(--line); border-radius:10px;
              color:var(--muted); max-width:640px; }}
  .chips {{ display:flex; gap:8px; flex-wrap:wrap; margin-top:10px; }}
  .chip {{ font:inherit; font-size:.85rem; padding:5px 12px; border-radius:999px; cursor:pointer;
           border:1px solid var(--line); background:transparent; color:var(--fg); }}
  .chip.on {{ background:var(--accent); border-color:var(--accent); color:#2b2014; font-weight:700; }}
  .hint {{ color:var(--muted); font-size:.85rem; margin:8px 0 0; }}
  .warn {{ color:var(--danger); font-size:.85rem; margin:8px 0 0; }}
  .busy {{ opacity:.55; pointer-events:none; }}
  .notebox {{ display:block; margin-top:12px; color:var(--muted); font-size:.85rem; max-width:640px; }}
  .notebox input {{ display:block; width:100%; margin-top:4px; font:inherit; font-size:.95rem; color:var(--fg);
                    padding:8px 10px; border-radius:10px; border:1px solid var(--line); background:var(--bg); }}
  .history {{ list-style:none; padding:0; margin:8px 0 0; max-width:640px; font-size:.85rem; }}
  .history li {{ display:flex; gap:8px; align-items:center; padding:3px 0; }}
  .history span {{ overflow-wrap:anywhere; }}
  .history .when {{ color:var(--muted); margin-left:auto; white-space:nowrap; }}
  h2.playlist {{ font-size:1.15rem; margin:26px 0 12px; padding-bottom:6px; border-bottom:2px solid var(--line); }}
  h2.playlist .count {{ font-size:.85rem; font-weight:400; margin-left:8px; }}
  video.vertical {{ width:100%; max-width:360px; aspect-ratio:9/16; margin:0 auto 0 0; }}
  .short-tag {{ background:#7fb069; }}
  .manage {{ display:flex; gap:8px; flex-wrap:wrap; align-items:center; background:var(--card); border-radius:14px;
             padding:12px 16px; box-shadow:0 2px 10px rgba(0,0,0,.08); }}
  .manage input, .manage select, .move select {{ font:inherit; padding:8px 10px; border-radius:10px; border:1px solid var(--line);
             background:var(--bg); color:var(--fg); }}
  .manage input {{ flex:1; min-width:180px; }}
  h2.playlist {{ display:flex; align-items:center; gap:8px; flex-wrap:wrap; }}
  .btn.small {{ padding:5px 10px; font-size:.85rem; }}
  .btn[disabled] {{ opacity:.45; cursor:not-allowed; }}
  .move {{ color:var(--muted); font-size:.9rem; }}
  .cover img.tall {{ max-width:300px; aspect-ratio:9/16; }}
</style></head>
<body><main>
<header><h1>คลังวิดีโอการ์ตูน</h1><span class="count">{len(pls)} เพลย์ลิสต์ · {total} คลิป</span></header>
{manage}
{body}
</main>
<script>
async function call(path, payload) {{
  const r = await fetch(path, {{method: "POST", headers: {{"Content-Type": "application/json"}},
                                body: JSON.stringify(payload)}});
  const data = await r.json().catch(() => ({{}}));
  if (!r.ok) throw new Error(data.error || r.statusText);
  return data;
}}
document.addEventListener("change", async (ev) => {{
  const sel = ev.target.closest("select[data-move]");
  if (!sel) return;
  try {{
    await call("/api/move", {{key: sel.dataset.move, playlist: sel.value}});
  }} catch (err) {{
    alert("ย้ายไม่สำเร็จ: " + err.message);
  }}
  location.reload();
}});
document.addEventListener("click", async (ev) => {{
  const pbtn = ev.target.closest("button[data-pact]");
  if (pbtn) {{
    const box = pbtn.closest("[data-pl]");
    try {{
      if (pbtn.dataset.pact === "add") {{
        const name = document.getElementById("plName").value.trim();
        if (!name) {{ alert("พิมพ์ชื่อเพลย์ลิสต์ก่อน"); return; }}
        await call("/api/playlist-add", {{name, aspect: document.getElementById("plAspect").value}});
      }} else if (pbtn.dataset.pact === "rename") {{
        const cur = box.querySelector(".plname").textContent;
        const next = prompt("ชื่อเพลย์ลิสต์ใหม่", cur);
        if (!next || next.trim() === cur) return;
        await call("/api/playlist-rename", {{id: box.dataset.pl, name: next.trim()}});
      }} else {{
        if (!confirm("ลบเพลย์ลิสต์นี้?")) return;
        await call("/api/playlist-delete", {{id: box.dataset.pl}});
      }}
    }} catch (err) {{
      alert("ทำไม่สำเร็จ: " + err.message);
    }}
    location.reload();
    return;
  }}
  const reuse = ev.target.closest("button[data-reuse]");
  if (reuse) {{
    const input = reuse.closest(".cover").querySelector("input.note");
    input.value = reuse.dataset.reuse;
    input.focus();
    return;
  }}
  const sbtn = ev.target.closest("button[data-sact]");
  if (sbtn) {{
    const card = sbtn.closest("section"), id = card.dataset.short;
    const title = card.querySelector(".title").textContent;
    if (sbtn.dataset.sact === "delete") {{
      if (!confirm(`ลบคลิป "${{title}}" ? ลบแล้วกู้คืนไม่ได้ (บทใน scripts/ ยังอยู่ เรนเดอร์ใหม่ได้)`)) return;
      const v = card.querySelector("video");
      v.removeAttribute("src");
      v.load();
      try {{
        await call("/api/short-delete", {{id}});
      }} catch (err) {{
        alert("ลบไม่สำเร็จ: " + err.message);
      }}
      location.reload();
      return;
    }}
    const next = prompt("ชื่อเรื่องใหม่", title);
    if (!next || next.trim() === title) return;
    try {{
      await call("/api/short-rename", {{id, title: next.trim()}});
    }} catch (err) {{
      alert("แก้ชื่อไม่สำเร็จ: " + err.message);
    }}
    location.reload();
    return;
  }}
  const btn = ev.target.closest("button[data-act]");
  if (!btn) return;
  const card = btn.closest("section"), folder = card.dataset.folder;
  const title = card.querySelector(".title").textContent;
  const act = btn.dataset.act;
  if (act.startsWith("cover-")) {{
    const box = card.querySelector(".cover");
    let payload = {{folder, note: box.querySelector("input.note")?.value.trim() || ""}};
    if (act === "cover-text") {{
      const next = prompt("ข้อความบนปก (พิมพ์ \\\\n เพื่อขึ้นบรรทัดใหม่ รวมไม่เกิน 80 ตัวอักษร ภาพปกเดิมจะอยู่ครบ เปลี่ยนเฉพาะข้อความ)", box.dataset.text.replace(/\\n/g, "\\\\n"));
      if (next === null || !next.trim()) return;
      payload.text = next;
    }} else if (act === "cover-choose") {{
      payload.index = Number(btn.dataset.i);
    }} else if (act === "cover-edit" && !payload.note) {{
      alert("พิมพ์สิ่งที่อยากแก้ในช่องก่อน เช่น เปลี่ยนฉากหลังเป็นสถานีรถไฟฟ้า");
      return;
    }} else if (act === "cover-generate" && box.querySelector("img") && !confirm(
        box.dataset.base === "1"
          ? "ปกนี้ใช้ภาพจากฉากในวิดีโอ สร้างแบบใหม่ (ใช้ AI 1 ครั้ง) ภาพและข้อความจะถูกแทนที่ด้วยแบบที่ AI ออกแบบ (กด 'ใช้ภาพจากตอน' เพื่อกลับมาภายหลังได้) ทำต่อไหม?"
          : "สร้างแบบใหม่ 3 แบบ (ใช้ AI 1 ครั้ง) ข้อความที่แก้ไว้จะถูกแทนที่ ทำต่อไหม?")) {{
      return;
    }}
    box.classList.add("busy");
    btn.textContent = "กำลังทำ...";
    try {{
      await call("/api/" + act, payload);
    }} catch (err) {{
      alert("ทำรูปปกไม่สำเร็จ: " + err.message);
    }}
    location.reload();
    return;
  }}
  try {{
    if (act === "rename") {{
      const next = prompt("ชื่อตอนใหม่", title);
      if (!next || next.trim() === title) return;
      card.querySelector("video")?.removeAttribute("src");
      card.querySelector("video")?.load();
      await call("/api/rename", {{folder, title: next.trim()}});
    }} else {{
      if (!confirm(`ลบ "${{folder}}" ทั้งโฟลเดอร์? ลบแล้วกู้คืนไม่ได้`)) return;
      card.querySelector("video")?.removeAttribute("src");
      card.querySelector("video")?.load();
      await call("/api/delete", {{folder}});
    }}
    location.reload();
  }} catch (err) {{
    alert("ทำไม่สำเร็จ: " + err.message);
    location.reload();
  }}
}});
</script>
</body></html>""".encode("utf-8")


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        url = urlparse(self.path)
        if url.path == "/":
            self._send(200, _page(), "text/html; charset=utf-8")
        elif url.path.startswith("/video/"):
            entry = library.find(unquote(url.path[len("/video/"):]))
            if entry is None or entry["video"] is None:
                self.send_error(404)
            else:
                self._send_video(entry["video"], download="download=1" in url.query)
        elif url.path.startswith("/short/"):
            entry = shorts_lib.find(unquote(url.path[len("/short/"):]))
            if entry is None:
                self.send_error(404)
            else:
                self._send_video(entry["video"], download="download=1" in url.query, name=shorts_lib.download_name(entry))
        elif url.path.startswith("/cover/"):
            key = unquote(url.path[len("/cover/"):])
            try:
                jpg, name = covers.cover_path(key), covers.download_name(key)
            except KeyError:
                return self.send_error(404)
            if not jpg.is_file():
                return self.send_error(404)
            data = jpg.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "image/jpeg")
            self.send_header("Content-Length", str(len(data)))
            self.send_header("Cache-Control", "no-store")
            if "download=1" in url.query:
                self.send_header("Content-Disposition", f"attachment; filename*=UTF-8''{quote(name)}")
            self.end_headers()
            self.wfile.write(data)
        else:
            self.send_error(404)

    def do_POST(self):
        # Only same-origin requests from the page itself may change files.
        host = self.headers.get("Host", "")
        if self.headers.get("Origin") not in (f"http://{host}",):
            return self._json(403, {"error": "forbidden"})
        try:
            payload = json.loads(self.rfile.read(int(self.headers.get("Content-Length", 0))) or b"{}")
            path = urlparse(self.path).path
            if path == "/api/rename":
                return self._json(200, {"folder": library.rename(payload["folder"], payload["title"])})
            if path == "/api/playlist-add":
                return self._json(200, playlists.add(payload["name"], payload.get("aspect", "16:9")))
            if path == "/api/playlist-rename":
                return self._json(200, {"name": playlists.rename(payload["id"], payload["name"])})
            if path == "/api/playlist-delete":
                playlists.delete(payload["id"])
                return self._json(200, {"ok": True})
            if path == "/api/move":
                playlists.move(payload["key"], payload["playlist"])
                return self._json(200, {"ok": True})
            if path == "/api/short-delete":
                shorts_lib.delete(payload["id"])
                return self._json(200, {"ok": True})
            if path == "/api/short-rename":
                return self._json(200, {"title": shorts_lib.rename(payload["id"], payload["title"])})
            if path == "/api/delete":
                library.delete(payload["folder"])
                return self._json(200, {"ok": True})
            cover_actions = {
                "/api/cover-generate": lambda p: covers.generate(p["folder"], p.get("note", "")),
                "/api/cover-edit": lambda p: covers.edit_concept(p["folder"], p.get("note", "")),
                "/api/cover-choose": lambda p: covers.choose(p["folder"], int(p["index"])),
                "/api/cover-text": lambda p: covers.set_text(p["folder"], p["text"]),
                "/api/cover-rewrite": lambda p: covers.rewrite_text(p["folder"], p.get("note", "")),
                "/api/cover-base": lambda p: covers.use_base(p["folder"]),
            }
            if path in cover_actions:
                data = cover_actions[path](payload)
                return self._json(200, {"text": data["text"], "error": data.get("error")})
            return self._json(404, {"error": "not found"})
        except KeyError:
            return self._json(404, {"error": "ไม่พบตอนนี้"})
        except FileExistsError:
            return self._json(409, {"error": "มีชื่อนี้อยู่แล้ว"})
        except PermissionError:
            return self._json(409, {"error": "ไฟล์กำลังถูกเปิดอยู่ ปิดวิดีโอแล้วลองใหม่"})
        except Exception as exc:  # e.g. Gemini quota/network during an AI cover action
            return self._json(500, {"error": str(exc)[:300]})

    def _send(self, status, data, ctype):
        self.send_response(status)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def _json(self, status, obj):
        self._send(status, json.dumps(obj, ensure_ascii=False).encode("utf-8"), "application/json; charset=utf-8")

    def _send_video(self, path, download: bool, name=None):
        size = path.stat().st_size
        start, end, status = 0, size - 1, 200
        rng = self.headers.get("Range", "")
        if rng.startswith("bytes="):
            first, _, last = rng[6:].split(",")[0].strip().partition("-")
            try:
                if first:
                    start, end = int(first), int(last) if last else size - 1
                else:
                    start = max(0, size - int(last))
            except ValueError:
                self.send_error(416)
                return
            end, status = min(end, size - 1), 206
            if start > end:
                self.send_response(416)
                self.send_header("Content-Range", f"bytes */{size}")
                self.end_headers()
                return

        self.send_response(status)
        self.send_header("Content-Type", "video/mp4")
        self.send_header("Accept-Ranges", "bytes")
        self.send_header("Content-Length", str(end - start + 1))
        if status == 206:
            self.send_header("Content-Range", f"bytes {start}-{end}/{size}")
        if download:
            self.send_header("Content-Disposition", f"attachment; filename*=UTF-8''{quote(name or path.name)}")
        self.end_headers()
        # Open the file per chunk: on Windows an open handle would block
        # renaming or deleting the episode while a browser tab is streaming it.
        pos, remaining = start, end - start + 1
        try:
            while remaining > 0:
                with path.open("rb") as f:
                    f.seek(pos)
                    chunk = f.read(min(CHUNK * 16, remaining))
                if not chunk:
                    break
                self.wfile.write(chunk)
                pos += len(chunk)
                remaining -= len(chunk)
        except (OSError, BrokenPipeError, ConnectionResetError, ConnectionAbortedError):
            pass

    def log_message(self, *args):
        pass


def main():
    server = ThreadingHTTPServer(("127.0.0.1", 52101), Handler)
    url = f"http://127.0.0.1:{server.server_address[1]}/"
    print(f"Library: {url}  (Ctrl+C to stop)", flush=True)
    if "--no-open" not in sys.argv:
        webbrowser.open(url)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
