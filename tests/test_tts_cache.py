import pytest

from life_lesson.errors import TTSError
from life_lesson.tts.cache import CachedTTS, VoiceBudgetExhausted, is_quota_error
from life_lesson.tts.silent import SilentTTSProvider

from .conftest import make_silence_wav


class Counting:
    def __init__(self, fail_after=None, message="429 RESOURCE_EXHAUSTED quota"):
        self.calls, self.fail_after, self.message = [], fail_after, message

    def synthesize(self, text):
        if self.fail_after is not None and len(self.calls) >= self.fail_after:
            raise TTSError(self.message)
        self.calls.append(text)
        return make_silence_wav(duration_ms=60)


def test_a_block_is_paid_for_once(tmp_path):
    inner = Counting()
    tts = CachedTTS(inner, tmp_path, namespace="g|m|Kore")
    a = tts.synthesize("ข้อความ")
    b = tts.synthesize("ข้อความ")
    assert a == b and inner.calls == ["ข้อความ"] and (tts.hits, tts.new_calls) == (1, 1)
    # a fresh object (a later run / another day) still hits the cache on disk
    again = CachedTTS(Counting(), tmp_path, namespace="g|m|Kore")
    assert again.synthesize("ข้อความ") == a and again.hits == 1


def test_voice_or_text_change_is_a_different_block(tmp_path):
    inner = Counting()
    CachedTTS(inner, tmp_path, namespace="g|m|Kore").synthesize("x")
    CachedTTS(inner, tmp_path, namespace="g|m|Puck").synthesize("x")      # other voice
    CachedTTS(inner, tmp_path, namespace="g|m|Kore").synthesize("x ")     # other text
    assert len(inner.calls) == 3


def test_budget_pauses_after_n_new_blocks_but_cached_blocks_are_free(tmp_path):
    inner = Counting()
    tts = CachedTTS(inner, tmp_path, namespace="n", budget=2)
    tts.synthesize("a"); tts.synthesize("b")
    tts.synthesize("a")                                    # cached: free even at the limit
    with pytest.raises(VoiceBudgetExhausted):
        tts.synthesize("c")
    assert inner.calls == ["a", "b"]


def test_quota_errors_pause_instead_of_failing_other_errors_still_fail(tmp_path):
    with pytest.raises(VoiceBudgetExhausted, match="quota"):
        CachedTTS(Counting(fail_after=0), tmp_path, namespace="n").synthesize("a")
    with pytest.raises(TTSError):
        CachedTTS(Counting(fail_after=0, message="400 invalid argument"), tmp_path, namespace="n").synthesize("a")
    assert is_quota_error("Error 429: Too Many Requests") and not is_quota_error("400 bad request")


def test_no_half_written_block_is_ever_served(tmp_path):
    tts = CachedTTS(Counting(), tmp_path, namespace="n")
    tts._path("a").parent.mkdir(parents=True, exist_ok=True)
    tts._path("a").write_bytes(b"RIFF")          # truncated leftover
    inner = tts._inner
    tts.synthesize("a")
    assert inner.calls == ["a"]                  # too small to trust: re-synthesised


def test_silent_voice_is_marked_uncacheable():
    assert SilentTTSProvider.cacheable is False
