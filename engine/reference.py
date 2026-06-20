"""Reference matching (Phase 2) — make a track sound like a reference.

Uses `matchering` (open source): it analyses a reference song and applies the
spectral + loudness profile to your track, so your master matches the tone and
level of a song you like. Great "make mine sound like this" feature.

Install:  pip install matchering
(matchering brings its own DSP; ffmpeg not required for this path.)
"""
from __future__ import annotations
from dataclasses import dataclass

from .master import EngineError


def available() -> bool:
    try:
        import matchering  # noqa: F401
        return True
    except Exception:
        return False


@dataclass
class MatchResult:
    output: str
    reference: str


def match(target: str, reference: str, dst: str) -> MatchResult:
    """Match `target` to `reference`, writing the result to `dst` (16-bit WAV)."""
    try:
        import matchering as mg
    except Exception:
        raise EngineError("matchering not installed.  pip install matchering")
    try:
        mg.process(target=target, reference=reference, results=[mg.pcm16(dst)])
    except Exception as e:  # matchering raises various errors for bad input
        raise EngineError(f"reference match failed: {e}")
    return MatchResult(output=dst, reference=reference)
