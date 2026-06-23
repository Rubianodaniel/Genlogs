# Current session

> Living state of the active session. The leader and subagents write here as they
> work, not at the end. Empty it (leaving this template) at session close.

## Active feature

- **id:** 3 — Deploy backend + frontend to a cloud provider
- **status:** in_progress (implementer)
- **start time:** 2026-06-22
- **spec:** specs/004-deploy.md

### Deploy decision (feature 3)

- Target: backend FastAPI → Docker image → **AWS App Runner**; frontend Vite
  build → **S3 + CloudFront** (static, no container). Chosen for lowest
  cost/effort; ECS/EC2 rejected as over-infra for an assessment.
- Artifacts to produce: `backend/Dockerfile` + `backend/.dockerignore`,
  `deploy/` docs/scripts (App Runner notes, frontend S3/CloudFront deploy),
  `deploy/README.md` tying it together.
- Out of scope: running the real AWS apply (needs owner's AWS creds) — artifacts
  must be correct/runnable; live URLs pasted later by the owner.

### Implementer plan (feature 2)

- Scaffold `frontend/` (Vite + React + TS + Tailwind + Vitest) under FSD layers.
- shared/config: env access (VITE_API_BASE_URL, VITE_GOOGLE_MAPS_API_KEY).
- shared/api: fetch wrapper (http client, base URL from env).
- entities/carrier: Carrier type + presentational CarrierItem.
- features/search-corridor: api (carriersApi POST /carriers), model (useSearchCorridor
  hook = business logic + state machine idle→loading→loaded/error), ui (CityInput
  with Places autocomplete + SearchPanel).
- widgets/route-map (Google Map + DirectionsService alternatives, up to 3 routes),
  widgets/carrier-list (presentational list).
- app/App.tsx (APIProvider), pages/portal (composition).
- Tests (Vitest + RTL, mocks only): carriersApi (mock fetch), useSearchCorridor
  (mock api), CarrierListWidget (presentational). No real network / Maps in tests.
- Extend init.sh to run frontend build+test guarded by `command -v npm` && frontend dir.

### Implementer plan (feature 4)

- Add reusable `CityField` Annotated type in `interface/schemas.py` (DRY): trim,
  min 1 / max 100, allowed-char pattern (unicode letters, space, `. , ' -`).
  Reuse for `CarriersRequest` (POST) and GET query params; `extra="forbid"`.
- Output DTOs: `trucks_per_day: int = Field(ge=0)`, `CarriersResponse`
  `extra="forbid"`.
- New `interface/settings.py`: `Settings` Singleton via `lru_cache`, reads
  `CORS_ORIGINS` env (default localhost:5173,3000) using `os.getenv` (no new dep).
- `main.py create_app()`: CORS from settings (no `*`), methods GET/POST/OPTIONS,
  drop credentials+`*`; security-headers middleware; generic 500 handler.
- TDD unit tests in `tests/test_validation_security.py` covering spec 003 §3.5.
- No domain/application changes; spec-001 behavior unchanged.

## Implementer plan (clean-arch refactor)

- Relocate flat `app/carriers.py` + `app/main.py` into Clean Arch layers:
  domain (entities + port), application (use case), infrastructure (in-memory
  repo with verbatim data + alias normalization), interface (schemas, deps
  composition root, router), main (create_app factory).
- TDD unit tests: use case with mock repo; repo direct (3 rules + aliases);
  router via dependency_overrides with fake use case; /health.
- Behavior identical to spec 001. Remove old flat module.

## Plan

- Go-ahead received from hiring manager (John). Proceed with implementation.
- Points 2 (architecture) and 3 (DB design) written as docs by leader.
- Feature 1 (backend) delegated to `implementer` per spec 001.
- Next: feature 2 (frontend), then deploy (feature 3).

## Notes / decisions

- John wants estimated vs actual effort tracked → deliverables/05_time_tracking.md.
- Engineering standards encoded in docs/conventions.md (Clean Arch, TDD, DI/mocks,
  SOLID/Factory/Singleton/Repository, FSD frontend). Flow diagrams in specs/.
- Frontend stack decided: React+TypeScript, Vite, Tailwind, @vis.gl/react-google-maps.
- Decision: refactor backend (flat) → Clean Architecture + TDD BEFORE frontend.

### Implementer plan (feature 3 — deploy) — STARTED 2026-06-22

- Artifacts (infra/docs only, no app code changes — CORS already env-driven):
  - `backend/Dockerfile`: python:3.12-slim, requirements copied first (layer
    cache), non-root user, `uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}`.
  - `backend/.dockerignore`: venv/, __pycache__/, .pytest_cache/, tests caches.
  - `deploy/README.md` (G1–G2): prereqs, order of ops, where to paste live URLs,
    Google Maps key restriction callout for CloudFront domain.
  - `deploy/backend-apprunner.md` + `apprunner.yaml`: port, health `/health`,
    `CORS_ORIGINS` env (must include CloudFront origin).
  - `deploy/frontend-deploy.sh` + `deploy/frontend-s3-cloudfront.md` (F3/F4 SPA
    routing: CloudFront 403/404 -> /index.html 200).
- Docker IS available -> will run `docker build` + curl /health to satisfy D6.

## Blockers

- None. Feature 2 implemented; Node present so build + tests ran green.
  Full report in progress/impl_2.md. Awaiting reviewer.
