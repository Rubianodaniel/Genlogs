# Current session

> Living state of the active session. The leader and subagents write here as they
> work, not at the end. Empty it (leaving this template) at session close.

## Active feature

- **id:** 4 — Backend input/output validation (Pydantic) + security hardening
- **status:** in_progress (implementer)
- **start time:** 2026-06-23

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

## Blockers

-
