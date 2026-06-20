"""Hum → Instrument — the magic core (Phase 1).

Pipeline:  hum.wav → transcribe (basic-pitch) → quantize to BPM → snap to key → MIDI

Faithful turns your hum into notes; quantize locks them to the grid; key-snap
moves every note into the song's scale so it's always in tune with the track.

Deps (on your Mac):  pip install basic-pitch pretty_midi librosa
basic-pitch is Spotify's open-source audio→MIDI model.
"""
from __future__ import annotations
from dataclasses import dataclass


class HumError(RuntimeError):
    pass


# ---- music theory: scales ----
_NOTE = {"c": 0, "c#": 1, "db": 1, "d": 2, "d#": 3, "eb": 3, "e": 4, "f": 5,
         "f#": 6, "gb": 6, "g": 7, "g#": 8, "ab": 8, "a": 9, "a#": 10, "bb": 10, "b": 11}
_SCALES = {
    "maj": [0, 2, 4, 5, 7, 9, 11], "major": [0, 2, 4, 5, 7, 9, 11],
    "min": [0, 2, 3, 5, 7, 8, 10], "minor": [0, 2, 3, 5, 7, 8, 10],
    "minpent": [0, 3, 5, 7, 10], "majpent": [0, 2, 4, 7, 9],
    "chromatic": list(range(12)),
}


def parse_key(key: str):
    """'Cmaj', 'A min', 'F#minpent' → (root_pitch_class, scale_intervals)."""
    k = key.strip().lower().replace(" ", "")
    for n in sorted(_NOTE, key=len, reverse=True):
        if k.startswith(n):
            scale = k[len(n):] or "maj"
            if scale not in _SCALES:
                raise HumError(f"unknown scale '{scale}'")
            return _NOTE[n], _SCALES[scale]
    raise HumError(f"could not parse key '{key}'")


def _snap_pitch(midi_note: int, root: int, scale: list[int]) -> int:
    allowed = {(root + s) % 12 for s in scale}
    if midi_note % 12 in allowed:
        return midi_note
    for d in range(1, 7):                       # nearest in-scale pitch
        if (midi_note - d) % 12 in allowed:
            return midi_note - d
        if (midi_note + d) % 12 in allowed:
            return midi_note + d
    return midi_note


@dataclass
class HumResult:
    output: str
    notes: int
    bpm: float
    key: str


def transcribe(wav: str):
    """wav → pretty_midi.PrettyMIDI (raw notes)."""
    try:
        from basic_pitch.inference import predict
    except Exception:
        raise HumError("basic-pitch not installed.  pip install basic-pitch")
    try:
        _, midi, _ = predict(wav)
    except Exception as e:
        raise HumError(f"transcription failed: {e}")
    return midi


def quantize(midi, bpm: float, grid: int = 16):
    """Snap note starts/ends to a `grid`-th-note grid at `bpm`."""
    step = (60.0 / bpm) * (4.0 / grid)          # seconds per grid cell
    for inst in midi.instruments:
        for n in inst.notes:
            n.start = round(n.start / step) * step
            n.end = max(n.start + step, round(n.end / step) * step)
    return midi


def snap_key(midi, key: str):
    root, scale = parse_key(key)
    for inst in midi.instruments:
        for n in inst.notes:
            n.pitch = _snap_pitch(n.pitch, root, scale)
    return midi


def run(wav: str, out: str, bpm: float = 90.0, key: str = "Cmaj",
        grid: int = 16, correct: bool = True) -> HumResult:
    """Full pipeline → writes a .mid you can drop on any instrument track."""
    midi = transcribe(wav)
    midi = quantize(midi, bpm, grid)
    if correct:
        midi = snap_key(midi, key)
    midi.write(out)
    n = sum(len(i.notes) for i in midi.instruments)
    return HumResult(output=out, notes=n, bpm=bpm, key=key)


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser(description="Hum → clean, in-key MIDI part")
    p.add_argument("wav", help="your hummed/sung/beatboxed clip")
    p.add_argument("-o", "--output", required=True, help="output .mid")
    p.add_argument("--bpm", type=float, default=90.0)
    p.add_argument("--key", default="Cmaj", help="e.g. Cmaj, Amin, F#minpent")
    p.add_argument("--grid", type=int, default=16, help="quantize grid (8, 16, 32)")
    p.add_argument("--faithful", action="store_true", help="don't snap to key")
    a = p.parse_args()
    try:
        r = run(a.wav, a.output, bpm=a.bpm, key=a.key, grid=a.grid, correct=not a.faithful)
        print(f"✓ {r.notes} notes → {r.output}  ({r.bpm} BPM, key {r.key})")
        print("Drop the .mid on any instrument track in your DAW.")
    except HumError as e:
        raise SystemExit(f"error: {e}")
