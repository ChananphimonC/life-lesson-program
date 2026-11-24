import math
import struct
import wave

from life_lesson.video.lipsync import mouth_levels


def _wav(path, segments, rate=16000):
    frames = bytearray()
    for loud, secs in segments:
        for n in range(int(rate * secs)):
            frames += struct.pack("<h", int(12000 * math.sin(n * 0.3)) if loud else 0)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(rate); w.writeframes(bytes(frames))


def test_mouth_opens_on_voice_and_shuts_on_pause(tmp_path):
    p = tmp_path / "v.wav"
    _wav(p, [(True, 0.5), (False, 0.5), (True, 0.5)])
    lv = mouth_levels(p, 0, 1500, 12)
    assert lv is not None and len(lv) >= 17
    assert lv[2] == 1 and lv[8] == 0 and lv[14] == 1       # open, shut, open


def test_silent_or_missing_audio_falls_back(tmp_path):
    p = tmp_path / "s.wav"
    _wav(p, [(False, 1.0)])
    assert mouth_levels(p, 0, 1000, 12) is None
    assert mouth_levels(tmp_path / "nope.wav", 0, 1000, 12) is None


def test_schedule_uses_lip_levels_for_the_speaker():
    from life_lesson.video.scenes import Scene, anim_schedule

    sc = Scene(0, 0, 3000, "t", None, None, speaker="ป้า")
    got = anim_schedule(sc, 6, 12, [1, 0, 2, 1, 0, 0])
    assert [m for _, _, m in got] == [1, 0, 2, 1, 0, 0]
    assert all(m == 0 for _, _, m in anim_schedule(Scene(1, 0, 3000, "t", None, None), 6, 12, [1] * 6))
