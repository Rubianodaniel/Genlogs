# Review — feature 3 (deploy)

**Verdict:** APPROVED

Reviewed against `specs/004-deploy.md` (D1–D7, F1–F4, G1–G2, DoD §4.6),
`docs/architecture.md`, `docs/conventions.md`, `CHECKPOINTS.md` (C13).

## Backend container — D1–D7
- D1 [x] `python:3.12-slim` slim official base (`backend/Dockerfile:8`).
- D2 [x] `requirements.txt` copied + installed before `COPY app ./app` (lines 19–23) → layer-cached.
- D3 [x] Non-root: `useradd ... --uid 10001 appuser`, `USER appuser` (lines 26–28). Report confirms `id` = uid 10001.
- D4 [x] `CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}` shell form so $PORT expands (line 37). Binds 0.0.0.0, defaults 8000.
- D5 [x] `.dockerignore` excludes venv/, .venv/, __pycache__/, .pytest_cache/, tests/, .env*, *.md, .git/, Dockerfile.
- D6 [x] Report documents executed `docker build backend/` + `docker run` → `/health` = {"status":"ok"} on default and injected PORT=9090. Build context correct (Dockerfile in backend/, COPY paths relative to backend/).
- D7 [x] No app change: `backend/app/interface/settings.py:52` reads `CORS_ORIGINS` from env (defaults to localhost). Deploy docs set it to CloudFront origin (`backend-apprunner.md` §CORS/§4, `apprunner.yaml`, README step 5).

## Frontend deploy — F1–F4
- F1 [x] `npm run build` → `dist/` (Vite); init.sh builds dist with hashed assets.
- F2 [x] `frontend-deploy.sh` injects `VITE_API_BASE_URL` (App Runner URL, not localhost) + `VITE_GOOGLE_MAPS_API_KEY` at build time; required-var guards present (lines 19–22).
- F3 [x] Both a repeatable script (`frontend-deploy.sh`, chmod +x) and `frontend-s3-cloudfront.md` with exact commands + manual equivalent.
- F4 [x] SPA routing: CloudFront custom error responses 403 AND 404 → `/index.html` (200) documented in `frontend-s3-cloudfront.md` and README step 2; 403 correctly justified for private S3+OAC origin.

## Documentation — G1–G2
- G1 [x] `deploy/README.md`: prerequisites, correct order (backend → URL → frontend build w/ URL → upload → invalidate → CORS), "Live URLs" paste section.
- G2 [x] Google Maps key restriction must include CloudFront domain called out explicitly (README step 4; `frontend-s3-cloudfront.md` §Google Maps key).

## DoD §4.6 / process
- [x] Dockerfile + .dockerignore satisfy D1–D7; image builds, /health responds (per report).
- [x] Frontend path documented and repeatable.
- [x] deploy/README.md exists and accurate.
- [x] `./init.sh` re-run by reviewer → EXIT 0 (backend pytest + frontend build + 12 vitest pass).
- [x] No leakage into `backend/app/**`, `src/`, `tests/` (git status: only new infra/docs + progress/specs; app untouched).
- [x] `feature_list.json` feature 3 still `in_progress` (NOT marked done by implementer).
- Cloud `apply` + live URLs = out of scope per §4.5 (manual owner step).

## Checkpoints
- C13 [ ] deploy — artifacts complete and verified; remains unchecked until owner runs the AWS apply and pastes live URLs (out of scope per §4.5). No blocker on the implementer.

## Required changes
None.

**APPROVED** — all in-scope DoD items met; init.sh exit 0; no app-code leakage; feature left in_progress as required.
