# SonicDNA

> AI platform that **detects, visualizes, categorizes and improves music emotion**.
> Outputs an **emotional DNA** (probability vector over 30–50 emotions) + timeline
> heatmaps + similarity search — across **web, mobile, and a DAW plugin**.

This folder holds the **production blueprint** (PRD, architecture, schema, API,
roadmap, costs) plus a runnable backend skeleton. It is a planning + scaffold
tree, not a finished platform — see the honest scope note below.

## Honest scope (read first)
Full spec = **18–24 months, a funded team** (ML + DSP + full-stack + DevOps).
The two hardest claims and how we de-risk them:
- **<20 ms plugin inference:** an ML model in the audio thread is research-hard.
  → Plugin **v1 ships analysis-on-buffer (offline/near-real-time)**, not 20 ms live.
- **Emotion models:** require training + labeled data. → Start from **pretrained
  audio embeddings + a light classifier** on public datasets before custom models.

**Therefore the MVP wedge = the web app: upload a track → Emotional DNA + timeline
heatmap + similar songs.** Everything else (mobile, plugin, fusion models, real-time)
sequences off that. See [`docs/ROADMAP.md`](docs/ROADMAP.md).

## Deliverables (index)
| Doc | What |
|---|---|
| [PRD](docs/PRD.md) | Product requirements, users, scope |
| [ARCHITECTURE](docs/ARCHITECTURE.md) | System design, monorepo, stack |
| [SCHEMA.sql](docs/SCHEMA.sql) | Postgres ERD (incl. pgvector) |
| [API](docs/API.md) | REST + WS endpoints |
| [TAXONOMY](docs/TAXONOMY.md) | 36-emotion label set |
| [ROADMAP](docs/ROADMAP.md) | Phases, sprints, costs, investor outline |
| `backend/` | FastAPI skeleton (health + analyze stub) |

## Run the backend skeleton
```bash
cd sonicdna/backend && pip install -r requirements.txt
uvicorn main:app --reload      # http://127.0.0.1:8000/docs
```
