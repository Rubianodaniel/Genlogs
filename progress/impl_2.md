# Implementation report — Feature 2: React single-page portal

- **Feature:** 2 — React single-page portal with Google Maps
- **Spec:** `specs/002-portal-ui.md` (also honored the backend contract in
  `specs/001-carriers-api.md` / `specs/003-backend-validation-security.md` and
  flow-diagram section B).
- **Status:** implemented, awaiting review (NOT marked done).
- **Environment:** Node v22.22.2 / npm 10.9.7 are present → build + tests were
  actually executed and are green.

## Stack (as decided)

React + TypeScript, Vite, Tailwind, `@vis.gl/react-google-maps`, Vitest +
@testing-library/react. No deviations.

## File tree created (`frontend/`)

```
frontend/
├── index.html
├── package.json                 # scripts: dev/build/test; deps incl. @vis.gl/react-google-maps
├── vite.config.ts               # react plugin, '@'->src alias, vitest (jsdom, tests/**)
├── tsconfig.json / tsconfig.app.json / tsconfig.node.json
├── tailwind.config.js / postcss.config.js
├── .env.example                 # VITE_API_BASE_URL, VITE_GOOGLE_MAPS_API_KEY
├── README.md
└── src/
    ├── main.tsx                 # React root
    ├── vite-env.d.ts            # typed import.meta.env
    ├── app/
    │   ├── App.tsx              # APIProvider (maps key from env, libraries places+routes)
    │   └── styles/index.css     # tailwind directives
    ├── pages/portal/
    │   ├── PortalPage.tsx       # composition root: owns the search hook, wires widgets
    │   └── index.ts
    ├── widgets/
    │   ├── route-map/
    │   │   ├── model/useDirections.ts     # Directions alternatives -> 3 fastest
    │   │   ├── ui/RouteMapWidget.tsx       # <Map> + legend
    │   │   ├── ui/RoutePolylines.tsx       # draws up to 3 polylines
    │   │   └── index.ts
    │   └── carrier-list/
    │       ├── ui/CarrierListWidget.tsx    # presentational: idle/loading/error/empty/loaded
    │       └── index.ts
    ├── features/search-corridor/
    │   ├── api/carriersApi.ts   # POST /carriers; CarriersApi interface (DI seam)
    │   ├── model/useSearchCorridor.ts      # business logic + state machine
    │   ├── ui/CityInput.tsx                # Places autocomplete input
    │   ├── ui/SearchPanel.tsx              # From/To + Search button
    │   └── index.ts
    ├── entities/carrier/
    │   ├── model/types.ts       # Carrier type (mirrors backend CarrierOut)
    │   ├── ui/CarrierItem.tsx
    │   └── index.ts
    ├── shared/
    │   ├── api/httpClient.ts    # fetch wrapper + HttpError; only place calling fetch
    │   ├── config/env.ts        # env access (base url normalized, maps key)
    │   └── ui/Spinner.tsx
    └── test/setup.ts            # jest-dom + cleanup/restoreAllMocks
tests/
├── carriersApi.test.ts
├── useSearchCorridor.test.ts
└── CarrierListWidget.test.tsx
```

## Key decisions

- **FSD + unidirectional imports** (`app → pages → widgets → features → entities
  → shared`). The `@/` path alias makes layer imports explicit. Widgets import the
  `Corridor`/`SearchStatus` *types* from the feature's `model/` file (not the
  barrel) so presentational widget tests never transitively pull in the
  Google-Maps UI.
- **No business logic in components.** All search state + orchestration lives in
  `features/search-corridor/model/useSearchCorridor.ts` (explicit state machine
  `idle → loading → loaded | error`). Components are presentational.
- **API calls only in api/shared-api.** `shared/api/httpClient.ts` is the single
  `fetch` site; `features/.../api/carriersApi.ts` owns the `/carriers` contract.
- **Dependency injection.** `carriersApi` is exposed via a `CarriersApi`
  interface and injected into the hook (default = real impl), which is exactly
  the seam the unit test mocks. Same DI spirit as the backend.
- **Env only.** Maps key + backend URL read solely in `shared/config/env.ts`
  from `VITE_*`; `.env.example` provided; base URL trailing slashes normalized.
  `App.tsx` shows a clear "configuration required" message if the key is missing.
- **No hardcoded carriers** anywhere in the UI — always from the backend response.

## Maps + 3 fastest routes — how

- `app/App.tsx` wraps the tree in `APIProvider` (key from env, `libraries:
  ['places','routes']`).
- `CityInput` uses `useMapsLibrary('places')` + `new places.Autocomplete(...)`
  with `types: ['(cities)']`; the selected place name is lifted into the search
  hook. Manual typing also updates state (so search works even without a pick).
- `useDirections` requests `DirectionsService.route({ ...,
  provideRouteAlternatives: true, travelMode: DRIVING })`, sorts the returned
  `routes` by total leg duration and keeps the **top 3 (fastest)**, then
  `map.fitBounds(...)` on the fastest. `RoutePolylines` draws up to 3 polylines
  (fastest highlighted, alternatives lighter); a small legend labels
  Fastest/Alt 1/Alt 2 with durations.
- The corridor is published to state immediately on Search so the map starts
  computing routes in parallel with the backend carriers call (matches flow B).

## Tests (Vitest + Testing Library, unit + mocks only)

- `tests/carriersApi.test.ts` — mocks global `fetch`; asserts URL
  `${base}/carriers`, `POST`, JSON `Content-Type`, exact `{from_city,to_city}`
  body, parsed response; plus `HttpError` on non-2xx and `HttpError(0)` on
  network failure.
- `tests/useSearchCorridor.test.ts` — injects a **mocked** `CarriersApi`; verifies
  idle → loading (corridor published) → loaded (carriers stored, api called with
  correct body), error path clears carriers + sets message, and blank city does
  not call the api.
- `tests/CarrierListWidget.test.tsx` — presentational: renders a given carriers
  array (names + trucks/day) and the loading/error/empty/idle states.
- No real network or Google Maps calls in any test.

## Exact build/test output (executed here)

`npm run build`:
```
tsc -b && vite build
✓ 51 modules transformed.
dist/index.html                   0.40 kB
dist/assets/index-*.css           8.16 kB
dist/assets/index-*.js          188.79 kB
✓ built in ~1.2s
```

`npm test`:
```
✓ tests/carriersApi.test.ts (3 tests)
✓ tests/useSearchCorridor.test.ts (4 tests)
✓ tests/CarrierListWidget.test.tsx (5 tests)
Test Files  3 passed (3)
Tests  12 passed (12)
```

Full `./init.sh`: backend **54 passed** (pytest) + frontend build + **12 passed**
(vitest) → `==> init OK`.

## Harness / housekeeping

- `feature_list.json`: feature 2 set to `in_progress` (left for reviewer to mark
  done).
- `init.sh`: appended a guarded frontend block — runs `npm install` (if needed) +
  `npm run build` + `npm test` only when `command -v npm` and `frontend/` exist;
  otherwise prints a skip line (non-fatal in a Node-less env; backend pytest stays
  the hard gate).
- `.gitignore`: added `dist/` (`node_modules/` and `.env` already ignored). The
  `dist/` build artifact was removed after verification.

## Acceptance criteria (spec 002) — mapped

- City inputs use Google autocomplete → `CityInput` (Places). ✓
- Map embeds + up to 3 alternative routes → `RouteMapWidget` + `useDirections`. ✓
- Carrier list from backend, no hardcoded carriers → `CarrierListWidget` fed by
  the hook from `POST /carriers`. ✓
- Maps key + backend URL from env vars → `shared/config/env.ts`, `.env.example`. ✓

## Scope

Only feature 2 (frontend). No backend logic touched; no deploy.
```

reviewer APPROVED (see progress/review_2.md), feature marked done.
