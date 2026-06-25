# SonicDNA — Roadmap, sprints, costs

2-week sprints. Each phase ends at a gate (ship + validate before next).

## Phase 0 — Foundation (S1–S2)
Monorepo, CI/CD, Terraform skeleton, auth (OAuth+MFA), Postgres+pgvector, S3,
upload→validate→scan→store. **Gate:** secure upload + job queue working.

## Phase 1 — Analysis MVP, web (S3–S7)  ★ the wedge
DSP features (BPM,key,chords,LUFS,dynamics,spectral). Audio-emotion model =
pretrained embedding (e.g. CLAP/PANNs) → classifier on **DEAM/EMOPIA**. ONNX serve.
Web: upload → **Emotional DNA + timeline heatmap + features**. Similarity (pgvector).
Free/Pro + Stripe. **Gate:** top-1 ≥60% vs human on holdout; real users analyzing.

## Phase 2 — Depth (S8–S12)
Lyrics sentiment + vocal-emotion + instrument detection → **fusion model**.
Human-annotation pipeline (active learning). Catalog batch ingest. Export.
**Gate:** fusion beats audio-only; sync/curator pilot user.

## Phase 3 — Reach (S13–S18)
Flutter app (analysis client). **JUCE plugin v1**: on-buffer near-real-time DNA
(quantized ONNX) + heatmap UI; deep pass via backend. **Gate:** plugin in a DAW,
producers using it.

## Phase 4 — Scale (S19+)
Realtime research (<100 ms → push lower), enterprise (SSO, on-prem), MSD-scale
catalog + similarity, SOC2.

## Team (lean)
ML/DSP eng, backend eng, full-stack/web, (Phase 3) Flutter + JUCE/C++ contractor,
part-time DevOps + designer. Solo-founder route: do Phase 0–1 yourself, contract Phase 3.

## Cost (indicative, monthly cloud)
MVP (Phase 1): **~$150–400** (Fargate + RDS + S3 + CloudFront, low traffic).
Phase 3 w/ realtime: **$1–4k**. Training: spot GPU bursts ~$200–800 one-off.
Datasets are free/research-licensed — **verify licenses before commercial use.**

## Monetization
Free (5/mo) · Pro (~$12/mo, 200 + similarity) · Studio (~$49, API+batch) ·
Enterprise (custom, SSO/on-prem/SLA).

## Investor deck (outline)
1 Problem · 2 Insight (emotion = the missing axis) · 3 Product/demo · 4 Why now
(audio ML matured) · 5 Market (artists, sync, catalog, streaming) · 6 Moat
(taxonomy + annotated data + embeddings) · 7 Business model · 8 Roadmap · 9 Team
· 10 Ask + use of funds.

## Top risks
Emotion is subjective (→ measure agreement, multi-label, per-segment) · dataset
licensing · 20 ms plugin (deferred) · ML eval honesty (hold out, report agreement).
