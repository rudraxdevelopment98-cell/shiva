-- SonicDNA — Postgres schema (ERD as SQL). Needs: CREATE EXTENSION vector;
create extension if not exists vector;

create table users (
  id uuid primary key default gen_random_uuid(),
  email text unique not null,
  password_hash text,                 -- null if OAuth-only
  mfa_secret text,
  plan text not null default 'free',  -- free|pro|studio|enterprise
  created_at timestamptz default now()
);

create table api_keys (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references users(id) on delete cascade,
  hash text not null, label text, last_used_at timestamptz,
  created_at timestamptz default now()
);

create table tracks (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references users(id) on delete cascade,
  title text, artist text,
  storage_key text not null,          -- S3 object
  duration_s real, sample_rate int, sha256 text,
  created_at timestamptz default now()
);

create table analyses (
  id uuid primary key default gen_random_uuid(),
  track_id uuid references tracks(id) on delete cascade,
  status text not null default 'queued',     -- queued|running|done|error
  model_version text, error text,
  features jsonb,                              -- bpm,key,chords,lufs,dynamics,spectral…
  dna jsonb,                                   -- {emotion: prob} full-track
  embedding vector(256),                       -- for similarity (pgvector)
  created_at timestamptz default now(), finished_at timestamptz
);
create index on analyses (track_id);
create index on analyses using ivfflat (embedding vector_cosine_ops);

-- per-segment timeline (heatmap)
create table timeline_segments (
  id bigserial primary key,
  analysis_id uuid references analyses(id) on delete cascade,
  t0 real not null, t1 real not null,
  dna jsonb not null
);
create index on timeline_segments (analysis_id);

-- normalized emotion scores (queryable: "find nostalgic tracks")
create table emotion_scores (
  analysis_id uuid references analyses(id) on delete cascade,
  emotion text not null, score real not null,
  primary key (analysis_id, emotion)
);
create index on emotion_scores (emotion, score desc);

create table subscriptions (
  id uuid primary key default gen_random_uuid(),
  user_id uuid references users(id) on delete cascade,
  plan text not null, stripe_customer text, stripe_sub text,
  status text, renews_at timestamptz
);

create table audit_log (
  id bigserial primary key,
  user_id uuid, action text, meta jsonb, at timestamptz default now()
);
