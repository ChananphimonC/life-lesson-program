# visual_poc — ภาพสตอรี่บอร์ดพิสูจน์แนวคิด "พับให้ถึงดวงจันทร์"

ทุกอย่างอยู่ในโฟลเดอร์นี้ ไม่มีไฟล์ภายนอกถูกแก้ ไม่มี API ไม่มีการติดตั้ง

## ดูผลที่ไหน
| อะไร | ไฟล์ |
|---|---|
| ภาพรวมซีน A (10 ช็อต พร้อมเวลา) | `scene_a_paper_roll/storyboard_sheet.png` |
| ภาพรวมซีน B (8 ช็อต) | `scene_b_bowls/storyboard_sheet.png` |
| เฟรมเต็มขนาด 1280×720 | `scene_a_paper_roll/frames/A01–A10.png`, `scene_b_bowls/frames/B01–B08.png` |
| Animatic (กล้องเคลื่อนบนเฟรมนิ่ง ไม่มีเสียง ไม่มีตัวละครขยับ) | `scene_a_paper_roll/scene_a_animatic.mp4` (36.8 วิ), `scene_b_bowls/scene_b_animatic.mp4` (30.0 วิ) ตรวจด้วย ffprobe: H.264, yuv420p, 1280×720, 24 fps, ถอดรหัสได้ครบ |
| ตัวละครแทนชั่วคราว | `chars_sheet.png` |
| รายละเอียดช็อต | `VISUAL_STORYBOARD.md` |
| ประเมิน | `VISUAL_EVALUATION.md` |

เปิดวิดีโอด้วยโปรแกรมเล่นวิดีโอทั่วไป หรือ `ffplay scene_a_paper_roll/scene_a_animatic.mp4`

## สร้างใหม่
```
cd experiments/storytelling_stress_test/production_feasibility/visual_poc
python scene_a.py        # เฟรม A
python scene_b.py        # เฟรม B
python sheets.py         # ภาพรวมพร้อมเวลา
python animatic.py       # MP4 สองไฟล์ (ต้องมี ffmpeg)
python poc_chars.py      # ตัวละครแทนชั่วคราว
```
ต้องการ Pillow และ numpy (มีอยู่ในโครงการแล้ว) โค้ดเรียกโมดูลจาก `experiments/prototype_v2/` โดยไม่แก้ไฟล์ (เพิ่มตัวละครใหม่ในหน่วยความจำของโปรเซสนี้เท่านั้น ดู docstring ใน `poc_chars.py`)

## ไฟล์โค้ด
`poc_chars.py` (ตัวละครแทน 4 ตัว), `stage.py` (ฉาก แถบกระดาษ ก้อน ชาม), `scene_a.py`, `scene_b.py`, `animatic.py`, `sheets.py`, `contact.py`

## ข้อจำกัดที่ต้องรู้
- ต้น ยายแก้ว ลุงโชค ป้าเอื้อน **ไม่ใช่ดีไซน์ที่อนุมัติ** (เดิมอนุมัติเฉพาะปิ่นและแม่)
- เป็นเฟรมนิ่ง ไม่ใช่แอนิเมชัน ตัดสินจังหวะตลกไม่ได้
- ซีน A ใช้ม้วนกว้าง 2 ม. (v2 ระบุ 0.30 ม.) เพื่อให้ก้อนหลังพับไม่เล็กเท่าอิฐ ต้องแก้บทถ้าเลือกทางนี้
- ภาพ "พับครั้งที่ 11 ไม่ลง" เป็นภาพสื่อความหมายจากแบบจำลองในอุดมคติ ไม่ได้ทดสอบกับกระดาษจริง
