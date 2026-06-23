# Review — feature 1

**Verdict:** APPROVED

Backend carriers endpoint refactored to Clean Architecture. Layering, patterns,
spec data, and unit tests all verified against `specs/001-carriers-api.md`,
`specs/flow-diagram.md` §C, and `docs/conventions.md` §0–§2. `./init.sh` is green
(18 passed, exit 0).

## Checkpoints (backend C1–C6)
- C1: [x] `POST /carriers` exists with `from_city`/`to_city`
  (`backend/app/interface/api.py:26-34`, schema `schemas.py:15-19`). A `GET`
  variant is also provided (`api.py:37-46`) — allowed by the spec.
- C2: [x] NYC → Washington DC returns Knight-Swift (10), J.B. Hunt (7), YRC (5),
  verbatim (`in_memory_carrier_repo.py:45-49`); covered by
  `test_in_memory_carrier_repo.py:24-31`.
- C3: [x] SF → LA returns XPO (9), Schneider (6), Landstar (2), verbatim
  (`in_memory_carrier_repo.py:50-54`); covered by `test_in_memory_carrier_repo.py:34-41`.
- C4: [x] Any other pair returns UPS Inc. (11), FedEx Corp (9)
  (`in_memory_carrier_repo.py:58-61`); covered by `test_in_memory_carrier_repo.py:44-50`.
- C5: [x] `pytest` green for all cases — 18 passed via `./init.sh`.
- C6: [x] CORS enabled (`main.py:21-27`, `allow_origins=["*"]`).

## Detailed review

### 1. Layering / dependencies point inward — PASS
- Domain (`entities.py`, `ports.py`) is framework-free: no FastAPI/HTTP/pydantic
  imports (only the entities docstring *names* FastAPI to say it has no dependency
  on it). `CityPair`/`Carrier` are frozen dataclasses.
- Application (`get_carriers.py:13-14`) imports only domain entities and the
  abstract `CarrierRepository` port — never the concrete repo. Dependency
  Inversion respected.
- Concrete `InMemoryCarrierRepo` is injected only at the composition root
  (`interface/deps.py:28-31`); the use case receives it via constructor DI.

### 2. Patterns present, not forced — PASS
- Factory: `create_app()` (`main.py:15`) and `get_carriers_use_case()`
  (`deps.py:28`).
- Singleton: `get_carrier_repository()` with `@lru_cache(maxsize=1)`
  (`deps.py:17-25`) — one shared in-memory repo/data source.
- Repository: port `CarrierRepository` (`ports.py:15`) + adapter
  `InMemoryCarrierRepo` (`in_memory_carrier_repo.py:64`).

### 3. Carrier data exact + normalization — PASS
- All three rule sets reproduced verbatim (names and trucks/day) — see C2–C4.
- Case-insensitive + alias-tolerant matching: `_normalize_city`
  (`in_memory_carrier_repo.py:67-72`) lowercases, trims, collapses whitespace;
  alias table (`:24-40`) covers NYC/New York/New York City, SF/San Francisco,
  Washington DC/Washington/DC/Washington D.C., LA/Los Angeles. Verified by the
  parametrized alias tests (`test_in_memory_carrier_repo.py:53-88`).

### 4. Genuine UNIT tests with mocks + DI — PASS
- Use case tested in isolation with a hand-written fake AND a
  `MagicMock(spec=CarrierRepository)`; the real repo is never used
  (`test_get_carriers_use_case.py`). Asserts correct `CityPair` and single call.
- Router tested via `app.dependency_overrides[get_carriers_use_case]` injecting a
  fake use case (`test_api_router.py:41-45`). POST shape + wiring, GET query
  params + wiring, 422 on missing field, `/health`, and a composition-root smoke
  test all covered.
- Repo tested directly (3 rules + alias variants + non-shared-list guard).

### 5. Old flat code removed (DRY) — PASS
- `backend/app/carriers.py` and `backend/tests/test_carriers.py` are absent
  (verified on disk). No duplicated rule data; the repo adapter is the single
  source of truth.

### 6. init.sh — PASS
- `./init.sh` exits 0: "18 passed, 1 warning". The single warning is a Starlette
  deprecation about `httpx` in TestClient — informational, not a failure.

## Required changes
None.

## Notes (non-blocking, not gating approval)
- `feature_list.json` feature 1 is still `in_progress` — correct for the
  implementer; leader closes it after this approval.
- `CORS allow_origins=["*"]` with `allow_credentials=True` is fine for the demo
  but should be tightened to the real frontend origin before production deploy
  (feature 3).
