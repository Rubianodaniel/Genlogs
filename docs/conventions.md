# Conventions

> Engineering standards for this project. The `implementer` and `reviewer`
> subagents MUST follow these. These encode the team's preferences.

## 0. Global principles (apply everywhere)

- **SOLID** — single responsibility, open/closed, Liskov, interface segregation,
  dependency inversion.
- **DRY** — no duplicated knowledge; one source of truth per rule.
- **KISS** — prefer the simplest design that satisfies the spec. Patterns serve
  the code, not the other way around.
- **Dependency Injection** — dependencies are passed in (constructor/params/FastAPI
  `Depends`), never hardcoded or imported deep inside. This is what makes unit
  tests mockable.
- All files, code, comments and identifiers in **English**.

## 1. Backend — Clean Architecture (FastAPI / Python)

Layered, dependencies point **inward** (outer depends on inner, never the reverse):

```
backend/app/
├── domain/          # Entities + business rules. Pure Python, no framework.
│   ├── entities.py        # Carrier, CityPair (dataclasses / pydantic)
│   └── ports.py           # Abstract interfaces (Protocol/ABC): repositories
├── application/     # Use cases. Orchestrates domain via ports. No FastAPI here.
│   └── get_carriers.py     # GetCarriersUseCase(repo: CarrierRepository)
├── infrastructure/  # Adapters that implement the ports.
│   └── in_memory_carrier_repo.py   # implements CarrierRepository (hardcoded data)
├── interface/       # Delivery layer: FastAPI routers, schemas, DI wiring.
│   ├── api.py              # routes; calls use cases
│   ├── schemas.py          # pydantic request/response DTOs
│   └── deps.py             # FastAPI Depends() providers (composition root)
└── main.py          # app factory: create_app(), CORS, router mounting
```

Rules:
- **Domain** knows nothing about FastAPI, HTTP or the DB.
- **Use cases** depend on **ports** (abstract interfaces), not concrete classes →
  Dependency Inversion. Concrete repos are injected.
- **Interface layer** wires concrete implementations via FastAPI `Depends`
  (composition root). This is the seam we mock in tests.

### Design patterns to use (where they fit, not forced)

- **Factory** — `create_app()` app factory; factories for building use cases /
  repositories so wiring is centralized and swappable.
- **Singleton** — the in-memory data source / settings exposed as a single shared
  instance (e.g. via `@lru_cache` provider) so there's one source of truth.
- **Repository (port + adapter)** — abstract `CarrierRepository` port; in-memory
  adapter now, swappable for a real DB later without touching use cases.

## 2. Tests — TDD, pytest, unit-only with mocks + DI

- **TDD**: write the failing test first, then the code to make it pass, then
  refactor (red → green → refactor).
- **pytest** only.
- **Unit tests only** (this project): test each unit in isolation. **Mock
  collaborators** using dependency injection — inject fakes/mocks of the ports
  (e.g. a fake `CarrierRepository`) instead of hitting real implementations.
- Use `unittest.mock` / `pytest` fixtures to provide the injected doubles.
- One test module per unit; arrange-act-assert; descriptive test names.
- The use case is tested with a **mock repository**; the router is tested with the
  use case **overridden via FastAPI dependency_overrides**.

## 3. Frontend — modular & independent (React, Feature-Sliced Design)

Architecture: **Feature-Sliced Design (FSD)** — modular, feature-independent,
unidirectional dependencies (a layer imports only from layers below it).

```
frontend/src/
├── app/         # app setup: providers, router, global styles
├── pages/       # route-level composition (the single portal page)
├── widgets/     # composite UI blocks (e.g. RouteMapWidget, CarrierListWidget)
├── features/    # user-facing features (e.g. search-corridor)
│   └── search-corridor/
│       ├── ui/        # components
│       ├── model/     # state/hooks (business logic)
│       ├── api/       # backend calls
│       └── lib/       # local helpers
├── entities/    # business entities (Carrier, Corridor) + their UI/model
└── shared/      # reusable, feature-agnostic: ui kit, api client, config, lib
```

Rules:
- **Unidirectional imports**: `app → pages → widgets → features → entities → shared`.
  Never import upward; no circular deps.
- Each slice keeps **UI, model (logic), api and lib together** (high cohesion).
- **No business logic in components** — it lives in `model/` hooks.
- **API calls only in `api/` segments** (or `shared/api` client), never inline.
- Config (API base URL, Google Maps key) from **env vars**, never hardcoded.
- Function components + hooks only.

> References (modular frontend, reviewed online): Feature-Sliced Design and
> feature-driven/clean React folder structures —
> https://feature-sliced.design/blog/scalable-react-architecture ,
> https://martinfowler.com/articles/modularizing-react-apps.html ,
> https://dev.to/usapopopooon/a-gradual-approach-to-react-folder-structure-from-package-by-feature-to-clean-architecture-e44

## 4. Errors

- Backend returns explicit HTTP status codes and a JSON error body.
- Never swallow exceptions silently; tests fail loud.
