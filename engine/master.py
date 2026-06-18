"""Auto-master engine — v0.

Two-pass EBU R128 loudness normalisation (via ffmpeg's `loudnorm`), which is a
real, transparent master for hitting a streaming loudness target with true-peak
safety. Later phases add an EQ/compression/limiting chain (pedalboard) and
reference matching (matchering).

Runs anywhere ffmpeg is installed:  brew install ffmpeg
"""
from __future__ import annotations
import json
import shutil
import subprocess
from dataclasses import dataclass


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
    measured: dict


def _measure_loudnorm(src: str, target_lufs: float, true_peak: float, lra: float) -> dict:
    """Pass 1: analyse the input and return loudnorm's measured values (JSON)."""
    cmd = [
        "ffmpeg", "-hide_banner", "-i", src,
        "-af", f"loudnorm=I={target_lufs}:TP={true_peak}:LRA={lra}:print_format=json",
        "-f", "null", "-",
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    # ffmpeg prints the JSON block to stderr; grab the last {...}
    err = proc.stderr
    start = err.rfind("{")
    end = err.rfind("}")
    if start == -1 or end == -1:
        raise EngineError("Could not read loudnorm analysis from ffmpeg output.")
    return json.loads(err[start:end + 1])


def master(src: str, dst: str, target_lufs: float = -14.0,
           true_peak: float = -1.0, lra: float = 11.0,
           sample_rate: int = 44100) -> MasterResult:
    """Master `src` to `dst` at the given loudness target.

    target_lufs : integrated loudness target (streaming ≈ -14, club ≈ -9..-11)
    true_peak   : max true peak in dBTP (keep ≤ -1 to avoid inter-sample clipping)
    """
    _require_ffmpeg()
    m = _measure_loudnorm(src, target_lufs, true_peak, lra)
    cmd = [
        "ffmpeg", "-hide_banner", "-y", "-i", src,
        "-af",
        (f"loudnorm=I={target_lufs}:TP={true_peak}:LRA={lra}:"
         f"measured_I={m['input_i']}:measured_TP={m['input_tp']}:"
         f"measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:"
         f"offset={m['target_offset']}:linear=true:print_format=summary"),
        "-ar", str(sample_rate), "-c:a", "pcm_s16le", dst,
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise EngineError(f"ffmpeg failed:\n{proc.stderr[-800:]}")
    return MasterResult(output=dst, target_lufs=target_lufs, true_peak=true_peak, measured=m)
