# Spec 004 — Deploy backend + frontend to AWS

> Source of truth for **feature 3** (point 4e of the test: "Deploy the project to
> a cloud provider and share the URL"). Defines the deployment artifacts and the
> contract they must satisfy. The actual `apply`/upload runs with the owner's AWS
> credentials and is out of scope for automated tests.

## 4.1 Target topology (decided)

- **Backend (FastAPI)** → container image → **AWS App Runner**.
  - App Runner builds/runs the image, gives an HTTPS URL, autoscales, no VPC/ALB
    to manage.
- **Frontend (React/Vite)** → static build (`dist/`) → **S3 bucket** served via
  **CloudFront** (HTTPS CDN). No container for the frontend.

Rationale: lowest cost/effort that still satisfies "deployed to a cloud provider
with a shareable URL". ECS/EC2 were rejected as over-infra for an assessment
(see `docs/platform_architecture.md` for the full-platform shape).

## 4.2 Backend container — requirements

A `backend/Dockerfile` MUST:

- D1: Use a slim official Python base image (e.g. `python:3.12-slim`).
- D2: Install only `backend/requirements.txt` (layer-cached: copy requirements
  first, then the app).
- D3: Run as a **non-root** user.
- D4: Start the app with a production server command binding `0.0.0.0` and a
  configurable `$PORT` (App Runner injects `PORT`, default 8000):
  `uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}`.
- D5: Be accompanied by a `backend/.dockerignore` excluding `venv/`,
  `__pycache__/`, tests caches, etc.
- D6: Image builds locally (`docker build`) and `GET /health` returns
  `{"status":"ok"}` when the container runs.
- D7: CORS — the deployed frontend origin (CloudFront URL) must be allowed. The
  backend already reads `CORS_ORIGINS` from env (spec 003); deployment sets it,
  no code change required.

Optional: an `apprunner.yaml` or a short `deploy/backend-apprunner.md` documenting
the App Runner service settings (port, health check path `/health`, the
`CORS_ORIGINS` env var).

## 4.3 Frontend static deploy — requirements

- F1: `npm run build` produces `frontend/dist/` (already configured via Vite).
- F2: Build-time env: `VITE_API_BASE_URL` must point to the deployed App Runner
  URL (not localhost); `VITE_GOOGLE_MAPS_API_KEY` is supplied at build time.
- F3: A documented, repeatable deploy path to S3 + CloudFront — either:
  - a short script `deploy/frontend-deploy.sh` (`aws s3 sync dist/ s3://… ` +
    CloudFront invalidation), **or**
  - `deploy/frontend-s3-cloudfront.md` with the exact steps/commands.
- F4: SPA routing note: CloudFront/S3 should serve `index.html` for unknown paths
  (custom error response 403/404 → `/index.html`), so the single-page app works.

## 4.4 Documentation — requirements

- G1: A `deploy/README.md` that ties it together: prerequisites (AWS account,
  credentials, a Google Maps key valid for the CloudFront origin), the order of
  operations (deploy backend → get URL → build frontend with that URL → upload),
  and where to paste the final two URLs.
- G2: The Google Maps API key restriction must be updated to include the
  CloudFront domain (the localhost-only restriction won't work in prod) — call
  this out explicitly.

## 4.5 Out of scope (explicit)

- Running the actual AWS deploy (needs the owner's AWS credentials/account). The
  artifacts must be correct and runnable, but executing them and pasting the live
  URLs is a manual step for the repo owner.
- No CI/CD pipeline required for the assessment (can be noted as a future step).

## 4.6 Definition of done

- `backend/Dockerfile` + `backend/.dockerignore` satisfy D1–D7; image builds and
  `/health` responds.
- Frontend deploy path (F1–F4) is documented and repeatable.
- `deploy/README.md` (G1–G2) exists and is accurate.
- `./init.sh` still exits 0 (no regression to backend/frontend builds/tests).
- Once the owner runs it, the two live URLs are pasted into `deploy/README.md`
  and/or the top-level `README.md`.
