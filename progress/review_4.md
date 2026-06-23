# Review — feature 4 (Backend input/output validation + security hardening)

**Verdict:** APPROVED

Spec: `specs/003-backend-validation-security.md`. `./init.sh` run by reviewer:
green — **54 passed, 1 warning** (pre-existing Starlette/httpx TestClient
deprecation; informational, not a failure). Prior spec-001 tests still pass
(`backend/tests/test_api_router.py`, incl. the no-regression NYC→DC case).

## Acceptance criteria (spec 003 §3.5)
- [x] Empty / whitespace-only city → 422, not passed to the use case.
      POST `schemas.py:31-39` (`CityField`, `strip_whitespace + min_length=1`),
      GET `api.py:21-23`. Tests `test_validation_security.py:59-70` assert
      `fake_use_case.calls == []` (no unvalidated path).
- [x] City > 100 chars → 422. `max_length=100` (`schemas.py:36`). Tested
      POST `:73-84`, GET `:154`.
- [x] Injection chars (`<`,`>`,`;`,`{`,`}`,`\`,backtick), digits-only and
      digit-containing → 422. Pattern `^[\p{L}\p{M} .,'\-]+$` (`schemas.py:26`).
      Reviewer verified directly: all listed bad inputs raise `ValidationError`;
      accented inputs (`Bogotá`,`Zürich`) pass and are trimmed (pydantic v2 Rust
      regex engine supports `\p{L}`). Tested `:87-109`, `:156`.
- [x] Extra/unexpected body field → 422. `ConfigDict(extra="forbid")` on
      `CarriersRequest` (`schemas.py:48`). Tested `:112-123`, `:349-353`.
- [x] Invalid GET query params → 422 with the same rules. `CityQuery` reuses
      `CityField` (`api.py:21-23`, `:48-50`). Tested `:149-168`.
- [x] Valid requests still return exact spec-001 carriers (no regression).
      `test_valid_request_returns_spec_001_carriers_via_real_repo` (`:327-346`)
      hits the real composition root → Knight-Swift(10), J.B. Hunt(7), YRC(5).
- [x] Security headers on responses: X-Content-Type-Options nosniff,
      X-Frame-Options DENY, Referrer-Policy no-referrer, Cache-Control no-store
      (`main.py:19-24,43-50`). Tested `:247-253`.
- [x] CORS reflects only configured origins, never `*`. `allow_origins` from
      `settings.cors_origins_list` (`main.py:37`), `allow_credentials=False`
      (`:38`) — insecure `*`+credentials combo removed. Methods limited to
      GET/POST/OPTIONS (`:39`). Tested `:292-319` (allowed reflected, disallowed
      not, never `*`). (`allow_headers=["*"]` is fine: spec only forbids the
      origins wildcard + credentials combo.)
- [x] Output validated by `response_model`; `trucks_per_day >= 0`.
      `response_model=CarriersResponse` kept on both routes (`api.py:35,46`);
      `CarrierOut.trucks_per_day: int = Field(..., ge=0)` (`schemas.py:60`);
      all three response models are strict (`extra="forbid"`). Tested `:189-199`.
- [x] All covered by pytest unit tests (mocks + DI via `dependency_overrides`),
      `./init.sh` green. Use case faked through the DI seam
      (`test_validation_security.py:50`); one no-regression test uses the real
      root by design.

Extra spec items:
- [x] Error handling, no leakage: clean 422 `{"detail":[...]}` (FastAPI default,
      tested `:207-215`); generic 500 `{"detail":"Internal server error."}` with
      no traceback / secret (`main.py:52-61`, tested `:218-239`).
- [x] Settings Singleton via `@lru_cache`, env-driven (`CORS_ORIGINS`), no
      hardcoded secrets (`settings.py:31-53`). Default + env parse + Singleton
      identity tested `:256-289`.
- [x] DRY: city constraints defined once (`CityField`) and reused for body and
      query — single source of truth.

## CHECKPOINTS.md (relevant to this feature)
- C1: [x] POST /carriers accepts from_city/to_city (`api.py:35`).
- C5: [x] pytest green (54 passed).
- C6: [x] CORS enabled for the frontend origin (configurable, default
      localhost:5173/3000; spec-001 behavior preserved and hardened).
- C11: [x] `./init.sh` exits 0.
- C14: [x] `feature_list.json` feature 4 = `in_progress` (not self-marked done);
      `progress/` reflects reality; changes confined to interface/config layer.
- C2/C3/C4: [x] Unchanged by this feature; no-regression test confirms C2.
- C7–C10, C13: [ ] Frontend / deploy — out of scope for feature 4.
- C12: [x] Prompts/rules committed (unchanged).

## Architecture / conventions
- Clean Architecture preserved: only `interface/*` + new `interface/settings.py`
  + tests changed; `domain/` and `application/get_carriers.py` untouched
  (verified by `git diff --stat`). DI seam (`deps.py`) intact and used by tests.
- SOLID/DRY/KISS honored: single `CityField` source of truth, no new
  dependency, `os.getenv` instead of pydantic-settings (KISS), patterns
  (Factory/Singleton) used where they fit, not forced.

## Required changes
None.
