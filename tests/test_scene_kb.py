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
