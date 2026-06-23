# Implementation report — Feature 1: Backend carriers endpoint (Clean Architecture refactor)

- **Feature id:** 1
- **Spec:** `specs/001-carriers-api.md`
- **Status:** refactored to Clean Architecture + TDD, all tests passing,
  `./init.sh` green — awaiting review.
- **Behavior:** identical to spec 001. Only structure, testing approach and
  patterns changed; the flat module was removed.

## Layer-by-layer file list

### domain (framework-free core)
- `backend/app/domain/__init__.py`
- `backend/app/domain/entities.py` — `Carrier` and `CityPair` as frozen
  dataclasses. No FastAPI/HTTP knowledge.
- `backend/app/domain/ports.py` — `CarrierRepository` abstract port (ABC with
  `find_by_city_pair`). This is the Dependency Inversion seam.

### application (use cases)
- `backend/app/application/__init__.py`
- `backend/app/application/get_carriers.py` — `GetCarriersUseCase(repository:
  CarrierRepository)` with `.execute(from_city, to_city) -> GetCarriersResult`.
  Depends only on the port. Builds a `CityPair`, delegates to the repo, echoes
  the original (un-normalized) city strings in the result.

### infrastructure (adapters)
- `backend/app/infrastructure/__init__.py`
- `backend/app/infrastructure/in_memory_carrier_repo.py` — `InMemoryCarrierRepo`
  implementing the port. Single source of truth for the verbatim spec data
  (NYC→DC: Knight-Swift 10, J.B. Hunt 7, YRC Worldwide 5; SF→LA: XPO 9,
  Schneider 6, Landstar 2; default: UPS Inc. 11, FedEx Corp 9). Owns the
  alias table + `_normalize_city` (case-insensitive, trimmed, whitespace
  collapsed; NYC/New York/New York City, SF/San Francisco,
  Washington DC/Washington/DC/Washington D.C., LA/Los Angeles). Returns a fresh
  list so callers cannot mutate the shared rule data.

### interface (delivery)
- `backend/app/interface/__init__.py`
- `backend/app/interface/schemas.py` — pydantic DTOs `CarriersRequest`,
  `CarrierOut`, `CarriersResponse` (+ `from_result` mapper).
- `backend/app/interface/deps.py` — composition root. `get_carrier_repository()`
  is a Singleton (`@lru_cache(maxsize=1)`); `get_carriers_use_case()` is the
  Factory that injects the repo into the use case. This is the seam overridden
  in tests.
- `backend/app/interface/api.py` — `APIRouter` with `GET /health`,
  `POST /carriers`, `GET /carriers`. The use case is injected via `Depends`.

### app factory
- `backend/app/main.py` — `create_app()` Factory: builds FastAPI app, adds CORS
  (allow all origins for the demo), mounts the router. Exposes module-level
  `app = create_app()` for `uvicorn app.main:app`.

### removed
- `backend/app/carriers.py` — flat rules module **deleted** (logic moved into
  `infrastructure/in_memory_carrier_repo.py`).
- `backend/tests/test_carriers.py` — old monolithic TestClient suite
  **deleted**; coverage split across the three layered unit test modules below.

## Tests (TDD, pytest, unit-only with mocks + DI)

- `backend/tests/test_get_carriers_use_case.py` — use case in isolation with a
  **mock/fake repository** (hand-written fake + `unittest.mock.MagicMock`). The
  real repo is never used here. Asserts the port is queried with the right
  `CityPair`, called once, and the result echoes the cities.
- `backend/tests/test_in_memory_carrier_repo.py` — repository tested **directly**:
  the 3 rule cases (verbatim names/counts) + alias/casing/whitespace variants
  (parametrized) for rule 1 and rule 2, plus a guard that the returned list is
  not the shared rule object.
- `backend/tests/test_api_router.py` — router tested with `TestClient` and
  `app.dependency_overrides[get_carriers_use_case]` injecting a **fake use
  case** (unit test of the interface layer, not integration through real data):
  POST shape + wiring, GET query params + wiring, 422 on missing field, health,
  and a smoke check that the real composition root builds a `GetCarriersUseCase`.

Coverage spans: 3 rule cases, alias variants, POST and GET, health — as required.

## Patterns applied
- **Repository** — `CarrierRepository` port + `InMemoryCarrierRepo` adapter.
- **Dependency Inversion / DI** — use case depends on the abstract port;
  concrete repo injected via the composition root.
- **Factory** — `create_app()` and `get_carriers_use_case()`.
- **Singleton** — `get_carrier_repository()` via `@lru_cache(maxsize=1)`.

## Verification

### Environment note
Deps were already present in BOTH the system python and the uv `pytest` tool
venv from the prior run, so no reinstall was needed. If a future run hits an
import error, reuse:
- system python: `pip install -r backend/requirements.txt`
- uv pytest tool venv: `VIRTUAL_ENV=/root/.local/share/uv/tools/pytest uv pip install fastapi "uvicorn[standard]" pydantic httpx`

No new dependencies were added; `backend/requirements.txt` and `pytest.ini`
are unchanged.

### `python -m pytest backend -q`
```
..................                                                       [100%]
18 passed, 1 warning in 0.44s
```

### `./init.sh`
```
==> Genlogs harness init
feature_list.json OK (3 features, 1 in_progress)
==> Running pytest
..................                                                       [100%]
18 passed, 1 warning in 0.37s
==> init OK
```

(The single warning is a Starlette deprecation notice about `httpx` in
TestClient — informational only, not a failure.)

## Notes for reviewer
- `feature_list.json` feature 1 remains `in_progress` (not `done` — reviewer's call).
- Flat `app/carriers.py` and old `tests/test_carriers.py` were removed.
- Behavior is unchanged vs spec 001; the response still echoes the original
  city strings the caller sent.
- No frontend or deploy work (out of scope for feature 1).

## Closeout
Reviewer APPROVED (see progress/review_1.md); feature 1 marked `done` in feature_list.json.
