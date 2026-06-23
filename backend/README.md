# Genlogs Carriers API (backend)

FastAPI service that returns the carriers moving the highest volume of trucks
between an origin and a destination city. Carrier data is in-memory / hardcoded
per `specs/001-carriers-api.md`. No database.

## Layout (Clean Architecture — dependencies point inward)

- `app/domain/` — framework-free core: `entities.py` (`Carrier`, `CityPair`),
  `ports.py` (`CarrierRepository` abstract port).
- `app/application/get_carriers.py` — `GetCarriersUseCase` (depends on the port).
- `app/infrastructure/in_memory_carrier_repo.py` — `InMemoryCarrierRepo`: the
  verbatim spec data + alias/normalization (single source of truth).
- `app/interface/` — delivery: `schemas.py` (DTOs), `deps.py` (composition root,
  Factory + Singleton via `lru_cache`), `api.py` (router).
- `app/main.py` — `create_app()` app factory (CORS + router mount).
- `tests/` — unit tests: use case (mock repo), repo direct, router
  (`dependency_overrides`), health.

## Endpoints

- `GET /health` → `{"status": "ok"}`
- `POST /carriers` with body `{"from_city": "...", "to_city": "..."}`
- `GET /carriers?from_city=...&to_city=...`

Response:

```json
{
  "from_city": "New York City",
  "to_city": "Washington DC",
  "carriers": [
    { "name": "Knight-Swift Transport Services", "trucks_per_day": 10 },
    { "name": "J.B. Hunt Transport Services Inc", "trucks_per_day": 7 },
    { "name": "YRC Worldwide", "trucks_per_day": 5 }
  ]
}
```

City matching is case-insensitive and tolerant of common variants
(`NYC`/`New York`/`New York City`, `SF`/`San Francisco`,
`Washington DC`/`Washington`/`DC`, `LA`/`Los Angeles`).

## Run locally

From the `backend/` directory:

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Then open http://localhost:8000/docs for the interactive API docs.

## Run tests

From the `backend/` directory:

```bash
pip install -r requirements.txt
pytest -q
```

Or from the repo root: `python -m pytest backend -q`.
