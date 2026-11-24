"""Scene knowledge base: retrieve what a scene needs before drawing it.

A small, local, copyright-safe "RAG": each recipe lists the props to draw, the
wardrobe a person working there wears, and a search query for optional online
reference lookup. `retrieve_recipe` ranks recipes against the chapter's
`visual_cue` (Thai + English keywords) so "เจ๊ร้านตามสั่งผัดกะเพรา" yields a
street-food stall with wok, flame, steam, menu board, plastic stools and a cook
in an apron -- instead of a generic room.

Add your own recipes (new places, jobs, props) to RECIPES.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SceneRecipe:
    id: str
    setting: str                       # which background the illustrator draws
    keywords: tuple[str, ...]
    props: tuple[str, ...] = ()
    role_words: tuple[str, ...] = ()   # who "works here" (gets the wardrobe)
    wardrobe: tuple[str, ...] = ()
    sleeve: str = "long"               # long | short
    worker_pose: str = "down"
    search_query: str = ""


RECIPES: tuple[SceneRecipe, ...] = (
    SceneRecipe(
        id="food_stall", setting="food_stall",
        keywords=("ร้านตามสั่ง", "ตามสั่ง", "กะเพรา", "กระเพรา", "ผัดกระเพรา", "ผัดกะเพรา", "เจ๊", "แม่ค้า",
                  "ร้านข้าว", "กระทะ", "ผัด", "wok", "street food", "stir fry", "food stall", "ร้านอาหาร", "ข้าวราดแกง"),
        props=("wok_flame", "steam", "menu_sign", "stools", "plate_kaprao", "fluorescent", "bottles"),
        role_words=("เจ๊", "แม่ค้า", "พ่อค้า", "แม่ครัว", "พ่อครัว", "เชฟ", "cook", "vendor", "chef"),
        wardrobe=("apron", "hairnet", "towel"), sleeve="short", worker_pose="stir",
        search_query="thai street food stall pad kaprao wok flame night",
    ),
    SceneRecipe(
        id="chicken_cart", setting="chicken_cart",
        keywords=("ข้าวมันไก่", "รถเข็น", "รถสามล้อ", "ไก่แขวน", "ไก่ต้ม", "ไก่ทอด", "พ่วงมอเตอร์ไซค์", "สับไก่", "chicken rice", "food cart"),
        props=("hanging_chicken", "chopping_board", "bulbs"),
        role_words=("แม่ค้า", "พ่อค้า", "คนขาย", "vendor"), wardrobe=("apron", "towel"), sleeve="short", worker_pose="chop",
        search_query="thai chicken rice tricycle cart motorbike roadside hanging chicken glass case",
    ),
    SceneRecipe(
        id="home_kitchen", setting="kitchen",
        keywords=("ห้องครัว", "ต้มไก่", "หม้อต้ม", "น้ำซุป", "หุงข้าว", "ครัวบ้าน", "kitchen"),
        props=("big_pot", "ginger"), role_words=("แม่ค้า", "แม่ครัว"), wardrobe=("apron",), sleeve="short",
        search_query="thai home kitchen boiling whole chicken big pot ginger coriander root steam",
    ),
    SceneRecipe(
        id="bus_stop", setting="bus_stop",
        keywords=("ป้ายรถเมล์", "รอรถเมล์", "รถเมล์ไฟฟ้า", "รถไฟฟ้าสีน้ำเงิน", "รถเมล์เข้าป้าย", "bus stop"),
        search_query="thai smile bus blue electric bus bus stop bangkok",
    ),
    SceneRecipe(
        id="home_front", setting="home_front",
        keywords=("หน้าบ้าน", "ก้อนหิน", "ปั๊มน้ำ", "ทางลาด", "ลานจอดรถ", "ซอยบ้าน", "home front"),
        role_words=("แม่", "น้า"), search_query="thai house front driveway ramp big rock water pump wet ground night",
    ),
    SceneRecipe(
        id="sky_train", setting="bts",
        keywords=("รถไฟฟ้า", "บีทีเอส", "bts", "สถานีรถไฟฟ้า", "skytrain"),
        search_query="bangkok bts sky train interior morning commuters",
    ),
    SceneRecipe(
        id="side_by_side", setting="compare",
        keywords=("เปรียบเทียบ", "เทียบตัวเลข", "สองคอลัมน์", "แท่งกราฟ", "เทียบรายได้"),
        role_words=("แม่ค้า", "พ่อค้า"), wardrobe=("apron",), sleeve="short",
        search_query="two column comparison infographic hours and income",
    ),
    SceneRecipe(
        id="wet_market", setting="market",
        keywords=("ตลาดสด", "ตลาดเช้า", "ตลาด", "ชั่งไก่", "แผงไก่", "wet market"),
        role_words=("แม่ค้า", "พ่อค้า", "คนขาย"), wardrobe=("apron",), sleeve="short",
        search_query="thai wet market early morning chicken stall tarp",
    ),
    SceneRecipe(
        id="shopping_mall", setting="mall",
        keywords=("ห้างสรรพสินค้า", "ห้าง", "เซ็นทรัล", "ร้านค้าในห้าง", "mall", "shopping"),
        search_query="shopping mall concourse shopfronts bright floor",
    ),
    SceneRecipe(
        id="island_camp", setting="island",
        keywords=("เกาะ", "ชายหาด", "ติดเกาะ", "เรือแตก", "กองไฟ", "island", "beach", "stranded"),
        props=("campfire",), role_words=("นักศึกษา", "student"), wardrobe=("lanyard", "backpack"),
        search_query="island beach night campfire",
    ),
    SceneRecipe(
        id="boat_sea", setting="sea",
        keywords=("ทะเล", "เรือ", "คลื่น", "ท่าเรือ", "sea", "boat", "ocean", "ferry"),
        role_words=("นักศึกษา", "student"), wardrobe=("hood",), search_query="small boat night sea moon",
    ),
    SceneRecipe(
        id="desk_night", setting="room",
        keywords=("โต๊ะ", "ห้อง", "บ้าน", "เตียง", "หน้าจอ", "มือถือ", "บิล", "เงิน", "ค่าเทอม", "ค่าเช่า", "room", "desk", "bills"),
        search_query="small room desk lamp night window",
    ),
    SceneRecipe(
        id="office_floor", setting="office",
        keywords=("ออฟฟิศ", "ที่ทำงาน", "ประชุม", "ลิฟต์", "office", "elevator", "meeting"),
        role_words=("พนักงาน", "หัวหน้า", "staff"), wardrobe=("lanyard",), search_query="office night city window desk",
    ),
    SceneRecipe(
        id="dead_end_alley", setting="alley",
        keywords=("ซอยตัน", "ซอยเปลี่ยว", "ซอยมืด", "ตรอก", "ซอยลับ", "dead end", "alley"),
        search_query="dark dead end alley night rain wet pavement",
    ),
    SceneRecipe(
        id="city_bus", setting="bus",
        keywords=("รถเมล์", "บนรถ", "รถโดยสาร", "ราวเหล็ก", "ที่นั่งสีฟ้า", "รถประจำทาง", "bus"),
        search_query="crowded city bus interior evening handrail passengers",
    ),
    SceneRecipe(
        id="night_street", setting="street",
        keywords=("ถนน", "ซอย", "ป้ายรถ", "ทางเท้า", "ร้านสะดวกซื้อ", "street", "alley", "bus stop"),
        search_query="city street night lamp post",
    ),
    SceneRecipe(
        id="city_roof", setting="city",
        keywords=("เมือง", "ตึก", "ดาดฟ้า", "คอนโด", "city", "skyline", "rooftop"),
        search_query="city skyline night rooftop",
    ),
    SceneRecipe(
        id="forest_path", setting="forest",
        keywords=("ป่า", "ต้นไม้", "ภูเขา", "forest", "woods", "trail"), search_query="pine forest night fog",
    ),
    SceneRecipe(
        id="night_sky_hill", setting="night_sky",
        keywords=("ดาว", "ท้องฟ้า", "พระจันทร์", "sky", "stars"), search_query="starry night hill",
    ),
)

_BY_ID = {r.id: r for r in RECIPES}
_BY_SETTING = {}
for _r in RECIPES:
    _BY_SETTING.setdefault(_r.setting, _r)


def retrieve_recipe(cue_text: str | None, explicit_setting: str | None = None) -> SceneRecipe:
    """Best recipe for the scene text; longer keyword matches weigh more."""
    text = (cue_text or "").lower()
    best, best_score = None, 0.0
    for recipe in RECIPES:
        score = sum(len(k) ** 1.2 for k in recipe.keywords if k.lower() in text)
        if explicit_setting and recipe.setting == explicit_setting:
            score += 3
        if score > best_score:
            best, best_score = recipe, score
    if best is not None:
        return best
    if explicit_setting and explicit_setting in _BY_SETTING:
        return _BY_SETTING[explicit_setting]
    return _BY_ID["desk_night"]


def is_worker(recipe: SceneRecipe, *texts: str | None) -> bool:
    blob = " ".join(t or "" for t in texts).lower()
    return any(w.lower() in blob for w in recipe.role_words)


def props_from_cue(cue_text: str | None) -> tuple[str, ...]:
    """Story props named in a scene's cue (drawn by the illustrator)."""
    text = cue_text or ""
    props: list[str] = []
    if any(k in text for k in ("ช่องหน้าต่าง", "จานผี", "จานที่ไม่มีคนสั่ง", "จานเซ่น")):
        props.append("ledge_plate")
    if "สองใบ" in text and "ledge_plate" in props:
        props.append("second_plate")
    if "ไข่ดาวหายไป" in text or "ครึ่งฟอง" in text:
        props.append("half_eaten")
    if any(k in text for k in ("ลืมตาพร้อมกัน", "ตื่นพร้อมกัน", "ทั้งคันลืมตา", "เล่นโทรศัพท์", "ก้มหน้าเล่นมือถือ")):
        props.append("passengers_awake")
    if any(k in text for k in ("นั่งลง", "นั่งบน", "ได้นั่ง")):
        props.append("protagonist_seated")
    if any(k in text for k in ("ยื่นจาน", "ยกจาน", "เสิร์ฟ", "ตักข้าวให้")):
        props.append("serving")
    if any(k in text for k in ("ขอบเตียง", "บนเตียง", "นอนคลุมผ้า", "นาฬิกาปลุก")):
        props.append("bed")
    if any(k in text for k in ("ออกจากสถานี", "รถไฟฟ้าวิ่ง", "ขึ้นรถไฟฟ้า")):
        props.append("riding")
    if any(k in text for k in ("เข้าป้าย", "รถมาจอด", "รถเมล์มาถึง", "รอรถเมล์")):
        props.append("arriving")
    if "กาแฟ" in text:
        props.append("coffee")
    if any(k in text for k in ("ถุงขนม", "ถือถุง")):
        props.append("carrying")
    if "เดิน" in text:
        props.append("walking")
    if "เงา" in text:
        props.append("far_silhouette")
    return tuple(props)
