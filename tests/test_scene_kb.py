from life_lesson.video.scene_kb import RECIPES, is_worker, retrieve_recipe


def test_kaprao_stall_cue_retrieves_the_food_stall_recipe():
    r = retrieve_recipe("เจ๊ร้านตามสั่งกำลังผัดกะเพราในกระทะไฟลุก")
    assert r.id == "food_stall" and r.setting == "food_stall"
    assert {"wok_flame", "steam", "menu_sign", "plate_kaprao"} <= set(r.props)
    assert "apron" in r.wardrobe and r.worker_pose == "stir" and r.sleeve == "short"


def test_english_cue_and_explicit_setting():
    assert retrieve_recipe("a street food stall at night, wok fire").id == "food_stall"
    assert retrieve_recipe("anything", explicit_setting="forest").setting == "forest"
    assert retrieve_recipe("ไม่มีคำบอกใบ้").id == "desk_night"


def test_other_places_map_to_their_settings():
    assert retrieve_recipe("นักศึกษานั่งริมหาดบนเกาะ").setting == "island"
    assert retrieve_recipe("เรือเล็กกลางทะเล").setting == "sea"


def test_only_the_worker_gets_the_wardrobe():
    r = retrieve_recipe("ร้านตามสั่ง")
    assert is_worker(r, "เจ๊", "แม่ค้า") and not is_worker(r, "นักศึกษา", "เด็กใหม่")


def test_every_recipe_is_well_formed():
    ids = [r.id for r in RECIPES]
    assert len(ids) == len(set(ids))
    assert all(r.keywords and r.setting for r in RECIPES)


def test_chicken_rice_cue_picks_cart_and_vendor_wardrobe():
    from life_lesson.video.scene_kb import is_worker, retrieve_recipe

    r = retrieve_recipe("ป้าหน่อยสับไก่ข้างรถเข็นข้าวมันไก่ ไก่แขวนในตู้กระจก")
    assert r.setting == "chicken_cart" and "apron" in r.wardrobe
    assert is_worker(r, "แม่ค้าข้าวมันไก่")
    assert retrieve_recipe("เดินผ่านห้างสรรพสินค้า").setting == "mall"
    assert retrieve_recipe("ชั่งไก่ในตลาดสด").setting == "market"


def test_bus_story_cues_pick_bus_stop_and_arrival():
    from life_lesson.video.scene_kb import props_from_cue, retrieve_recipe

    assert retrieve_recipe("น้ำฝนรอรถเมล์ไฟฟ้าสีน้ำเงินที่ป้ายรถเมล์").setting == "bus_stop"
    assert "arriving" in props_from_cue("รถเมล์เข้าป้ายแล้วจอด")
    assert "passengers_awake" in props_from_cue("ผู้โดยสารเล่นโทรศัพท์ทั้งคัน")


def test_riding_and_home_front_cues():
    from life_lesson.video.scene_kb import props_from_cue, retrieve_recipe

    assert "riding" in props_from_cue("ออกจากสถานีช่องนนทรี")
    assert retrieve_recipe("หน้าบ้านมีก้อนหินก้อนใหญ่ ปั๊มน้ำบุบ").setting == "home_front"
