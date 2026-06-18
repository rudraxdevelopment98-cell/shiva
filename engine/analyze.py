"""Loudness / peak analysis via ffmpeg (EBU R128 + true peak)."""
from __future__ import annotations
import json
import shutil
import subprocess
from dataclasses import dataclass


class EngineError(RuntimeError):
    pass


@dataclass
class Analysis:
    integrated_lufs: float
    loudness_range: float
    true_peak_db: float

    def pretty(self) -> str:
        return (f"Integrated loudness : {self.integrated_lufs:.1f} LUFS\n"
                f"Loudness range (LRA): {self.loudness_range:.1f} LU\n"
                f"True peak           : {self.true_peak_db:.1f} dBTP")


def analyze(src: str) -> Analysis:
    if shutil.which("ffmpeg") is None:
        raise EngineError("ffmpeg not found. Install it: brew install ffmpeg")
    cmd = ["ffmpeg", "-hide_banner", "-i", src,
           "-af", "loudnorm=print_format=json", "-f", "null", "-"]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    err = proc.stderr
    s, e = err.rfind("{"), err.rfind("}")
    if s == -1 or e == -1:
        raise EngineError("Could not read analysis from ffmpeg output.")
    d = json.loads(err[s:e + 1])
    return Analysis(
        integrated_lufs=float(d["input_i"]),
        loudness_range=float(d["input_lra"]),
        true_peak_db=float(d["input_tp"]),
    )
