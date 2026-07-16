"""SonicDNA — real audio features (librosa) + valence/arousal.

Extracts objective DSP features and maps them to a (valence, arousal) point per
segment. Emotion probabilities are derived from V/A in emotion.py. This is a
transparent v0 (heuristic, explainable) — swap in a trained model later without
changing the API.

Needs: librosa, numpy, soundfile, ffmpeg.
"""
from __future__ import annotations
import subprocess
import tempfile
import os

SR = 22050
_KRUMHANSL_MAJ = [6.35,2.23,3.48,2.33,4.38,4.09,2.52,5.19,2.39,3.66,2.29,2.88]
_KRUMHANSL_MIN = [6.33,2.68,3.52,5.38,2.60,3.53,2.54,4.75,3.98,2.69,3.34,3.17]
_NAMES = ["C","C#","D","D#","E","F","F#","G","G#","A","A#","B"]


class FeatureError(RuntimeError):
    pass


def _to_wav(src: str) -> str:
    from shutil import which
    if which("ffmpeg") is None:
        raise FeatureError("ffmpeg not found. brew install ffmpeg")
    dst = tempfile.NamedTemporaryFile(suffix=".wav", delete=False).name
    p = subprocess.run(["ffmpeg", "-hide_banner", "-y", "-i", src,
                        "-ac", "1", "-ar", str(SR), dst],
                       capture_output=True, text=True)
    if p.returncode != 0:
        os.path.exists(dst) and os.remove(dst)
        raise FeatureError(f"couldn't decode audio:\n{p.stderr[-300:]}")
    return dst


def _key(chroma_mean):
    import numpy as np
    best = (-1e9, "C", "major", 1)
    for i in range(12):
        maj = np.corrcoef(np.roll(_KRUMHANSL_MAJ, i), chroma_mean)[0, 1]
        mnr = np.corrcoef(np.roll(_KRUMHANSL_MIN, i), chroma_mean)[0, 1]
        if maj > best[0]:
            best = (maj, _NAMES[i], "major", 1)
        if mnr > best[0]:
            best = (mnr, _NAMES[i], "minor", -1)
    return best[1], best[2], best[3]


def _va(bpm, rms, centroid, mode_sign, sr=SR):
    """features → (valence, arousal) in [-1,1]."""
    def clip01(x): return max(0.0, min(1.0, x))
    tempo = clip01((bpm - 60) / 120)
    energy = clip01(rms / 0.2)
    bright = clip01(centroid / (sr / 2) * 4)          # relative brightness
    arousal01 = 0.5 * tempo + 0.3 * energy + 0.2 * bright
    valence01 = clip01(0.5 + 0.3 * mode_sign + 0.15 * (bright - 0.5) + 0.1 * (energy - 0.5))
    return (2 * valence01 - 1, 2 * arousal01 - 1)


def analyze_track(path: str, segments: int = 12) -> dict:
    """Return objective features + full-track and per-segment (valence,arousal)."""
    try:
        import numpy as np
        import librosa
    except Exception:
        raise FeatureError("librosa/numpy not installed. pip install librosa soundfile numpy")

    wav = _to_wav(path)
    try:
        y, sr = librosa.load(wav, sr=SR, mono=True)
    finally:
        os.path.exists(wav) and os.remove(wav)
    if y.size == 0:
        raise FeatureError("empty audio")
    dur = len(y) / sr

    tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
    bpm = float(np.atleast_1d(tempo)[0])
    chroma = librosa.feature.chroma_cqt(y=y, sr=sr)
    key, mode, mode_sign = _key(chroma.mean(axis=1))
    rms = float(librosa.feature.rms(y=y).mean())
    centroid = float(librosa.feature.spectral_centroid(y=y, sr=sr).mean())
    rolloff = float(librosa.feature.spectral_rolloff(y=y, sr=sr).mean())
    bandwidth = float(librosa.feature.spectral_bandwidth(y=y, sr=sr).mean())
    zcr = float(librosa.feature.zero_crossing_rate(y).mean())
    peak = float(np.max(np.abs(y)) or 1e-9)
    crest = 20 * np.log10(peak / (rms + 1e-9))        # dynamics proxy (dB)

    features = {
        "duration_s": round(dur, 1), "bpm": round(bpm, 1), "key": key, "mode": mode,
        "rms": round(rms, 4), "crest_db": round(float(crest), 1),
        "spectral_centroid_hz": round(centroid), "spectral_rolloff_hz": round(rolloff),
        "spectral_bandwidth_hz": round(bandwidth), "zero_crossing_rate": round(zcr, 4),
    }
    va = _va(bpm, rms, centroid, mode_sign, sr)

    # per-segment V/A for the timeline
    seglen = max(1, len(y) // segments)
    timeline = []
    for i in range(0, len(y), seglen):
        s = y[i:i + seglen]
        if len(s) < sr // 2:
            continue
        srms = float(librosa.feature.rms(y=s).mean())
        sc = float(librosa.feature.spectral_centroid(y=s, sr=sr).mean())
        t0 = i / sr
        timeline.append({"t0": round(t0, 1), "t1": round(min(dur, t0 + seglen / sr), 1),
                         "va": _va(bpm, srms, sc, mode_sign, sr)})
    return {"features": features, "va": va, "timeline": timeline}
