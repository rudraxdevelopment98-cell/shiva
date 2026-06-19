"""Auto-mix (v0) — balance several stems into one cohesive track.

Approach (heuristic, transparent):
  1. Loudness-balance every stem to a common target (so nothing buries anything).
  2. Sum them on a float bus (headroom preserved, no clipping).
  3. Master the bus to the final loudness target (optionally through a tone chain).

This is a sensible automatic starting mix. Per-stem EQ/pan/role-aware balancing
comes later; this already turns raw stems into a level-coherent master.

Needs ffmpeg (brew install ffmpeg). Tone presets additionally need pedalboard.
"""
from __future__ import annotations
import os
import subprocess
import tempfile
from dataclasses import dataclass

from .master import master, _require_ffmpeg, EngineError


@dataclass
class MixResult:
    output: str
    stems: int
    target_lufs: float
    preset: str | None


def automix(stems: list[str], dst: str, stem_lufs: float = -18.0,
            target_lufs: float = -14.0, true_peak: float = -1.0,
            preset: str | None = None, sample_rate: int = 44100) -> MixResult:
    if len(stems) < 2:
        raise EngineError("Provide at least two stems to mix.")
    _require_ffmpeg()

    tmps: list[str] = []
    try:
        # 1) balance each stem to a common loudness
        balanced: list[str] = []
        for s in stems:
            t = tempfile.NamedTemporaryFile(suffix=".wav", delete=False).name
            tmps.append(t)
            master(s, t, target_lufs=stem_lufs, true_peak=-1.0, sample_rate=sample_rate)
            balanced.append(t)

        # 2) sum to a float bus (no clipping)
        bus = tempfile.NamedTemporaryFile(suffix=".wav", delete=False).name
        tmps.append(bus)
        cmd = ["ffmpeg", "-hide_banner", "-y"]
        for b in balanced:
            cmd += ["-i", b]
        cmd += ["-filter_complex",
                f"amix=inputs={len(balanced)}:normalize=0:duration=longest",
                "-ar", str(sample_rate), "-c:a", "pcm_f32le", bus]
        p = subprocess.run(cmd, capture_output=True, text=True)
        if p.returncode != 0:
            raise EngineError(f"ffmpeg amix failed:\n{p.stderr[-800:]}")

        # 3) master the bus
        res = master(bus, dst, target_lufs=target_lufs, true_peak=true_peak,
                     preset=preset, sample_rate=sample_rate)
    finally:
        for t in tmps:
            if os.path.exists(t):
                os.remove(t)

    return MixResult(output=dst, stems=len(stems), target_lufs=target_lufs, preset=res.preset)
