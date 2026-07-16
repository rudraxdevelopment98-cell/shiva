"""SonicDNA — emotion DNA from valence/arousal (v0, heuristic + explainable).

Each emotion sits at a point in Valence×Arousal space. A track's (V,A) yields a
probability per emotion via a softmax over closeness. Transparent placeholder to
be replaced by a trained model (audio embedding → classifier) behind the same
`dna_from_va` signature.
"""
from __future__ import annotations
import math

# emotion → (valence, arousal), each in [-1, 1]
VA = {
    "joy": (0.8, 0.6), "euphoria": (0.8, 0.9), "excitement": (0.6, 0.9),
    "playfulness": (0.7, 0.5), "triumph": (0.7, 0.7), "awe": (0.4, 0.5),
    "love": (0.8, 0.2), "romance": (0.7, 0.3), "tenderness": (0.7, 0.0),
    "hope": (0.6, 0.3), "gratitude": (0.7, 0.1), "serenity": (0.6, -0.5),
    "contentment": (0.6, -0.3), "nostalgia": (0.1, -0.1), "longing": (-0.1, 0.1),
    "melancholy": (-0.4, -0.3), "bittersweet": (0.0, 0.0), "wistfulness": (-0.1, -0.2),
    "catharsis": (0.2, 0.6), "sadness": (-0.6, -0.4), "grief": (-0.8, -0.2),
    "loneliness": (-0.6, -0.5), "despair": (-0.8, -0.3), "regret": (-0.5, -0.2),
    "anger": (-0.6, 0.8), "tension": (-0.3, 0.6), "fear": (-0.7, 0.7),
    "anxiety": (-0.5, 0.6), "menace": (-0.6, 0.5), "mystery": (-0.1, 0.2),
    "confidence": (0.5, 0.5), "power": (0.4, 0.8), "determination": (0.4, 0.6),
    "rebellion": (0.0, 0.8), "dreamy": (0.3, -0.4), "meditative": (0.4, -0.6),
}
TAXONOMY = list(VA.keys())


def dna_from_va(v: float, a: float, temp: float = 0.28) -> dict[str, float]:
    """(valence, arousal) → {emotion: probability} (sums to 1)."""
    scores = {}
    for e, (ev, ea) in VA.items():
        d2 = (v - ev) ** 2 + (a - ea) ** 2
        scores[e] = math.exp(-d2 / (2 * temp * temp))
    s = sum(scores.values()) or 1.0
    return {e: round(x / s, 4) for e, x in scores.items()}


def top(dna: dict[str, float], k: int = 6):
    return sorted(dna.items(), key=lambda kv: -kv[1])[:k]
