# Plan — Auto Mix & Master

## Thesis
Most people can record or produce something, but **can't make it sound finished**.
Mixing and mastering are the gap. Automate the "make it sound pro" step with a
tool that's fast, honest about what it did, and good enough to ship.

## Principles
- **Engine first.** The DSP is the product; UI is a wrapper. Keep the engine
  UI-agnostic so a CLI, web app, or plugin can all reuse it.
- **Show the numbers.** Always report LUFS / true peak / dynamic range before &
  after — trust comes from transparency, not magic.
- **Ship the smallest useful thing**, then add chain stages from real feedback.

## Phases

### Phase 0 — Loudness master (now)
- Two-pass EBU R128 loudnorm to a target (−14 LUFS streaming default) + true-peak limit.
- Analysis report. CLI: `master`, `analyze`.
- **Done when:** a raw mix in → a loudness-correct master out, with a before/after report.

### Phase 1 — Master chain
- Add a real chain with `pedalboard`: high-pass, gentle tonal EQ, multiband/
  glue compression, then a brick-wall limiter to the loudness target.
- Presets: *Streaming*, *Warm*, *Bright*, *Loud*.

### Phase 2 — Reference matching
- `matchering`: match a user-supplied reference track's spectrum + loudness.
- "Make mine sound like this."

### Phase 3 — UI
- Upload → process → **A/B compare**, waveforms, LUFS meters, download.
- Decide platform (web vs desktop) when the engine is good enough to show off.

### Phase 4 — Auto-mix (stretch)
- Multitrack stems → balanced mix: level-set to targets, panning, corrective EQ,
  de-mud, glue. Heuristics first; ML later.

## Open questions (to confirm)
- **Mastering-first vs mixing-first?** (Recommend mastering — far more tractable.)
- **Form factor for the eventual UI?** (Web app, desktop, or a DAW plugin.)
- **Quality bar / reference:** what do "good" results sound like to you?
- **Offline (local on your Mac) vs hosted service** for processing?
