"""Auto-master engine.

Pipeline:
  (optional) tonal/dynamics chain via pedalboard  →  two-pass EBU R128 loudnorm
to hit a streaming loudness target with true-peak safety.

ffmpeg is required for the loudness stage:  brew install ffmpeg
The chain stage is optional (needs pedalboard); without it you still get a real
loudness master.
"""
from __future__ import annotations
import json
import os
import shutil
import subprocess
import tempfile
from dataclasses import dataclass

from . import chain


class EngineError(RuntimeError):
    pass


def _require_ffmpeg() -> None:
    if shutil.which("ffmpeg") is None:
        raise EngineError("ffmpeg not found. Install it: brew install ffmpeg")


@dataclass
class MasterResult:
    output: str
    target_lufs: float
    true_peak: float
    preset: str | None
    measured: dict


def _measure_loudnorm(src: str, target_lufs: float, true_peak: float, lra: float) -> dict:
    cmd = ["ffmpeg", "-hide_banner", "-i", src,
           "-af", f"loudnorm=I={target_lufs}:TP={true_peak}:LRA={lra}:print_format=json",
           "-f", "null", "-"]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    err = proc.stderr
    s, e = err.rfind("{"), err.rfind("}")
    if s == -1 or e == -1:
        raise EngineError("Could not read loudnorm analysis from ffmpeg output.")
    return json.loads(err[s:e + 1])


def _loudness_master(src: str, dst: str, target_lufs: float, true_peak: float,
                     lra: float, sample_rate: int) -> dict:
    m = _measure_loudnorm(src, target_lufs, true_peak, lra)
    cmd = ["ffmpeg", "-hide_banner", "-y", "-i", src, "-af",
           (f"loudnorm=I={target_lufs}:TP={true_peak}:LRA={lra}:"
            f"measured_I={m['input_i']}:measured_TP={m['input_tp']}:"
            f"measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:"
            f"offset={m['target_offset']}:linear=true:print_format=summary"),
           "-ar", str(sample_rate), "-c:a", "pcm_s16le", dst]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise EngineError(f"ffmpeg failed:\n{proc.stderr[-800:]}")
    return m


def master(src: str, dst: str, target_lufs: float = -14.0, true_peak: float = -1.0,
           lra: float = 11.0, sample_rate: int = 44100,
           preset: str | None = None) -> MasterResult:
    """Master `src` → `dst`.

    preset : optional tonal/dynamics chain ('clean'|'warm'|'bright'|'loud').
             Ignored with a warning if pedalboard isn't installed.
    """
    _require_ffmpeg()
    used_preset = None
    work = src
    tmp = None
    if preset:
        if chain.available():
            tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False).name
            chain.apply_chain(src, tmp, preset)
            work = tmp
            used_preset = preset
        else:
            print("note: pedalboard not installed — skipping chain, doing loudness master only.")
    try:
        m = _loudness_master(work, dst, target_lufs, true_peak, lra, sample_rate)
    finally:
        if tmp and os.path.exists(tmp):
            os.remove(tmp)
    return MasterResult(output=dst, target_lufs=target_lufs, true_peak=true_peak,
                        preset=used_preset, measured=m)
