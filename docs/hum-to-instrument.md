# Hum → Instrument  (working concept)

> **The idea:** you hum, sing, or beatbox an idea — the tool turns it into a
> clean, perfectly-timed, in-key **instrument part** placed right on the grid,
> with zero cleanup. Eventually a DAW plugin; first, a standalone proof.

## Why it could be a real invention
Audio-to-MIDI already exists (Ableton convert-to-MIDI, Dubler 2, Jam Origin,
Spotify's `basic-pitch`). **But it's messy** — wrong notes, loose timing, no
musical context — so people still hand-fix everything. The opening is making it:

- **Effortless** — hum → usable part, no editing.
- **Musically correct** — auto-quantized to the project tempo and **snapped to
  the song's key/scale** (and later, its chords), so the result is always *in tune
  with the song*.
- **Realised, not just notes** — voiced as a real-sounding instrument (bass,
  keys, plucks, or drums from beatbox), not raw MIDI you have to assign.
- **In your DAW** — capture a hum in a clip, get the part back in place.

That combination — *capture-time, automatic, in-context, clean* — is what no tool
nails today. That's the wedge.

## Architecture (UI-agnostic engine, like before)

```
hum.wav ─▶ transcribe (pitch + rhythm)  ─▶ quantize to BPM ─▶ snap to key/scale ─▶ MIDI
                                                                          └▶ (optional) render with an instrument → audio
```

- **Transcribe:** Spotify **`basic-pitch`** (open source) → notes (pitch, start, end).
- **Quantize:** snap note starts/ends to a grid (1/8, 1/16…) at the project BPM.
- **Key-snap:** move each note to the nearest pitch in the chosen key/scale.
- **Render (optional):** MIDI → audio via a soundfont (fluidsynth) for a preview;
  in a DAW you'd just route the MIDI to any instrument.

Keep the engine standalone so a CLI, the desktop app, or (later) a JUCE plugin
all reuse the same core.

## Phases
1. **Magic core (now):** `hum2inst/` — wav → clean, quantized, in-key MIDI. CLI.
2. **Preview + UI:** render to audio so you can *hear* it; add to the desktop app.
3. **Validate:** show producers a hum → result clip. Do they say "I need this"?
4. **Plugin (big):** JUCE VST3/AU — record a hum in a clip, generate the part in place.

## Honest difficulty
- Monophonic (one hummed line) transcription is **solid** today. Polyphonic and
  beatbox→drum-kit classification are **harder** (next steps).
- The plugin shell (C++/JUCE, real-time, host tempo/key) is the **biggest lift** —
  deliberately last, after the magic is proven.

## Open questions
- **Faithful vs corrected:** transcribe exactly what you hummed, or auto-fix it to
  the song's key/chords (more "perfect", less literal)? *(Lean: offer both, default corrected.)*
- **First instruments:** melodic (bass / keys / lead) or **beatbox → drums**?
- **Record-then-generate** (simpler) vs **real-time** (harder)?
