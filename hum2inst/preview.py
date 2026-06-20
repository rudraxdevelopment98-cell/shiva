"""Hear-it preview — render the generated MIDI to audio so you can hear it
without opening a DAW.

Two paths:
  • If a soundfont (.sf2) is available → realistic instrument via fluidsynth.
  • Otherwise → a clean sine synthesis fallback (no extra setup), so it always
    plays and you can judge the melody, timing, and tuning.

Point at a soundfont with --sf2 or the HUM2INST_SF2 env var for real sounds.
"""
from __future__ import annotations
import os
import wave

from .transcribe import HumError

# name → General MIDI program (0-indexed)
INSTRUMENTS = {
    "piano": 0, "epiano": 4, "organ": 16, "guitar": 24, "pluck": 45,
    "bass": 33, "synthbass": 38, "strings": 48, "lead": 81, "pad": 89,
}


def _write_wav(path: str, pcm, sr: int) -> None:
    with wave.open(path, "w") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(pcm.tobytes())


def render(midi, out_wav: str, instrument: str = "bass",
           sf2: str | None = None, sr: int = 44100) -> str:
    """Render `midi` (a pretty_midi.PrettyMIDI) to `out_wav`."""
    try:
        import numpy as np
    except Exception:
        raise HumError("numpy needed for preview.  pip install numpy")

    prog = INSTRUMENTS.get(instrument, INSTRUMENTS["bass"])
    for inst in midi.instruments:
        inst.program = prog
        inst.is_drum = False
        inst.name = instrument

    sf2 = sf2 or os.environ.get("HUM2INST_SF2")
    audio = None
    if sf2 and os.path.exists(sf2):
        try:
            audio = midi.fluidsynth(fs=sr, sf2_path=sf2)   # realistic
        except Exception:
            audio = None
    if audio is None:
        try:
            audio = midi.synthesize(fs=sr)                  # sine fallback
        except Exception as e:
            raise HumError(f"could not render audio: {e}")

    if audio is None or len(audio) == 0:
        raise HumError("nothing to render — no notes were detected.")
    peak = float(np.max(np.abs(audio))) or 1.0
    pcm = (audio / peak * 0.95 * 32767).astype("<i2")
    _write_wav(out_wav, pcm, sr)
    return out_wav
