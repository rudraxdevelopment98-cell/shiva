# Hum → Instrument 🎤→🎹

Hum, sing, or beatbox an idea → get a clean, quantized, **in-key** MIDI part you
can drop on any instrument in your DAW. The "magic core" (Phase 1) of the
hum-to-instrument concept — see [`../docs/hum-to-instrument.md`](../docs/hum-to-instrument.md).

## Try it (on your Mac)
```bash
pip install -r hum2inst/requirements.txt
python -m hum2inst.transcribe myhum.wav -o part.mid --bpm 90 --key Amin
# then drag part.mid onto a bass / piano / synth track in your DAW
```

Options:
- `--bpm` your song's tempo (so it lands on the grid)
- `--key` your song's key, e.g. `Cmaj`, `Amin`, `F#minpent` (notes get snapped in-key)
- `--grid` quantize resolution (8 / 16 / 32)
- `--faithful` keep exactly what you hummed (skip key-snapping)

## What it does
1. **Transcribe** your hum to notes (Spotify `basic-pitch`).
2. **Quantize** note timing to the grid at your BPM.
3. **Snap** every note into your song's key/scale (unless `--faithful`).
4. **Write** a `.mid` — assign it to any instrument.

## Next
- Render a quick audio preview (soundfont) so you can hear it without a DAW.
- Beatbox → drum-kit mapping (kick/snare/hat).
- Chord-aware correction (fit to the song's chords, not just key).
- Eventually: a DAW plugin that records your hum and drops the part in place.
