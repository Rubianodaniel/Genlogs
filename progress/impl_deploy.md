# Implementation report — feature 3 (deploy)

- **Feature:** 3 — Deploy backend + frontend to a cloud provider
- **Spec:** `specs/004-deploy.md`
- **Scope:** infra/docs only. No changes to `src/`, `tests/`, or `backend/app/**`
  (CORS is already env-driven via `CORS_ORIGINS`, so no app code change needed).
- **Status:** implemented, awaiting review. Not marked `done`.

## Files created

| File | Purpose | DoD |
| ---- | ------- | --- |
| `backend/Dockerfile` | `python:3.12-slim`, requirements copied before app (layer cache), non-root user `appuser` (uid 10001), shell-form `CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}` | D1–D4 |
| `backend/.dockerignore` | excludes `venv/`, `__pycache__/`, `.pytest_cache/`, `tests/`, `.env*`, `*.md`, `.git/` | D5 |
| `deploy/apprunner.yaml` | documents App Runner settings (port 8000, `CORS_ORIGINS` env) | 4.2 optional |
| `deploy/backend-apprunner.md` | ECR build/push + App Runner create-service, port 8000, health `/health`, `CORS_ORIGINS` incl. CloudFront origin, CORS-update step | D6, D7 |
| `deploy/frontend-deploy.sh` (chmod +x) | build with prod `VITE_*` env → `aws s3 sync dist/ --delete` (immutable assets, no-cache index.html) → CloudFront invalidation | F1–F3 |
| `deploy/frontend-s3-cloudfront.md` | one-time S3+CloudFront setup, SPA custom error responses 403/404 → `/index.html` 200, Google Maps referrer note | F3, F4, F2/G2 |
| `deploy/README.md` | prerequisites, order of operations (backend → URL → frontend build → upload → invalidate), live-URL paste section, explicit Maps-key CloudFront callout | G1, G2 |

## Key decisions

- **Shell-form CMD** (`CMD uvicorn ... --port ${PORT:-8000}`) is intentional so the
  shell expands the App Runner-injected `$PORT`; defaults to 8000 locally. This
  triggers Docker's `JSONArgsRecommended` warning — accepted, as exec/JSON form
  cannot do `${PORT:-8000}` expansion. Signal handling is fine for App Runner.
- **Image-based App Runner** (Dockerfile → ECR → service), not managed
  source-build. `apprunner.yaml` is kept as living documentation of the settings;
  the authoritative runtime config (port/health/env) is set on the service, as
  documented in `backend-apprunner.md`.
- **SPA routing (F4):** CloudFront custom error responses for **both 403 and 404**
  → `/index.html` (200). 403 is required because a private S3 origin via OAC
  returns 403 (not 404) for missing keys.
- **Cache strategy:** fingerprinted assets `max-age=31536000, immutable`;
  `index.html` `no-cache` so redeploys are visible immediately.
- No app code touched — `backend/app/interface/settings.py` already reads
  `CORS_ORIGINS`; deployment just sets it to the CloudFront origin.

## docker build / run — EXECUTED (docker available)

- `docker build -t genlogs-backend backend/` → **success** (image built; only the
  expected `JSONArgsRecommended` warning).
- `docker run -p 18000:8000 genlogs-backend` → `curl /health` → `{"status":"ok"}`.
- `docker exec ... id` → `uid=10001(appuser)` — confirms **non-root** (D3).
- `docker run -e PORT=9090 -p 19090:9090 ...` → `curl /health` → `{"status":"ok"}`
  — confirms the App Runner-style injected `$PORT` works (D4).
- **D6 satisfied locally.**

## init.sh — EXIT 0 (no regression)

- Backend pytest: passed.
- Frontend `npm run build`: built `dist/` (index.html + hashed css/js).
- Frontend vitest: 12 passed (3 files).
- `==> init OK`, exit code 0.

## DoD status

- D1–D5: satisfied by inspection of `backend/Dockerfile` + `.dockerignore`.
- D6: **verified by running the container** (health OK on default and injected port).
- D7: backend already env-driven; `CORS_ORIGINS` documented to include CloudFront.
- F1–F4: documented and scripted (`frontend-deploy.sh` + `frontend-s3-cloudfront.md`).
- G1–G2: `deploy/README.md` ties it together; Maps-key CloudFront restriction
  called out explicitly.

## Remaining manual (out of scope per spec 4.5)

- Running the real AWS apply with the owner's credentials (ECR push, App Runner
  create, S3/CloudFront provision, Maps-key restriction update).
- Pasting the two live URLs into `deploy/README.md` "Live URLs" section.
- No CI/CD pipeline (intentionally out of scope; noted as future work).
