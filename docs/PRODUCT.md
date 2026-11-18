# Product Specification: Life Lesson Program

## 1. Product Vision
An AI-assisted content generation system that creates original, 3-5 minute Thai "life reflection" audio-visual episodes. It provides a calm, non-judgmental space for listeners to process their daily experiences, acting as a mirror for their thoughts rather than a guide telling them what to do.

## 2. Target Audience
- Thai-speaking Millennials and Gen Z (18–40 years old).
- Individuals navigating urban life, career burnout, relationship complexities, and quarter-life crises.
- People seeking comfort, validation, and a moment of pause, not lectures or toxic positivity.

## 3. Content Philosophy (Core Principle)

### 3.1 Definition: LIFE REFLECTION vs. LIFE ADVICE
The product's entire value proposition rests on staying on the "reflection" side of this line. Every prompt, Critic rule, and QA checklist item must be traceable back to it.

**LIFE REFLECTION (what we make):**
- Observes an experience or feeling without resolving it.
- Explores *why* something feels the way it feels.
- Offers a perspective or a different angle — never a fix.
- Leaves interpretation to the listener; the ending stays open.
- Trusts the listener to draw their own conclusion.

**LIFE ADVICE / MOTIVATIONAL CONTENT (what we explicitly avoid):**
- Tells the listener what to do, feel, or believe.
- Promises that adopting a mindset, habit, or perspective will resolve the problem.
- Closes with a resolution, a lesson "learned," or a call to action.
- Borrows authority from a teacher, book, or tradition instead of standing on its own observation.

### 3.2 The System DOES NOT
- Teach religion or quote religious texts (e.g., no Buddha quotes, no dharma teachings).
- Quote or attribute statements to famous people, books, or public figures — including paraphrased or recognizably derivative versions of well-known quotes.
- Reproduce or lightly reword existing motivational content ("copied or derivative motivational content").
- Give therapy, diagnose mental health conditions, or make clinical/medical claims.
- Give prescriptive life advice or tell the listener what they "should," "must," or "need to" do.
- Promise that a particular mindset, habit, or perspective will solve the listener's problem.
- Rely on generic motivational clichés (e.g., "Don't give up," "Tomorrow is a new day").
- Use manipulative or preachy language (guilt-tripping, faux-inspirational urgency, rhetorical pressure to change).

### 3.3 The System SHOULD
- Observe everyday human experiences (loneliness, failure, self-worth, comparison).
- Explore emotions and situations deeply, without rushing to resolve them.
- Tell relatable, grounded stories or observations.
- Offer perspectives rather than instructions.
- Leave room for the listener to interpret and reflect.
- Feel calm, intimate, conversational, and human.
- End with an open-ended reflection rather than a motivational conclusion.

### 3.4 Originality: Two Distinct Concerns
The system must guard against two different kinds of "not original," and they are solved differently:

- **A. Repetition against the project's own back catalog** — the same angle or observation reused across episodes. Solved with an in-project similarity check (see ARCHITECTURE.md, deferred to the milestone where it becomes necessary).
- **B. Resemblance to external/copyrighted/attributed material** — quoting or closely paraphrasing religious texts, famous quotes, published authors, or existing motivational content. Solved primarily through generation constraints and the Critic's explicit quote/attribution checks (see AI_DESIGN.md), not through a large external plagiarism-detection system. MVP does not build a full external corpus-matching system; the Critic's job is to catch recognizable copied phrasing and attributed statements before they reach a human.

## 4. Human-in-the-Loop Requirement
The AI is an engine, not the final decision-maker.
- AI generates topics, scripts, and media.
- The automated Critic performs the first pass of tone/content-philosophy QA (see AI_DESIGN.md).
- **MVP assumption: a single human reviewer (the project owner)** performs final QA on script tone, anti-advice/anti-quote compliance, and approves the final video before publishing. The Streamlit dashboard is designed as a single-user review tool for this stage of the product; multi-reviewer workflows are out of scope for MVP.
- Any episode that fails automated Critic review after the maximum rewrite attempts is routed to the human reviewer for manual handling rather than being discarded or force-published (see AI_DESIGN.md §4 for the FAILED_REVIEW state).

## 5. Sensitive Topics Policy
Because the target emotional territory (loneliness, burnout, self-worth, comparison) sits near topics that require care, the product explicitly does not attempt to handle:
- Self-harm or suicidal ideation.
- Severe mental-health crisis.
- Abuse.
- Any topic requiring medical/clinical claims or professional diagnosis.

The system must never generate instructions, encouragement, or narrative detail related to these topics, must never imply it is providing professional/clinical help, and must not attempt to diagnose. Detection and handling of these topics is a pipeline-level safeguard, not a purely stylistic Critic concern — see AI_DESIGN.md §6 and ARCHITECTURE.md for where this sits in the pipeline.

---

## 6. ซีรีส์ที่ 2: "รู้หรือไม่ / ทำไม" (เล่าเรื่องความรู้ แนวนอน 16:9)

> เพิ่มเมื่อ 2026-10-23 รายละเอียดเชิงเทคนิคอยู่ที่ REQUIREMENTS.md (FR-4, FR-5, FR-6)

### 6.1 แนวคิด
วิดีโอการ์ตูนแนวนอนที่ **มีผู้เล่าเรื่อง 1 คน** พาคนดูไปรู้จักเรื่องที่น่าสงสัย สนุก และเอาไปใช้ได้จริง มีตัวละครการ์ตูนแสดงประกอบ
- ตัวละครขยับท่าทางและขยับปากได้ แต่ **ไม่จำเป็นต้องพูดเอง** เสียงหลักคือผู้เล่าคนเดียว
- มีภาพเคลื่อนไหวประกอบ (กราฟิก ไอคอน ตัวเลข ฉาก) ช่วยให้เข้าใจ
- ลายเส้นเดียวกับ Life Lesson: เส้นน้ำตาลอุ่น บาง มุมโค้งมน แขนเรียว เงาอ่อน ไม่แข็งทื่อ

### 6.2 ตัวอย่างหัวข้อ
- เอาตัวรอดในยุคเศรษฐกิจไม่ดี
- รู้หรือไม่ MBTI มาจากไหน แม่นแค่ไหน
- ธาตุในปาจื่อ (ดวงจีน) กับคนที่เข้ากัน และอาหารที่เชื่อกันว่าเสริมธาตุ
- อีก 50 ปี หุ่นยนต์ครองโลก เราจะใช้ชีวิตยังไง
- เรื่องเล่าแนวลึกลับ/ผี (เล่าแบบนิทาน ไม่อ้างว่าเป็นเรื่องจริง)

### 6.3 หลักเนื้อหา (ต่างจาก Life Lesson)
ซีรีส์นี้ **ให้ข้อมูลและคำแนะนำได้** ไม่ต้องจบแบบปลายเปิดเหมือน Life Lesson แต่ต้องซื่อตรงกับข้อเท็จจริง:
- **เรื่องที่เป็นความรู้ต้องค้นข้อมูลก่อนเขียนบท** ใส่แหล่งอ้างอิงในสคริปต์ (`sources[]`) และไม่พูดเกินหลักฐาน
- **ความเชื่อ/ศาสตร์ที่ไม่ใช่วิทยาศาสตร์** (ปาจื่อ ดวงจีน โหราศาสตร์) เล่าในฐานะ "ความเชื่อ/ตำรา" เสมอ เช่น "ตามตำราปาจื่อเชื่อว่า..." ห้ามพูดเหมือนเป็นข้อเท็จจริงทางวิทยาศาสตร์
- **MBTI และแบบทดสอบบุคลิกภาพ** บอกทั้งที่มา ประโยชน์ และข้อจำกัดตามงานวิจัย
- **อนาคต/สมมติ** (หุ่นยนต์ครองโลก) บอกชัดว่าเป็นการคาดการณ์หรือจินตนาการ แยกจากสิ่งที่เกิดขึ้นจริงแล้ว
- **การเงิน** ให้หลักการทั่วไปได้ แต่ไม่แนะนำให้ซื้อ/ขายหลักทรัพย์ใดเป็นการเฉพาะ
- **สุขภาพ/อาหาร** ต้องมีแหล่งอ้างอิง และไม่อ้างว่ารักษาโรคได้
- นโยบายหัวข้ออ่อนไหวใน §5 ยังใช้กับซีรีส์นี้ทั้งหมด

### 6.4 น้ำเสียงผู้เล่า
ผู้เล่าคนเดียว แต่ **เปลี่ยนโทนเสียงตามเนื้อหา** ทั้งตอนและรายช่วง:
- เรื่องผี/ลึกลับ: เบา ช้า เหมือนกระซิบ
- เรื่องน่ารู้: สนุก มีชีวิตชีวา ชวนสงสัย
- คำแนะนำ: อบอุ่น ชัดเจน น่าเชื่อถือ
- ออกเสียงคำไทยให้ชัดและถูกเหมือน Life Lesson (ใช้ Gemini TTS เป็นหลัก)

---

## 7. คลังวิดีโอและเพลย์ลิสต์

> เพิ่มเมื่อ 2026-10-23 รายละเอียดอยู่ที่ REQUIREMENTS.md (FR-2, FR-6)

หน้าคลัง (`preview.py`) คือที่จัดการวิดีโอทุกซีรีส์:
- **เพลย์ลิสต์:** Life Lesson (16:9), Shorts (9:16), รู้หรือไม่ (16:9) และเพลย์ลิสต์ที่ผู้ใช้สร้างเอง
- **จัดการเพลย์ลิสต์:** เพิ่ม เปลี่ยนชื่อ ลบ (ลบได้เมื่อว่าง) และย้ายคลิปไปเพลย์ลิสต์อื่น
- **ทุกคลิปในทุกเพลย์ลิสต์:** ดูได้ ดาวน์โหลด MP4 ได้ เปลี่ยนชื่อและลบได้ มีรูปปกที่สร้าง แก้ และดาวน์โหลดได้เหมือนฝั่ง Life Lesson

### รูปปกคลิป (หลักการ)
> เพิ่มเมื่อ 2026-10-23 รายละเอียดอยู่ที่ REQUIREMENTS.md (FR-7)

- **ทำปกหลังวิดีโอเสร็จ** เพื่อให้ปกสะท้อนเนื้อหาจริง ไม่ใช่เดาจากชื่อ
- **ปกต้องบอกว่าวิดีโอเกี่ยวกับอะไร:** คำสำคัญของเรื่อง (เช่น MBTI) ต้องอยู่บนปก ไม่ใช้ปกกว้างๆ ที่ใช้กับเรื่องไหนก็ได้
- **สีและอารมณ์ต้องตรงกับวิดีโอ:** เรื่องสดใสใช้สีสด เรื่องเศร้าหรือน่ากลัวใช้โทนหม่นหรือมืด ห้ามเอาปกเศร้าไปแปะวิดีโอสนุก หรือกลับกัน
- **ซีรีส์รู้หรือไม่:** มีน้องปิ่นพิธีกรกับหมา 5 ตัวบนปก พร้อมกราฟิกของหัวข้อนั้น
- **ดึงดูดแต่ไม่หลอก:** คำบนปกต้องตรงกับสิ่งที่วิดีโอเล่าจริง

### พิธีกรของซีรีส์ "รู้หรือไม่"
- **น้องปิ่น** (ในไฟล์ตัวละครใช้ id `host_mint` เดิมเพื่อไม่ให้แคชเสียงและสคริปต์เสีย): สาวผมยาวแว่นกลม ใส่ฮู้ดสีเขียวมิ้นต์ ร่าเริง ชอบเล่าเรื่องสุดๆ
- เลี้ยงหมา 5 ตัว: ลูกตาล, สาคู (ผู้ชาย), แพนด้า, ลูกจิ๋ว, แพนดี้ (ตัวที่เหลือเป็นผู้หญิง) ใช้เป็นตัวประกอบในฉากและบนปกได้

### รูปแบบตอนของซีรีส์ "รู้หรือไม่" (เพิ่ม 2026-10-24)
ซีรีส์มี 2 รูปแบบ เลือกตามเนื้อหา:
1. **เชิงให้ความรู้ (explainer)** เช่น MBTI, ธาตุปาจื้อ: **น้องปิ่นปรากฏตัวเป็นผู้บรรยาย** ปากขยับตามเสียงพูดตามปกติ **ตัวยืนอยู่กับที่ ไม่ขยับเท้า/ไม่เดิน** (ขยับแค่ปาก หน้า ท่ามือ และโยกตัวเล็กน้อย) ตัวละครอื่นแสดงประกอบ ปากไม่ต้องพูด
2. **เชิงเปรียบเทียบ/เล่าเรื่อง (story)** เช่น เด็กจบใหม่เงินเดือน 28,000 vs 40,000: **ไม่ต้องมีน้องปิ่น** ใช้ผู้เล่าเรื่องที่ไม่ปรากฏตัว (ตัวละคร `storyteller`) ตัวละครในเรื่องแสดงตามบท มีตารางและกราฟเปรียบเทียบขึ้นตามจังหวะเล่า จบด้วยกลยุทธ์ที่เอาไปใช้ได้จริง และบอกชัดว่าตัวเลขเป็นตัวอย่างสมมติ
- ปกของแบบที่ 1 ใช้น้องปิ่นกับหมา 5 ตัว ปกของแบบที่ 2 ใช้ตัวละครเอกของเรื่อง
- **ตอนแบบเปรียบเทียบต้อง "ดูเพลิน":** เล่าเป็นฉากชีวิตจริงในเมืองใหญ่ (เดินทาง ที่พัก กิน) แบ่งเฟรมซ้าย-ขวาให้เห็นชีวิตของสองคนพร้อมกัน ตัวเลขเป็นป้ายเล็กตามจังหวะพูด ตารางอยู่มุมเดียว ข้อมูลให้พอดี ไม่ยัดเยียด แต่จบด้วยกลยุทธ์ที่เอาไปใช้ได้จริง
- **ตัวละครต้องน่ารักและขยับนุ่ม:** สัดส่วนหัวโตตัวสั้น แขนโค้งต่อเนื่อง ไม่เป็นท่อนทรงกระบอก ยืนนิ่งแบบธรรมชาติ ไม่เด้ง
- **ข้อเท็จจริงล่าสุดที่ต้องตรวจเสมอ:** ประกันสังคม ม.33 หัก 5% เพดานค่าจ้าง 17,500 บาท สมทบสูงสุด **875** บาท/เดือน ตั้งแต่ 1 ม.ค. 2569 (เดิม 750); ค่าโดยสาร MRT สายสีน้ำเงิน 17–44 บาท ตั้งแต่ 3 ก.ค. 2569; BTS สายสุขุมวิทหลัก 17–47 บาท ตั้งแต่ 1 ม.ค. 2566 (ส่วนต่อขยายคิดแยกตามระยะ ตรวจกับ bts.co.th ก่อนระบุราคาสถานีเฉพาะ)

### แนวการวาดตัวละคร (บันทึกถาวร 2026-10-25 ตามผู้ใช้สั่ง)
**หลักใหญ่: ห้ามเอารูปทรงเรขาคณิตมาต่อกัน** (วงกลม ครึ่งวงกลม สี่เหลี่ยม ท่อนกระบอก) เพราะดูแข็ง ดูเป็น AI และต้องกลับมาแก้ทีหลัง ทุกครั้งที่ออกแบบตัวละครหรือของประกอบใหม่ ให้คิดแบบนักออกแบบวิดีโอชื่อดังที่ทำให้น่าจดจำและไม่ซ้ำจำเจ และ **หาข้อมูลก่อนวาด** (ค้นเว็บ หรือถาม Gemini เรื่องสัดส่วน สี ทรงผม ชุด) ไม่วาดมั่ว
- **สัดส่วน:** ประมาณ 3 หัวต่อความสูง **คอสั้นนุ่ม** (ไม่ยาวแบบกระสือ) ไหล่แคบ เอวคอดเล็กน้อย ลำตัวไม่อ้วนท้วม แขนขาเรียวลงหาข้อมือข้อเท้า
- **หน้า:** ทรงไข่ คางเล็ก ตาโตเงา มีเส้นหนังตาบน (ผู้หญิงมีขนตา) คิ้วบาง จมูกเป็นเส้นสั้น ๆ ปากเล็ก แก้มระเรื่อ หน้าหวาน
- **ผิว:** สีเนื้อขาวอมชมพูอ่อน (เช่น `#F9DDCB`, ผู้ชายเข้มขึ้นนิด `#F3D2B8`) ไม่เหลืองจัด
- **มือ/หู/แขน:** มือเล็กเรียว ฝ่ามือนุ่ม นิ้วชิดกัน นิ้วโป้งแยก; หูเป็นเส้นโค้งหยักธรรมชาติพร้อมขอบใน ไม่ใช่วงรี; แขนเป็นเส้นโค้งเดียว ไม่แบ่งเป็นท่อนต่อกัน มีรอยพับข้อศอก
- **ผม:** เป็นก้อนผมซ้อนชั้นมีไฮไลต์โค้ง ผู้หญิงผมยาวประบ่าปลายม้วนเข้า มีลอนกรอบหน้า หน้าม้าปัดข้างและกิ๊บติดผม; ผู้ชายผมสั้นเซ็ตปัดข้าง
- **แต่งตัวให้เข้ากับบริบท:** ตอนวัยทำงานในเมือง ผู้หญิงแต่งสวย (เสื้อเชิ้ตสีฟ้าคอปกบัว เข็มขัดเส้นเล็ก กระโปรงทรงดินสอ รองเท้าคัทชูส้นเตี้ย) ผู้ชายแต่งแบบผู้ชาย (เสื้อเชิ้ตพับแขน เข็มขัด กางเกงสแลค รองเท้าหนัง) ทั้งคู่ห้อยบัตรพนักงาน; สีเสื้อสื่อชื่อ (ฟ้า = ฟ้า, ต้น = เขียวใบไม้); เปลี่ยนชุดตามเนื้อเรื่องเสมอ ไม่ใส่ชุดเดียวทุกฉาก
- **เส้น/เงา:** เส้นขอบสีน้ำตาลอุ่นไม่ดำสนิท ความหนาไม่เท่ากันได้ รอยยับเสื้อผ้าเป็นเส้นโค้งอิสระ ไม่ใช่ขีดตรง เงา/ไฮไลต์ไม่ตัดขอบแข็ง
- **อาหารและของประกอบ:** ต้องมีรายละเอียดจริง (หมูปิ้งมีรอยไหม้และเงาเคลือบ, กระติบข้าวเหนียวสาน, กาแฟเย็นมีน้ำแข็งชั้นนม, ไข่ดาว) ไม่ใช่ก้อนสีเรียบ
- **การขยับ:** นุ่ม ไม่เด้งตามเสียง ไม่ตัดฉากแข็ง ไม่ทำท่าเดียวซ้ำทั้งคลิป
- **ที่มา:** คำแนะนำจาก Gemini (3.5 หัว, คอ ~0.2 หัว, กฎ "ห้ามวงกลม/ครึ่งวงกลม/สี่เหลี่ยมตรง ๆ", ชุดทำงาน) ปรับเป็น 3 หัวให้น่ารักขึ้น และคู่มือวาดตัวการ์ตูนแนว chibi/flat vector (ลำตัวทรงถั่ว/โค้งตามกระดูกสันหลัง แขนขาเรียวนุ่ม)
- โค้ด: `experiments/shorts/character_soft.py` (สไตล์ `cute` ใน `characters/<id>.json`)

### ตอนเรื่องความเชื่อ + สุขภาพ (เพิ่ม 2026-10-27, ตอน `know_craving` แพ้ท้องอยากกินของแปลก)
- โครงเรื่อง: เล่าจากเรื่องจริงในครอบครัวของน้องปิ่น (คุณยายกินทุเรียน, แม่ท้องพี่สาวอยากชาบู+ตับลวก, แม่ท้องปิ่นอยากตำผลไม้+โอเลี้ยง) → **ความเชื่อโบราณ** → **ทฤษฎีในอินเทอร์เน็ต** → **วิทยาศาสตร์** → **ข้อควรระวังด้านความปลอดภัย** → สรุปด้วยความอบอุ่น
- **แยก "ความเชื่อ" ออกจาก "หลักฐาน" ให้ชัดเสมอ:** ความเชื่อเล่าตามต้นฉบับอย่างให้เกียรติ (ระบุว่าเป็นตำราโบราณ ไม่ใช่การแพทย์สมัยใหม่ ไม่ตัดสินว่าเด็กดีหรือไม่ดี) แล้วตามด้วยสิ่งที่วิทยาศาสตร์พบ พร้อมระดับหลักฐาน (ตัวชี้วัด "หลักฐานสนับสนุน") และงานที่เป็นแค่ "สัญญาณ" ต้องบอกว่ากลุ่มตัวอย่างเล็ก
- เรื่องสุขภาพต้องมีคำเตือนท้ายตอนว่าเป็นความรู้ทั่วไป ไม่ใช่คำแนะนำแทนแพทย์ และห้ามพูดเกินหลักฐาน (เช่น ไม่บอกว่าความอยากกินทายเพศลูกได้)
- ตัวละครครอบครัวใช้สไตล์เดียวกัน: น้องปิ่นฮู้ดเขียวมิ้นต์+แว่น, แม่ผมบ๊อบเดรสเหลือง (ท้อง), คุณยายผมเทาเกล้ามวย เสื้อลายดอก นุ่งผ้าถุง
