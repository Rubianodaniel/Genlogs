# Implementation report — Feature 4: Backend validation (Pydantic) + security hardening

- **Feature id:** 4
- **Spec:** `specs/003-backend-validation-security.md`
- **Status:** implemented, all tests green (`pytest` + `./init.sh`) — awaiting review.
- **Scope:** ADD-only validation + security to the existing Clean Architecture
  backend. All changes live in the **interface layer** + a new settings module.
  Domain and application layers untouched. Spec-001 carrier behavior unchanged.

## Files created

- `backend/app/interface/settings.py` — `Settings` (frozen dataclass) exposed as
  a **Singleton** via `@lru_cache(maxsize=1)` `get_settings()`. Reads
  `CORS_ORIGINS` (comma-separated) from env via `os.getenv`, default
  `http://localhost:5173,http://localhost:3000`. `_parse_origins` trims and drops
  blanks; stores a tuple (immutable/hashable). `cors_origins_list` property
  returns a list for Starlette. No new dependency (no pydantic-settings).
- `backend/tests/test_validation_security.py` — 35 unit tests (parametrized)
  covering every acceptance criterion in spec 003 §3.5 (see below).

## Files changed

- `backend/app/interface/schemas.py`
  - Added DRY shared `CityField = Annotated[str, StringConstraints(...)]`:
    `strip_whitespace=True`, `min_length=1`, `max_length=100`, and pattern
    `^[\p{L}\p{M} .,'\-]+$` (unicode letters incl. accents + combining marks,
    space, `. , ' -`). Rejects empty/whitespace (after trim), oversized,
    digits-only or digit-containing, and injection chars `< > ; { } \ ` `` ` ``.
  - `CarriersRequest`: fields now `CityField`; `model_config =
    ConfigDict(extra="forbid")`.
  - `CarrierOut`: `trucks_per_day: int = Field(..., ge=0)`; `extra="forbid"`.
  - `CarriersResponse`: `extra="forbid"`.
- `backend/app/interface/api.py`
  - GET `/carriers` now validates `from_city`/`to_city` with the **same**
    constraints, reusing `CityField` via `CityQuery = Annotated[CityField,
    Query(...)]`. No unvalidated path into the use case (DRY — one source of
    truth shared by body + query).
- `backend/app/main.py` `create_app()`
  - CORS from `Settings.cors_origins_list` (never `*`),
    `allow_methods=["GET","POST","OPTIONS"]`, `allow_credentials=False`
    (dropped the insecure `*`+credentials combo).
  - `@app.middleware("http")` adds security headers on **every** response:
    `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`,
    `Referrer-Policy: no-referrer`, `Cache-Control: no-store`
    (centralized in `_SECURITY_HEADERS`).
  - Generic `Exception` handler → `500 {"detail": "Internal server error."}`
    (no traceback / internal detail leakage). Validation errors keep FastAPI's
    default clean `422 {"detail": [...]}` shape.
- `backend/tests/test_api_router.py`
  - Updated the pre-existing GET test's sample values from `"Q1"/"Q2"` (now
    invalid — contain digits) to `"Query One"/"Query Two"`. Same assertion
    intent (query params route through to the use case); only the placeholder
    strings changed to satisfy the new validation that this feature introduces.

No rate limiter (out of scope per spec, KISS). No domain/application edits.

## Key decisions

- **DRY**: city constraints defined once (`CityField`) and reused for POST body
  and GET query (`CityQuery`). Single source of truth for the rule.
- **No new deps**: env read with `os.getenv` (spec's preferred path);
  `backend/requirements.txt` unchanged.
- **Output names** (e.g. "Knight-Swift Transport Services") have no pattern —
  only inputs are constrained — so spec-001 names serialize unchanged.
- The no-regression test runs through the **real composition root** (no
  override) to prove NYC→DC still returns the exact spec-001 carriers.

## Test coverage vs spec 003 §3.5

- Empty/whitespace city → 422 (POST + GET), not passed to use case ✓
- City > 100 chars → 422 (POST + GET) ✓
- `<script>` / injection chars + digits → 422 ✓
- Extra body field → 422 (route + direct model) ✓
- Invalid GET query params → 422 with same rules ✓
- Valid request → exact spec-001 carriers (real repo, no regression) ✓
- Security headers present on responses ✓
- CORS reflects only configured origin; disallowed origin not reflected, never
  `*`; Settings default + env parsing + Singleton identity ✓
- Output `trucks_per_day >= 0` enforced by model (negative raises, zero ok) ✓
- Generic 500 with no traceback / secret leakage ✓
- Valid accented/punctuated names accepted and trimmed ✓

## Verification

### `python -m pytest backend -q`
```
......................................................                   [100%]
54 passed, 1 warning in 0.57s
```

### `./init.sh`
```
==> Genlogs harness init
feature_list.json OK (4 features, 1 in_progress)
==> Running pytest
......................................................                   [100%]
54 passed, 1 warning in 0.59s
==> init OK
```

(The single warning is the pre-existing Starlette/httpx TestClient deprecation
notice — informational, not a failure.)

## Notes for reviewer

- `feature_list.json` feature 4 is `in_progress` (NOT `done` — reviewer's call).
- Only `backend/app/interface/*` + new `settings.py` + tests changed; domain and
  application layers are untouched; spec-001 behavior is unchanged.
- `requirements.txt` unchanged (no new dependency). Environment note from
  `progress/impl_1.md` still applies if a future env hits import errors.
- No frontend / deploy work (out of scope for feature 4).

Reviewer APPROVED (see progress/review_4.md), feature marked done.
