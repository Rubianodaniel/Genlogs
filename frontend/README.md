# Genlogs Portal — Frontend

React + TypeScript single-page client (Vite, Tailwind,
`@vis.gl/react-google-maps`). Captures origin/destination cities, shows the 3
fastest driving routes on an embedded Google Map, and lists carriers returned by
the backend. Organized with Feature-Sliced Design (see `docs/conventions.md` §3).

## Setup

```bash
cp .env.example .env   # set VITE_API_BASE_URL and VITE_GOOGLE_MAPS_API_KEY
npm install
npm run dev            # http://localhost:5173
```

## Scripts

- `npm run build` — `tsc -b` type-check + `vite build` production bundle.
- `npm test` — Vitest unit tests (run once).
- `npm run test:watch` — Vitest in watch mode.

## Environment

| Var | Purpose |
|-----|---------|
| `VITE_API_BASE_URL` | FastAPI backend base URL (no trailing slash). |
| `VITE_GOOGLE_MAPS_API_KEY` | Google Maps JS key (Maps JS + Places + Directions). |

Never hardcode these — they are read only in `src/shared/config/env.ts`.

## Architecture (FSD, unidirectional imports)

```
app → pages → widgets → features → entities → shared
```

- `shared/api` — fetch wrapper (only place that calls `fetch`).
- `shared/config` — env access.
- `entities/carrier` — `Carrier` type + `CarrierItem`.
- `features/search-corridor` — `api/` (POST /carriers), `model/` (search hook =
  business logic), `ui/` (city inputs + search button).
- `widgets/route-map` — embedded map + 3 fastest routes (Directions alternatives).
- `widgets/carrier-list` — presentational carrier list.
- `pages/portal`, `app/App.tsx` — composition + Maps provider.

## Tests

Unit tests with mocks only (`tests/`): `carriersApi` (mock fetch),
`useSearchCorridor` (mock api via DI), `CarrierListWidget` (presentational). No
real network or Google Maps calls.
