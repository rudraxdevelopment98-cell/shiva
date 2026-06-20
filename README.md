# 🎚️ Auto Mix & Master

> Working title: **Mastr** (name TBD). Owner: Kuldeep · Solo build.
> An automatic **mixing & mastering** tool — drop in a track (or stems) and get
> back a polished, loudness-correct master, with clear before/after metrics.

This repo was reset from a previous project. Fresh start.

---

## What we're building

A tool that takes raw audio and makes it sound finished — automatically:

- **Auto-master (first):** a finished stereo mix → a clean master at a chosen
  streaming loudness target (e.g. −14 LUFS), with true-peak limiting, gentle
  tonal balance, and a before/after report (LUFS, true peak, dynamic range).
- **Reference match (next):** "make my track sound like *this* reference."
- **Auto-mix (later):** balance multiple stems (levels, panning, EQ, glue).

The hard part — and the value — is the **audio engine**. UI comes on top of it.

## Engine MVP (in this repo)

`engine/` is a Python audio engine. The v0 master uses a **two-pass EBU R128
loudnorm** (via ffmpeg) — a real, robust master for loudness + true-peak
control — plus an analysis pass that reports the numbers.

```bash
# on your Mac (one-time)
brew install ffmpeg
pip install -r requirements.txt

# Desktop app (native window) — the main way to use it
python desktop.py

# …or the same UI in a browser
python app.py            # → http://127.0.0.1:5000

# …or the command line
python cli.py master input.wav out.wav --lufs -14 --preset warm
python cli.py mix drums.wav bass.wav vocals.wav -o mix.wav --lufs -14 --preset clean
python cli.py match mine.wav reference.wav -o matched.wav
python cli.py analyze out.wav
```

## What works now
- **Master** a finished mix to a loudness target (−14 / −9 / −16 LUFS) with
  true-peak limiting + an optional tone chain (`clean` / `warm` / `bright` / `loud`).
- **Auto-mix** 2+ stems: loudness-balance each → sum on a headroom bus → master.
- **Reference match**: make your track match the tone + loudness of a song you like.
- **Analyze**: LUFS / true peak / dynamic range, before & after.
- **Desktop app** (pywebview) and a browser app (Flask) over the same engine.

## Roadmap

| Phase | What | Tech | State |
|---|---|---|---|
| **0 — Engine** | Loudness master + analysis | ffmpeg | ✅ |
| **1 — Master chain** | EQ, compression, glue, limiter | `pedalboard` | ✅ presets |
| **1b — Auto-mix v0** | Balance stems → bus → master | ffmpeg | ✅ |
| **2 — Reference match** | Match a reference track's tone + loudness | `matchering` | ✅ |
| **3 — Desktop polish** | A/B, waveforms, batch, presets UI | pywebview | next |
| **4 — Smarter mix** | Per-stem EQ / pan / role-aware balance | DSP + ML | later |

## Why Python for the engine
Audio DSP/ML lives in Python: `pedalboard`, `matchering`, `pyloudnorm`,
`soundfile`, `librosa`, plus `ffmpeg` for I/O. The engine stays UI-agnostic so
we can put a CLI, a web app, or a desktop app on top of the same core.

## Status
Phase 0 scaffold. See [`docs/plan.md`](docs/plan.md).
