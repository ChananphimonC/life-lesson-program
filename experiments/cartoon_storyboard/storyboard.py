"""Hand-authored storyboards, one per episode.

EP01 aa1899f7: "วันที่เรารู้สึกว่าเดินช้ากว่าคนอื่น".

Each scene starts at an anchor phrase in its script block ("" = block start).
Events are phrases inside the scene that trigger an on-screen beat (a card
popping in, a question mark appearing, the camera tilting...). All times are
resolved against the real narration audio by `timing.py`.
"""

EP01 = {
    1: [
        ("morning_phone", "", {}),
        ("others_running", "ก็เหมือนกับการมองเห็น", {}),
    ],
    2: [
        ("feed_success", "", {
            "trophy": "เราเห็นข่าวความสำเร็จ",
            "house": "บางคนมีบ้าน",
            "car": "มีรถ",
            "briefcase": "มีตำแหน่ง",
            "life": "หรือมีชีวิต",
        }),
        ("walking_behind", "แล้วพอย้อนกลับมามองตัวเอง", {}),
        ("night_desk", "มันทำให้เกิดคำถามเงียบๆ", {
            "q1": "เราพลาดอะไรไป",
            "q2": "ทำไมจังหวะชีวิต",
        }),
        ("gap_ideal", "ความกดดันนี้ไม่ได้มาจาก", {"ideal": "กับภาพที่เราคิดว่า"}),
    ],
    3: [
        ("different_paths", "", {"ruler": "มาให้วัดด้วยไม้บรรทัด"}),
        ("explore_rest", "การที่เราใช้เวลาสำรวจ", {"rest": "หรือหยุดพัก"}),
        ("highway_dirt", "เส้นทางของบางคนเป็นถนนหลวง", {"dirt": "แต่เส้นทางของบางคน"}),
    ],
    4: [
        ("night_window", "", {"room": "ท่ามกลางความเงียบงัน"}),
        ("own_pace", "เรายังคงต้องก้าวเดินต่อไป", {"sign": "หรือจริงๆ แล้ว"}),
    ],
}

# EP02 915f22fc: "เงาของความเร่งรีบ" (lonely in a crowded city). Scenes in scenes_ep02.py.
EP02 = {
    1: [
        ("station_crowd", "", {}),
        ("station_quiet", "ในพื้นที่ที่มีคนอยู่เต็มไปหมด", {"quiet": "บางทีมันก็เป็นจุดที่เสียงข้างใน"}),
    ],
    2: [
        ("rush_past", "", {"ghost": "มันให้ความรู้สึกเหมือนเราเป็นแค่ฉากหลัง"}),
        ("dark_room", "ความโดดเดี่ยวในเมืองใหญ่", {}),
        ("train_interior", "แต่มันเกิดขึ้นตรงที่ที่เรา", {"lines": "แต่กลับไม่มีพื้นที่"}),
        ("loud_thoughts", "ความเร่งรีบของคนรอบข้าง", {"loud": "มันดังขึ้น", "echo": "จนกลายเป็นความอ้างว้าง"}),
    ],
    3: [
        ("city_flow", "", {}),
        ("echo", "แต่มันเป็นเพียงเสียงสะท้อน", {"human": "เรากำลังเป็นมนุษย์"}),
        ("million_windows", "แม้ในที่ที่มีคนเป็นล้าน", {}),
    ],
    4: [
        ("train_arrives", "", {"doors": "ประตูเปิดออก", "still": "ปล่อยให้ความเงียบ"}),
    ],
}

# EP03 39593eda: "ราคาที่จ่ายไปกับตัวเลขในบัญชี" (The Cost of Hustle). Scenes in scenes_ep03.py.
EP03 = {
    1: [
        ("balance_rise", "", {"cost": "อาจแลกมาด้วยอะไรบางอย่าง"}),
    ],
    2: [
        ("hustle_years", "", {"ding": "เสียงแจ้งเตือนเงินเข้า", "endure": "อดทนอีกนิด"}),
        ("body_warning", "จนกระทั่งวันที่ร่างกายส่งเสียงเตือน", {"bill": "และบิลค่ารักษาพยาบาลในมือ"}),
        ("bill_hospital", "ความรู้สึกตอนที่ยืนมองกระดาษแผ่นนั้น", {"time": "เวลาหลายปีที่หายไปกับงาน"}),
        ("sealed_office", "ร่างกายนี้พังลงไปทีละส่วน", {"outside": "ขณะที่โลกข้างนอกหมุนไป"}),
    ],
    3: [
        ("future_house", "", {"now": "ปัจจุบันที่เรากำลังใช้อยู่"}),
        ("scale_time", "และบางครั้ง บิลใบเดียว", {"tip": "แต่คือลมหายใจและเวลา"}),
    ],
    4: [
        ("hospital_rain", "", {"pain": "ในขณะที่เสียงของความเจ็บปวด"}),
    ],
}

# EP04 95ae3699: "ป้ายราคาที่ต้องแลก" (Trend Chaser & The Debt Trap). Scenes in scenes_ep04.py.
EP04 = {
    1: [
        ("unbox_room", "", {}),
    ],
    2: [
        ("checkout", "", {"drop": "ยอดเงินในบัญชีที่ลดฮวบ", "excite": "ถูกแทนที่ด้วยความตื่นเต้น"}),
        ("photo_shoot", "ตอนที่จัดวางมุมถ่ายรูป", {"post": "รูปภาพที่ถูกโพสต์ลงไป"}),
        ("spotlight", "ความรู้สึกเหมือนตัวเองมีความสำคัญ", {"quiet": "แต่พอนาฬิกาผ่านไปสักพัก"}),
        ("noodle_month", "สิ่งที่ยังคงอยู่คือบิล", {"noodle": "สิ้นเดือนนี้อาจจะต้องกินบะหมี่"}),
    ],
    3: [
        ("strangers", "", {}),
        ("heavy_bags", "ความพยายามที่จะกลมกลืน", {"minus": "และในบัญชีที่ติดลบ"}),
    ],
    4: [
        ("debt_glow", "", {}),
    ],
}

# EP05 42eac64a: "เสียงที่หายไปกับการกระทำที่เหลืออยู่" (Actions Louder Than Words). Scenes in scenes_ep05.py.
EP05 = {
    1: [
        ("sweet_voice", "", {}),
    ],
    2: [
        ("facade", "", {"facade": "สุดท้ายมันเป็นแค่ฉากบังหน้า", "pain": "พอมันจบลง"}),
        ("waiting_dog", "ในขณะที่อีกมุมหนึ่ง", {"lap": "คอยเอาหัวมาซบตัก"}),
    ],
    3: [
        ("word_storm", "", {}),
        ("quiet_actions", "กลับกัน การกระทำเล็กๆ", {}),
    ],
    4: [
        ("bedside_breath", "", {}),
    ],
}

# EP06 f6c2117b: "อีเมลฉบับที่เท่าไหร่" (First Jobber's Struggle). Scenes in scenes_ep06.py.
EP06 = {
    1: [
        ("wardrobe", "", {}),
    ],
    2: [
        ("friends_hired", "", {"us": "แต่สำหรับเรา"}),
        ("email_pile", "อีเมลฉบับที่ยี่สิบ", {"n30": "สามสิบ", "n40": "สี่สิบ"}),
        ("resume_edit", "ทุกครั้งที่แก้เรซูเม่", {"same": "แต่ผลลัพธ์ที่ได้กลับเท่าเดิม"}),
        ("interview_exit", "ตอนเดินออกจากห้องสัมภาษณ์", {"unequal": "หรือโลกใบนี้มันถูกออกแบบ"}),
    ],
    3: [
        ("calendars", "", {}),
        ("envelope_stairs", "และทุกการปฏิเสธที่ผ่านมา", {}),
    ],
    4: [
        ("new_email", "", {}),
    ],
}

# episode id -> storyboard; render.py defaults to the last one that has narration audio.
STORYBOARDS = {
    "aa1899f700264850904380daa5e6340f": EP01,
    "915f22fc43c84c3491308361839b0c1c": EP02,
    "39593eda69cf4a8fb0ed81515f58c9e7": EP03,
    "95ae3699eed54c65b1313e22011f3b3a": EP04,
    "42eac64ab38748c8a65d313b6ea909d0": EP05,
    "f6c2117b169444d0a621dbee383f71fd": EP06,
}
