# 🎵 Music projects — monorepo

Three independent music-tech projects, kept in one repo while exploring. Each is
self-contained; pick a folder and go. (When one gets serious, split it into its
own repo.)

| Project | What it is | Status | Run |
|---|---|---|---|
| **[Auto Mix & Master](#auto-mix--master)** | Upload → polished, loud, streaming-ready master; auto-mix stems; reference match | Working + web product + landing page | `python app.py` |
| **[Hum → Instrument](hum2inst/README.md)** | Hum a line → clean, in-key MIDI instrument part | Working engine + Hum Studio app | `python hum_app.py` |
| **[SonicDNA](sonicdna/README.md)** | Upload → Emotional DNA + timeline heatmap + features | Web MVP (heuristic emotion model) | `uvicorn main:app` in `sonicdna/backend` |

Prereqs across all: `brew install ffmpeg`, Python 3.11+.

---

## Auto Mix & Master
Auto **mastering**, stem **auto-mix**, and **reference matching**, with before/after
LUFS · true-peak · dynamics. Engine in `engine/`; apps: `app.py` (web product with
freemium gate), `desktop.py` (native), `cli.py`. Validation kit in `landing/` +
`docs/validation.md`; monetization plan in `docs/monetization.md`.
```bash
pip install -r requirements.txt   # flask, pywebview, pedalboard, matchering
python app.py                     # http://127.0.0.1:5000
python cli.py master in.wav out.wav --lufs -14 --preset warm
```

## Hum → Instrument  → [`hum2inst/`](hum2inst/README.md)
Hum/sing → transcribe → quantize to BPM → snap to key → MIDI (+ audio preview).
Concept & plan: [`docs/hum-to-instrument.md`](docs/hum-to-instrument.md).
```bash
pip install -r hum2inst/requirements.txt flask
python hum_app.py                 # http://127.0.0.1:5005  (record → generate → hear → save MIDI)
```

## SonicDNA  → [`sonicdna/`](sonicdna/README.md)
Emotion analysis platform (blueprint + runnable web MVP). Real DSP features +
valence/arousal emotion model + timeline heatmap. Full PRD/architecture/schema/
API/roadmap in [`sonicdna/docs/`](sonicdna/docs/).
```bash
cd sonicdna/backend && pip install -r requirements.txt
uvicorn main:app --reload         # http://127.0.0.1:8000
```

---
*Solo builder note: three fronts is a lot — when you're ready to push one hard,
split it out and give it its own repo + focus.*
