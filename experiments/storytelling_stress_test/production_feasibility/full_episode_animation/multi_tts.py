"""Two-voice Gemini TTS for dialogue scenes (one request = one scene, at most TWO speakers: the Gemini multi-speaker limit).

    dialogue(settings, cache_id, idx, lines, voices, direction) -> (wav path, 'cache' | 'gemini')

lines: [{"speaker": "Tang", "text": "..."}, ...]; voices: {"Tang": "Umbriel", "Jin": "Zephyr"}; direction: plain-English acting note put before the script.
Cached next to the shorts-pipeline TTS cache (same normalise + trim), keyed by direction + script + voices, so nothing is voiced twice.
"""
import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2] / "shorts"))
sys.path.insert(0, str(HERE.parents[3] / "src"))

import gemini_guard  # noqa: E402
import tts as T  # noqa: E402
from google import genai  # noqa: E402
from google.genai import types  # noqa: E402
from life_lesson.tts.gemini_tts import _extract_pcm, _pcm_to_wav_bytes  # noqa: E402


def dialogue(settings, cache_id, idx, lines, voices, direction):
    names = []
    for l in lines:
        if l["speaker"] not in names:
            names.append(l["speaker"])
    if len(names) > 2:
        raise ValueError(f"more than two speakers in one request: {names}")
    script = "\n".join(f"{l['speaker']}: {l['text']}" for l in lines)
    prompt = f"{direction}\n\n{script}"
    key = hashlib.sha1((prompt + json.dumps({n: voices[n] for n in names}, sort_keys=True)).encode("utf-8")).hexdigest()[:10]
    folder = T.CACHE / cache_id
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / f"line{idx:02d}-{key}.multi.wav"
    if path.is_file():
        return path, "cache"
    client = genai.Client(api_key=settings.gemini_api_key)

    def vc(name):
        return types.VoiceConfig(prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name=voices[name]))

    if len(names) == 2:
        sp = types.SpeechConfig(multi_speaker_voice_config=types.MultiSpeakerVoiceConfig(
            speaker_voice_configs=[types.SpeakerVoiceConfig(speaker=n, voice_config=vc(n)) for n in names]))
    else:
        sp = types.SpeechConfig(voice_config=vc(names[0]))
    cfg = types.GenerateContentConfig(response_modalities=["AUDIO"], speech_config=sp)
    resp = gemini_guard.guarded("tts", lambda: client.models.generate_content(model=settings.gemini_tts_model, contents=prompt, config=cfg))
    pcm = _extract_pcm(resp)
    if not pcm:
        raise RuntimeError("Gemini TTS returned no audio data")
    tmp = folder / "_tmp_multi.wav"
    tmp.write_bytes(_pcm_to_wav_bytes(pcm))
    T.write_wav(path, T.normalize(T.trim_silence(T.read_wav(tmp))))
    tmp.unlink()
    return path, "gemini"
