"""Master chain (Phase 1) — EQ / compression / limiting via `pedalboard`.

Lazy-imports pedalboard so the rest of the engine works even when it isn't
installed yet. Install:  pip install pedalboard
"""
from __future__ import annotations


def available() -> bool:
    try:
        import pedalboard  # noqa: F401
        return True
    except Exception:
        return False


PRESETS = ("clean", "warm", "bright", "loud")


def _board(pb, preset: str):
    """Build a mastering Pedalboard for the given preset."""
    fx = [pb.HighpassFilter(cutoff_frequency_hz=30)]  # remove sub rumble
    if preset == "warm":
        fx += [pb.LowShelfFilter(cutoff_frequency_hz=120, gain_db=1.5),
               pb.HighShelfFilter(cutoff_frequency_hz=8000, gain_db=-1.0)]
    elif preset == "bright":
        fx += [pb.HighShelfFilter(cutoff_frequency_hz=8000, gain_db=2.0),
               pb.PeakFilter(cutoff_frequency_hz=300, gain_db=-1.0, q=1.0)]
    elif preset == "loud":
        fx += [pb.Compressor(threshold_db=-20, ratio=3.0, attack_ms=10, release_ms=120)]
    # glue compression (skip if 'loud' already added a stronger one)
    if preset != "loud":
        fx += [pb.Compressor(threshold_db=-18, ratio=2.0, attack_ms=15, release_ms=150)]
    fx += [pb.Gain(gain_db=0.0), pb.Limiter(threshold_db=-1.0, release_ms=100)]
    return pb.Pedalboard(fx)


def apply_chain(src: str, dst: str, preset: str = "clean") -> None:
    """Run the tonal/dynamics chain on `src`, write to `dst` (WAV)."""
    if preset not in PRESETS:
        raise ValueError(f"unknown preset '{preset}' (choose: {', '.join(PRESETS)})")
    import pedalboard as pb
    from pedalboard.io import AudioFile
    with AudioFile(src) as f:
        audio = f.read(f.frames)
        sr = f.samplerate
    out = _board(pb, preset)(audio, sr)
    with AudioFile(dst, "w", sr, out.shape[0]) as f:
        f.write(out)
