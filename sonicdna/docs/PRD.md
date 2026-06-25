# SonicDNA — PRD (condensed)

## Problem
Music is described by genre/BPM, but **felt** by emotion. No tool gives artists,
supervisors, or listeners a precise, structured read of a song's emotion over time.

## Users & jobs
- **Artist/producer:** "Does my track land the feeling I intend? Where does it dip?"
- **Sync/music supervisor:** "Find tracks that feel *nostalgic + hopeful* for this scene."
- **Curator/label:** tag catalog by emotion; find similar-feeling songs.
- **Listener (later):** discover by mood.

## Core value
Upload/stream audio → **Emotional DNA**: a probability vector over 36 emotions,
a **timeline heatmap** (emotion vs time), and **similarity search** by feeling.

## MVP (web, offline analysis)
1. Upload track (or paste link) → async analysis job.
2. **Emotional DNA** vector + top emotions + confidence.
3. **Timeline heatmap** (per-segment emotion).
4. **Audio features** surfaced: BPM, key, chords, LUFS, dynamics, spectral.
5. **Similar songs** by emotional embedding.
6. Accounts + Free/Pro gating + export (JSON/PNG).

## Later
Lyrics sentiment · vocal-emotion · instrument detection · **fusion model** ·
Flutter app · JUCE plugin (analysis-on-buffer) · realtime · catalog ingestion.

## Outputs (not single labels)
- `dna`: `{emotion: prob}` over the full taxonomy (sums≈1 within groups).
- `timeline`: `[{t0,t1, dna}]`.
- `embedding`: vector for similarity (pgvector).
- `features`: objective DSP metrics.

## Non-goals (v1)
Real-time <20 ms · on-device mobile inference · stem separation · generation.

## Success metrics
Analysis p95 < 30 s (3-min track) · emotion top-1 agreement vs human ≥ 60% on
DEAM holdout · web signup→analysis ≥ 40% · Pro conversion ≥ 3%.
