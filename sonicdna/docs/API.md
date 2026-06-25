# SonicDNA — API (v1)

Auth: `Authorization: Bearer <jwt>` or `X-API-Key`. JSON. Errors: RFC 7807.

## Auth
- `POST /v1/auth/register` `{email,password}` → user
- `POST /v1/auth/login` `{email,password,otp?}` → `{access,refresh}`
- `POST /v1/auth/refresh` `{refresh}` → `{access}`
- `POST /v1/auth/mfa/enable` → otpauth uri

## Analysis
- `POST /v1/analyze` (multipart `file` **or** `{url}`) → `202 {analysis_id,status}`
  - validates type/size/duration, malware-scans, enqueues.
- `GET /v1/analyses/{id}` → `{status, features, dna, model_version}`
- `GET /v1/analyses/{id}/timeline` → `[{t0,t1,dna}]`  (heatmap data)
- `GET /v1/analyses/{id}/export?fmt=json|png` → file
- `WS /v1/analyses/{id}/stream` → progress + result push

## Similarity & search
- `POST /v1/similar` `{analysis_id, k?}` → `[{track_id,score}]`  (pgvector cosine)
- `GET /v1/search?emotion=nostalgia&min=0.6` → tracks ranked by emotion_scores

## Account / billing
- `GET /v1/me` · `GET /v1/usage`
- `POST /v1/billing/checkout` `{plan}` → Stripe session
- `POST /v1/webhooks/stripe` (signed)

## Plugin (near-real-time)
- Local ONNX on-buffer; optional `POST /v1/analyze` for deep pass.
- `GET /v1/models/latest?target=plugin` → signed ONNX URL + version.

## Limits (per plan)
free: 5 analyses/mo · pro: 200 + similarity · studio: unlimited + API + batch ·
enterprise: SSO, on-prem, SLA. Rate-limit headers on every response.
