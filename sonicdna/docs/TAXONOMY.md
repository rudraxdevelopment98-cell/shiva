# SonicDNA — Emotion taxonomy (36)

Grouped (Russell valence/arousal-inspired). DNA = probabilities; groups help the
heatmap and UI. Versioned (`taxonomy_v1`) so models/labels stay in sync.

| Group | Emotions |
|---|---|
| **Joy / high-positive** | joy, euphoria, excitement, playfulness, triumph, awe |
| **Warm / positive** | love, romance, tenderness, hope, gratitude, serenity, contentment |
| **Bittersweet** | nostalgia, longing, melancholy, bittersweet, wistfulness, catharsis |
| **Sad / low** | sadness, grief, loneliness, despair, regret |
| **Tension / dark** | anger, tension, fear, anxiety, menace, mystery |
| **Energy / drive** | confidence, power, determination, rebellion |
| **Calm / neutral** | dreamy, meditative, detachment |

Notes:
- Models output the **full 36-vector**; UI shows top-k + group rollups.
- Human-annotation pipeline uses this exact list + intensity (0–3) per segment.
- Multi-label (a track can be nostalgic **and** hopeful) — not single-class.
