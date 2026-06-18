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
# on your Mac
brew install ffmpeg
pip install -r requirements.txt           # (python deps for later stages)

python cli.py master input.wav output.wav --lufs -14 --tp -1
python cli.py analyze output.wav          # prints LUFS / true peak / etc.
```

## Roadmap

| Phase | What | Tech |
|---|---|---|
| **0 — Engine v0** | Loudness master (loudnorm 2-pass) + analysis report | ffmpeg |
| **1 — Master chain** | EQ, multiband compression, glue, limiter | `pedalboard` (Spotify) |
| **2 — Reference match** | Match a reference track's tone + loudness | `matchering` |
| **3 — UI** | Upload → process → A/B compare + waveforms + download | web (TBD) |
| **4 — Auto-mix** | Balance stems: levels, pan, EQ, dynamics | DSP + heuristics/ML |

## Why Python for the engine
Audio DSP/ML lives in Python: `pedalboard`, `matchering`, `pyloudnorm`,
`soundfile`, `librosa`, plus `ffmpeg` for I/O. The engine stays UI-agnostic so
we can put a CLI, a web app, or a desktop app on top of the same core.

## Status
Phase 0 scaffold. See [`docs/plan.md`](docs/plan.md).
