"""Thumbnail Studio: local web UI on top of thumbnail_studio.py.

    python thumbnail_app.py

Flow: pick an episode (or type a title/summary) -> analyze (1 Gemini text
call) -> 3 concepts -> render -> edit text/crop live -> export a PNG/JPEG
sized for YouTube -> optionally record the outcome you observed later.

No image-generation API; thumbnails are composed from the same procedural
renderer that draws the episodes. See thumbnail_studio.py's docstring.
"""

from __future__ import annotations

import base64
import html
import io
import json
import sys
import webbrowser
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, quote, unquote, urlparse

from life_lesson.config import get_settings
from life_lesson.errors import PipelineError

import thumbnail_studio as T

PORT = 52102


def _concept_dict(c, cid):
    d = c.model_dump()
    d["id"] = cid
    return d


def _new_store_from_analysis(key, episode_id, title, analysis, concepts):
    store = T.load_store(key)  # keep prior exports/outcomes if this key was used before
    store.update({
        "key": key, "episode_id": episode_id, "title": title,
        "analysis": analysis.model_dump(),
        "concepts": [_concept_dict(c, f"c{i + 1}") for i, c in enumerate(concepts)],
    })
    store.setdefault("concept_settings", {})
    store.setdefault("exports", [])
    store.setdefault("outcomes", [])
    return store


def _concept_by_id(store, concept_id):
    for c in store["concepts"]:
        if c["id"] == concept_id:
            return T.ThumbnailConcept.model_validate(c)
    raise KeyError(concept_id)


def _data_uri(img, fmt="PNG"):
    buf = io.BytesIO()
    img.save(buf, fmt)
    return f"data:image/{fmt.lower()};base64,{base64.b64encode(buf.getvalue()).decode()}"


def _b64_png(img):
    buf = io.BytesIO()
    img.save(buf, "PNG")
    return base64.b64encode(buf.getvalue()).decode()


DEFAULT_TEXT = {"size": 96, "bold": True, "color": "#FFFFFF", "outline": True, "outline_color": "#2B2016",
                "shadow": True, "scrim": True, "anchor": "bottom-center"}
DEFAULT_CROP = {"fx": 0.5, "fy": 0.5, "zoom": 1.0}


def _page() -> bytes:
    opts = "".join(f'<option value="{html.escape(e["key"])}">{html.escape(e["label"])}</option>'
                    for e in T.episode_options())
    return f"""<!doctype html>
<html lang="th"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Thumbnail Studio</title>
<style>
  :root {{ --bg:#f6f4ef; --fg:#2b2735; --muted:#6d6878; --card:#fff; --line:#e6e1d8;
          --accent:#e0a043; --danger:#c8553d; }}
  @media (prefers-color-scheme: dark) {{ :root:not([data-theme="light"]) {{ --bg:#1d1b24; --fg:#ece8f2;
          --muted:#a59fb2; --card:#2a2733; --line:#3a3644; }} }}
  :root[data-theme="dark"] {{ --bg:#1d1b24; --fg:#ece8f2; --muted:#a59fb2; --card:#2a2733; --line:#3a3644; }}
  * {{ box-sizing:border-box; }}
  body {{ margin:0; padding:24px 16px 80px; background:var(--bg); color:var(--fg);
         font-family:"Leelawadee UI","Segoe UI",sans-serif; }}
  main {{ max-width:1180px; margin:0 auto; }}
  h1 {{ font-size:1.4rem; margin:0 0 4px; }}
  .sub {{ color:var(--muted); margin:0 0 18px; }}
  section {{ background:var(--card); border-radius:14px; padding:18px; margin-bottom:20px;
            box-shadow:0 2px 10px rgba(0,0,0,.08); }}
  h2 {{ font-size:1.05rem; margin:0 0 12px; }}
  label {{ display:block; font-size:.85rem; color:var(--muted); margin:10px 0 4px; }}
  select, textarea, input[type=text] {{ width:100%; font:inherit; padding:9px 10px; border-radius:8px;
          border:1px solid var(--line); background:transparent; color:var(--fg); }}
  textarea {{ resize:vertical; min-height:70px; }}
  .row {{ display:flex; gap:14px; flex-wrap:wrap; align-items:flex-end; }}
  .row > div {{ flex:1; min-width:160px; }}
  .btn {{ font:inherit; font-weight:700; padding:9px 16px; border-radius:10px; cursor:pointer;
          border:1px solid var(--line); background:transparent; color:var(--fg); }}
  .btn.primary {{ background:var(--accent); border-color:var(--accent); color:#2b2014; }}
  .btn.small {{ padding:5px 10px; font-weight:600; font-size:.85rem; }}
  .err {{ color:var(--danger); font-size:.9rem; margin-top:8px; white-space:pre-wrap; }}
  .muted {{ color:var(--muted); font-size:.85rem; }}
  .analysis {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(220px,1fr)); gap:10px; font-size:.9rem; }}
  .analysis b {{ display:block; color:var(--muted); font-weight:600; font-size:.78rem; margin-bottom:2px; }}
  .concepts {{ display:grid; grid-template-columns:repeat(auto-fit,minmax(280px,1fr)); gap:14px; }}
  .concept {{ border:1px solid var(--line); border-radius:12px; padding:12px; }}
  .concept.active {{ border-color:var(--accent); }}
  .concept img {{ width:100%; border-radius:8px; aspect-ratio:16/9; object-fit:cover; background:#1119; }}
  .tag {{ display:inline-block; border:1px solid var(--line); color:var(--muted); border-radius:999px;
         padding:1px 9px; font-size:.75rem; margin-bottom:6px; }}
  .concept h3 {{ margin:4px 0; font-size:1rem; }}
  .concept p {{ font-size:.83rem; margin:4px 0; color:var(--muted); }}
  #editor {{ display:none; }}
  .editgrid {{ display:grid; grid-template-columns:1.1fr 1fr; gap:20px; }}
  @media (max-width:820px) {{ .editgrid {{ grid-template-columns:1fr; }} }}
  #previewImg {{ width:100%; border-radius:10px; cursor:crosshair; background:#1119; }}
  .feedwrap {{ margin-top:10px; width:320px; max-width:100%; }}
  .feedcard img {{ width:100%; border-radius:8px; }}
  .feedcard .ft {{ font-size:.78rem; margin-top:6px; color:var(--fg); }}
  .feedcard .fm {{ font-size:.72rem; color:var(--muted); }}
  .anchorgrid {{ display:grid; grid-template-columns:repeat(3,1fr); gap:4px; width:140px; }}
  .anchorgrid button {{ aspect-ratio:1; border-radius:6px; border:1px solid var(--line); background:transparent;
          cursor:pointer; color:var(--fg); }}
  .anchorgrid button.on {{ background:var(--accent); border-color:var(--accent); }}
  .checks {{ display:flex; gap:14px; flex-wrap:wrap; font-size:.85rem; }}
  .checks label {{ display:flex; align-items:center; gap:6px; margin:0; }}
  input[type=color] {{ width:48px; height:32px; padding:2px; border-radius:6px; border:1px solid var(--line); }}
  table {{ width:100%; border-collapse:collapse; font-size:.85rem; }}
  th, td {{ text-align:left; padding:6px 8px; border-bottom:1px solid var(--line); }}
  .note {{ font-size:.78rem; color:var(--muted); margin-top:10px; }}
</style></head>
<body><main>
<h1>Thumbnail Studio</h1>
<p class="sub">วิเคราะห์เรื่อง → 3 คอนเซ็ปต์ที่ต่างกันจริง → แก้ข้อความ/ครอปสด → ส่งออกให้พร้อมอัปโหลด
ภาพทั้งหมดวาดด้วยระบบตัวละครของช่องเอง ไม่มีการเรียก API สร้างภาพ</p>

<section id="pick">
  <h2>1. เลือกตอน หรือกรอกเรื่องเอง</h2>
  <div class="row">
    <div><label>ตอนในคลัง</label><select id="epSelect"><option value="">-- กรอกเอง --</option>{opts}</select></div>
  </div>
  <label>ชื่อตอน</label><input type="text" id="title">
  <label>สรุปเรื่อง หรือสคริปต์เต็ม</label><textarea id="summary"></textarea>
  <div class="row" style="margin-top:12px">
    <button class="btn primary" id="analyzeBtn">วิเคราะห์เรื่อง</button>
    <span class="muted" id="analyzeStatus"></span>
  </div>
  <div class="err" id="analyzeErr"></div>
</section>

<section id="analysisSec" style="display:none">
  <h2>2. บทวิเคราะห์</h2>
  <div class="analysis">
    <div><b>อารมณ์หลัก</b><span id="a_emotion"></span></div>
    <div><b>ความขัดแย้งหลัก</b><span id="a_conflict"></span></div>
    <div><b>ภาพที่ทรงพลังที่สุด</b><span id="a_moment"></span></div>
    <div><b>คำถามที่ยังไม่มีคำตอบ</b><span id="a_hook"></span></div>
    <div><b>กลุ่มเป้าหมาย</b><span id="a_audience"></span></div>
  </div>
</section>

<section id="conceptsSec" style="display:none">
  <h2>3. สามคอนเซ็ปต์</h2>
  <div class="concepts" id="concepts"></div>
</section>

<section id="editor">
  <h2>4. แก้ไขและส่งออก</h2>
  <div class="editgrid">
    <div>
      <img id="previewImg" alt="">
      <div class="muted" style="margin-top:4px">คลิกบนภาพเพื่อกำหนดจุดโฟกัส</div>
      <div class="feedwrap">
        <div class="muted" style="margin-bottom:6px">ตัวอย่างขนาดเล็กบนฟีด</div>
        <div class="feedcard">
          <img id="feedImg" alt="">
          <div class="ft" id="feedTitle"></div>
          <div class="fm">ช่องของคุณ</div>
        </div>
      </div>
    </div>
    <div>
      <label>ข้อความบนภาพ (ขึ้นบรรทัดใหม่ได้)</label>
      <textarea id="t_text"></textarea>
      <div class="row">
        <div><label>ขนาดตัวอักษร</label><input type="range" id="t_size" min="40" max="160" value="96"></div>
        <div><label>ซูมครอป</label><input type="range" id="c_zoom" min="100" max="200" value="100"></div>
      </div>
      <label>สีข้อความ</label>
      <div class="row">
        <div><input type="color" id="t_color" value="#ffffff"></div>
        <div class="checks">
          <label><input type="checkbox" id="t_outline" checked> ขอบตัวอักษร</label>
          <label><input type="checkbox" id="t_shadow" checked> เงา</label>
          <label><input type="checkbox" id="t_scrim" checked> แถบช่วยอ่าน</label>
        </div>
      </div>
      <label>ตำแหน่งข้อความ</label>
      <div class="anchorgrid" id="anchorGrid"></div>
      <div class="row" style="margin-top:16px">
        <div><label>รูปแบบไฟล์</label><select id="exportFmt"><option value="jpeg">JPEG</option><option value="png">PNG</option></select></div>
        <div><label>ความละเอียด</label><select id="exportRes"><option value="hd">1920×1080</option><option value="4k">3840×2160</option></select></div>
        <button class="btn primary" id="exportBtn" style="align-self:flex-end">ส่งออก</button>
      </div>
      <div class="err" id="exportErr"></div>
      <div class="muted" id="exportStatus"></div>
    </div>
  </div>

  <h2 style="margin-top:26px">5. ผลลัพธ์ที่บันทึกไว้</h2>
  <table id="exportTable"><thead><tr><th>เวลา</th><th>คอนเซ็ปต์</th><th>ไฟล์</th><th>ขนาด</th></tr></thead>
    <tbody id="exportRows"></tbody></table>

  <h2 style="margin-top:26px">6. บันทึกผลลัพธ์จริงบน YouTube</h2>
  <p class="note">กรอกเฉพาะตัวเลขที่คุณเห็นจริงจาก YouTube Studio เท่านั้น ระบบนี้ไม่คาดเดาหรือดึงข้อมูลให้เอง</p>
  <div class="row">
    <div><label>คอนเซ็ปต์</label><select id="o_concept"></select></div>
    <div><label>Impressions</label><input type="text" id="o_impr"></div>
    <div><label>CTR (%)</label><input type="text" id="o_ctr"></div>
    <div><label>Watch time (%)</label><input type="text" id="o_watch"></div>
    <div><label>ที่มา</label><input type="text" id="o_src"></div>
  </div>
  <label>หมายเหตุ</label><textarea id="o_note" style="min-height:40px"></textarea>
  <div class="row" style="margin-top:10px"><button class="btn" id="outcomeBtn">บันทึกผล</button></div>
  <table id="outcomeTable" style="margin-top:12px">
    <thead><tr><th>เวลา</th><th>คอนเซ็ปต์</th><th>Impr.</th><th>CTR</th><th>Watch%</th><th>ที่มา</th><th>หมายเหตุ</th></tr></thead>
    <tbody id="outcomeRows"></tbody></table>
</section>
</main>
<script>
const EP = {{}};
let state = {{ key: null, episodeId: null, concepts: [], active: null, text: {json.dumps(DEFAULT_TEXT)},
               crop: {json.dumps(DEFAULT_CROP)}, store: null }};

async function call(path, payload) {{
  const r = await fetch(path, {{method:"POST", headers:{{"Content-Type":"application/json"}}, body: JSON.stringify(payload||{{}})}});
  const data = await r.json().catch(()=>({{}}));
  if (!r.ok) throw new Error(data.error || r.statusText);
  return data;
}}

document.getElementById("epSelect").addEventListener("change", async (e) => {{
  const key = e.target.value;
  if (!key) return;
  const info = await call("/api/episode_text", {{episode_id: key}});
  document.getElementById("title").value = info.title;
  document.getElementById("summary").value = info.summary;
}});

document.getElementById("analyzeBtn").addEventListener("click", async () => {{
  const title = document.getElementById("title").value.trim();
  const summary = document.getElementById("summary").value.trim();
  const episode_id = document.getElementById("epSelect").value || null;
  const errBox = document.getElementById("analyzeErr"), status = document.getElementById("analyzeStatus");
  errBox.textContent = ""; status.textContent = "";
  if (!title || !summary) {{ errBox.textContent = "กรอกชื่อตอนและสรุปเรื่องก่อน"; return; }}
  status.textContent = "กำลังวิเคราะห์ด้วย Gemini... (ใช้โควตาการสร้างข้อความ 1 ครั้ง)";
  try {{
    const data = await call("/api/analyze", {{title, summary, episode_id}});
    state.key = data.key; state.episodeId = episode_id; state.concepts = data.concepts;
    showAnalysis(data.analysis); showConcepts(data.concepts);
    status.textContent = "เสร็จแล้ว";
  }} catch (err) {{
    errBox.textContent = "วิเคราะห์ไม่สำเร็จ: " + err.message;
    status.textContent = "";
  }}
}});

function showAnalysis(a) {{
  document.getElementById("analysisSec").style.display = "";
  document.getElementById("a_emotion").textContent = a.primary_emotion;
  document.getElementById("a_conflict").textContent = a.central_conflict;
  document.getElementById("a_moment").textContent = a.visual_moment;
  document.getElementById("a_hook").textContent = a.hook_question;
  document.getElementById("a_audience").textContent = a.audience_fit;
}}

const TPL_TH = {{portrait:"ภาพใหญ่ใบหน้า", wide_symbolic:"ภาพกว้างเชิงสัญลักษณ์",
                 contrast_split: "แบ่งภาพสองฝั่ง", object_hero: "วัตถุสัญลักษณ์ขนาดใหญ่"}};

function showConcepts(concepts) {{
  const sec = document.getElementById("conceptsSec"); sec.style.display = "";
  const wrap = document.getElementById("concepts"); wrap.innerHTML = "";
  const oSel = document.getElementById("o_concept"); oSel.innerHTML = "";
  for (const c of concepts) {{
    const div = document.createElement("div");
    div.className = "concept"; div.id = "concept_" + c.id;
    div.innerHTML = `<span class="tag">${{TPL_TH[c.template] || c.template}}</span>
      <h3>${{c.name}}</h3><p>${{c.visual_hook}}</p>
      <p class="muted">เหตุผล: ${{c.rationale}}</p><p class="muted">ความเสี่ยง: ${{c.risks}}</p>
      <img id="img_${{c.id}}" style="display:none">
      <div class="row" style="margin-top:8px">
        <button class="btn small" data-render="${{c.id}}">สร้างภาพ</button>
        <button class="btn small primary" data-pick="${{c.id}}" style="display:none">แก้ไข/ส่งออก</button>
      </div>`;
    wrap.appendChild(div);
    const opt = document.createElement("option"); opt.value = c.id; opt.textContent = c.name;
    oSel.appendChild(opt);
  }}
  wrap.querySelectorAll("[data-render]").forEach(b => b.addEventListener("click", () => renderConcept(b.dataset.render)));
  wrap.querySelectorAll("[data-pick]").forEach(b => b.addEventListener("click", () => selectConcept(b.dataset.pick)));
}}

async function renderConcept(id) {{
  const btn = document.querySelector(`[data-render="${{id}}"]`);
  btn.disabled = true; btn.textContent = "กำลังวาด...";
  try {{
    const data = await call("/api/render", {{key: state.key, concept_id: id}});
    const img = document.getElementById("img_" + id);
    img.src = data.url; img.style.display = "";
    document.querySelector(`[data-pick="${{id}}"]`).style.display = "";
    btn.textContent = "วาดใหม่";
  }} catch (err) {{
    alert("สร้างภาพไม่สำเร็จ: " + err.message);
  }} finally {{ btn.disabled = false; }}
}}

function selectConcept(id) {{
  state.active = id;
  document.querySelectorAll(".concept").forEach(d => d.classList.remove("active"));
  document.getElementById("concept_" + id).classList.add("active");
  const c = state.concepts.find(x => x.id === id);
  document.getElementById("t_text").value = c.thai_text;
  state.text = Object.assign({{}}, state.text, {{text: c.thai_text}});
  state.crop = Object.assign({{}}, {json.dumps(DEFAULT_CROP)});
  document.getElementById("c_zoom").value = 100;
  setAnchor(state.text.anchor);
  document.getElementById("editor").style.display = "";
  document.getElementById("editor").scrollIntoView({{behavior:"smooth"}});
  refreshPreview();
}}

const ANCHORS = ["top-left","top-center","top-right","center-left","center-center","center-right",
                  "bottom-left","bottom-center","bottom-right"];
const ARROWS = ["\\u2196","\\u2191","\\u2197","\\u2190","\\u00b7","\\u2192","\\u2199","\\u2193","\\u2198"];
(function buildAnchorGrid() {{
  const g = document.getElementById("anchorGrid");
  ANCHORS.forEach((a, i) => {{
    const b = document.createElement("button"); b.textContent = ARROWS[i]; b.dataset.anchor = a;
    b.addEventListener("click", () => {{ setAnchor(a); refreshPreview(); }});
    g.appendChild(b);
  }});
}})();
function setAnchor(a) {{
  state.text.anchor = a;
  document.querySelectorAll("#anchorGrid button").forEach(b => b.classList.toggle("on", b.dataset.anchor === a));
}}
setAnchor("bottom-center");

function readControls() {{
  state.text.text = document.getElementById("t_text").value;
  state.text.size = parseInt(document.getElementById("t_size").value, 10);
  state.text.color = document.getElementById("t_color").value;
  state.text.outline = document.getElementById("t_outline").checked;
  state.text.shadow = document.getElementById("t_shadow").checked;
  state.text.scrim = document.getElementById("t_scrim").checked;
  state.crop.zoom = parseInt(document.getElementById("c_zoom").value, 10) / 100;
}}

let previewTimer = null;
function refreshPreview() {{
  clearTimeout(previewTimer);
  previewTimer = setTimeout(async () => {{
    readControls();
    try {{
      const data = await call("/api/preview", {{key: state.key, concept_id: state.active, crop: state.crop, text: state.text}});
      document.getElementById("previewImg").src = data.url;
      document.getElementById("feedImg").src = data.url;
      document.getElementById("feedTitle").textContent = (document.getElementById("title").value || "ชื่อวิดีโอ");
    }} catch (err) {{ /* ignore transient errors while the base image is still rendering */ }}
  }}, 180);
}}
["t_text","t_size","t_color"].forEach(id => document.getElementById(id).addEventListener("input", refreshPreview));
["t_outline","t_shadow","t_scrim"].forEach(id => document.getElementById(id).addEventListener("change", refreshPreview));
document.getElementById("c_zoom").addEventListener("input", refreshPreview);
document.getElementById("previewImg").addEventListener("click", (e) => {{
  const r = e.target.getBoundingClientRect();
  state.crop.fx = (e.clientX - r.left) / r.width;
  state.crop.fy = (e.clientY - r.top) / r.height;
  refreshPreview();
}});

document.getElementById("exportBtn").addEventListener("click", async () => {{
  const err = document.getElementById("exportErr"), status = document.getElementById("exportStatus");
  err.textContent = ""; status.textContent = "กำลังส่งออก...";
  readControls();
  try {{
    const fmt = document.getElementById("exportFmt").value, res = document.getElementById("exportRes").value;
    const data = await call("/api/export", {{key: state.key, concept_id: state.active, crop: state.crop,
                                               text: state.text, format: fmt, resolution: res}});
    status.textContent = `เสร็จแล้ว: ${{data.w}}x${{data.h}}, ${{(data.bytes/1e6).toFixed(2)}} MB`;
    await loadStore();
  }} catch (e2) {{ err.textContent = "ส่งออกไม่สำเร็จ: " + e2.message; status.textContent = ""; }}
}});

document.getElementById("outcomeBtn").addEventListener("click", async () => {{
  const payload = {{key: state.key, concept_id: document.getElementById("o_concept").value,
    impressions: document.getElementById("o_impr").value || null,
    ctr: document.getElementById("o_ctr").value || null,
    watch_time_pct: document.getElementById("o_watch").value || null,
    traffic_source: document.getElementById("o_src").value || null,
    note: document.getElementById("o_note").value || null}};
  try {{ await call("/api/outcome", payload); await loadStore();
    document.getElementById("o_impr").value = ""; document.getElementById("o_ctr").value = "";
    document.getElementById("o_watch").value = ""; document.getElementById("o_note").value = "";
  }} catch (err) {{ alert("บันทึกไม่สำเร็จ: " + err.message); }}
}});

async function loadStore() {{
  if (!state.key) return;
  const s = await fetch("/api/store?key=" + encodeURIComponent(state.key)).then(r => r.json());
  state.store = s;
  const erows = document.getElementById("exportRows"); erows.innerHTML = "";
  for (const e of (s.exports || []).slice().reverse()) {{
    const tr = document.createElement("tr");
    tr.innerHTML = `<td>${{(e.exported_at||"").replace("T"," ").slice(0,16)}}</td><td>${{e.concept_id}}</td>
      <td><a href="${{e.url}}" download>${{e.filename}}</a></td><td>${{(e.bytes/1e6).toFixed(2)}} MB</td>`;
    erows.appendChild(tr);
  }}
  const orows = document.getElementById("outcomeRows"); orows.innerHTML = "";
  for (const o of (s.outcomes || []).slice().reverse()) {{
    const tr = document.createElement("tr");
    tr.innerHTML = `<td>${{(o.recorded_at||"").replace("T"," ").slice(0,16)}}</td><td>${{o.concept_id}}</td>
      <td>${{o.impressions ?? "-"}}</td><td>${{o.ctr ?? "-"}}</td><td>${{o.watch_time_pct ?? "-"}}</td>
      <td>${{o.traffic_source ?? "-"}}</td><td>${{o.note ?? ""}}</td>`;
    orows.appendChild(tr);
  }}
}}
</script>
</body></html>""".encode("utf-8")


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        url = urlparse(self.path)
        if url.path == "/":
            self._send(200, _page(), "text/html; charset=utf-8")
        elif url.path == "/api/store":
            key = parse_qs(url.query).get("key", [""])[0]
            self._json(200, T.load_store(key) if key else {})
        elif url.path.startswith("/asset/"):
            self._send_asset(url.path[len("/asset/"):])
        else:
            self.send_error(404)

    def do_POST(self):
        host = self.headers.get("Host", "")
        if self.headers.get("Origin") not in (f"http://{host}",):
            return self._json(403, {"error": "forbidden"})
        try:
            length = int(self.headers.get("Content-Length", 0))
            payload = json.loads(self.rfile.read(length) or b"{}")
            path = urlparse(self.path).path
            handler = {
                "/api/episode_text": self._episode_text,
                "/api/analyze": self._analyze,
                "/api/render": self._render,
                "/api/preview": self._preview,
                "/api/export": self._export,
                "/api/outcome": self._outcome,
            }.get(path)
            if handler is None:
                return self._json(404, {"error": "not found"})
            handler(payload)
        except KeyError as exc:
            self._json(404, {"error": f"ไม่พบ: {exc}"})
        except PipelineError as exc:
            self._json(502, {"error": str(exc)})
        except Exception as exc:  # noqa: BLE001 - surface as a readable API error, not a stack trace
            self._json(500, {"error": str(exc)})

    # --- handlers --------------------------------------------------------------------

    def _episode_text(self, payload):
        settings = get_settings()
        episode_id = payload["episode_id"]
        opt = next((e for e in T.episode_options() if e["key"] == episode_id), None)
        if opt is None:
            raise KeyError(episode_id)
        transcript = T.episode_transcript(settings, episode_id)
        summary = transcript or f"{opt['topic']}\n\nธีม: {opt['theme']}"
        self._json(200, {"title": opt["title"], "summary": summary})

    def _analyze(self, payload):
        settings = get_settings()
        title, summary = payload["title"].strip(), payload["summary"].strip()
        episode_id = payload.get("episode_id") or None
        key = episode_id or T.slug_for(title)
        analysis = T.analyze_story(settings, title, summary)
        store = _new_store_from_analysis(key, episode_id, title, analysis, analysis.concepts)
        T.save_store(key, store)
        self._json(200, {"key": key, "analysis": store["analysis"], "concepts": store["concepts"]})

    def _render(self, payload):
        key, concept_id = payload["key"], payload["concept_id"]
        w, h = int(payload.get("w", 1920)), int(payload.get("h", 1080))
        store = T.load_store(key)
        concept = _concept_by_id(store, concept_id)
        img = T.render_concept(concept, w, h)
        name = f"{concept_id}_base.png"
        img.save(T.store_dir(key) / name, "PNG")
        store.setdefault("concept_settings", {}).setdefault(concept_id, {})["base"] = {"w": w, "h": h}
        T.save_store(key, store)
        self._json(200, {"url": f"/asset/{quote(key)}/{name}"})

    def _edited_image(self, store, concept_id, crop, text_settings, w=1920, h=1080):
        concept = _concept_by_id(store, concept_id)
        img = T.render_concept(concept, w, h)
        img = T.apply_crop(img, crop.get("fx", 0.5), crop.get("fy", 0.5), crop.get("zoom", 1.0))
        size = max(10, round(text_settings.get("size", 96) * h / 1080))
        return T.compose_text(
            img, text_settings.get("text", ""), size=size, bold=text_settings.get("bold", True),
            color=text_settings.get("color", "#FFFFFF"), outline=text_settings.get("outline", True),
            outline_color=text_settings.get("outline_color", "#2B2016"),
            shadow=text_settings.get("shadow", True), scrim=text_settings.get("scrim", True),
            anchor=text_settings.get("anchor", "bottom-center"))

    def _preview(self, payload):
        key, concept_id = payload["key"], payload["concept_id"]
        store = T.load_store(key)
        store.setdefault("concept_settings", {}).setdefault(concept_id, {})
        store["concept_settings"][concept_id]["crop"] = payload.get("crop", {})
        store["concept_settings"][concept_id]["text"] = payload.get("text", {})
        T.save_store(key, store)
        img = self._edited_image(store, concept_id, payload.get("crop", {}), payload.get("text", {}), 960, 540)
        self._json(200, {"url": "data:image/png;base64," + _b64_png(img)})

    def _export(self, payload):
        key, concept_id = payload["key"], payload["concept_id"]
        fmt = payload.get("format", "jpeg")
        w, h = (3840, 2160) if payload.get("resolution") == "4k" else (1920, 1080)
        store = T.load_store(key)
        img = self._edited_image(store, concept_id, payload.get("crop", {}), payload.get("text", {}), w, h)
        ext = "jpg" if fmt == "jpeg" else "png"
        name = f"{concept_id}_{payload.get('resolution', 'hd')}_{int(datetime.now().timestamp())}.{ext}"
        path = T.store_dir(key) / name
        T.export_image(img, path, fmt)
        store.setdefault("exports", []).append({
            "concept_id": concept_id, "filename": name, "url": f"/asset/{quote(key)}/{name}",
            "format": fmt, "w": w, "h": h, "bytes": path.stat().st_size,
            "exported_at": datetime.now().isoformat(timespec="seconds")})
        T.save_store(key, store)
        self._json(200, {"url": f"/asset/{quote(key)}/{name}", "bytes": path.stat().st_size, "w": w, "h": h})

    def _outcome(self, payload):
        key = payload["key"]
        store = T.load_store(key)
        store.setdefault("outcomes", []).append({
            "concept_id": payload.get("concept_id"), "impressions": payload.get("impressions"),
            "ctr": payload.get("ctr"), "watch_time_pct": payload.get("watch_time_pct"),
            "traffic_source": payload.get("traffic_source"), "note": payload.get("note"),
            "recorded_at": datetime.now().isoformat(timespec="seconds")})
        T.save_store(key, store)
        self._json(200, {"outcomes": store["outcomes"]})

    # --- plumbing ----------------------------------------------------------------------

    def _send_asset(self, rel):
        key, _, name = unquote(rel).partition("/")
        path = T.store_dir(key) / name
        if not path.is_file():
            return self.send_error(404)
        ctype = "image/jpeg" if path.suffix.lower() in (".jpg", ".jpeg") else "image/png"
        data = path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Disposition", f"inline; filename*=UTF-8''{quote(name)}")
        self.end_headers()
        self.wfile.write(data)

    def _send(self, status, data, ctype):
        self.send_response(status)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def _json(self, status, obj):
        self._send(status, json.dumps(obj, ensure_ascii=False).encode("utf-8"), "application/json; charset=utf-8")

    def log_message(self, *args):
        pass


def main():
    server = ThreadingHTTPServer(("127.0.0.1", PORT), Handler)
    url = f"http://127.0.0.1:{server.server_address[1]}/"
    print(f"Thumbnail Studio: {url}  (Ctrl+C to stop)", flush=True)
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
