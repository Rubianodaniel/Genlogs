# Review — feature 2 (React single-page portal)

**Verdict:** APPROVED

Reviewed against `specs/002-portal-ui.md`, `docs/conventions.md` §0/§3,
`specs/flow-diagram.md` §B, and the implementer report `progress/impl_2.md`.
`npm`/`node` ARE present (node v22.22.2), so the full gate was actually run.

## Gate (./init.sh) — PASS, exits 0
- `feature_list.json OK (4 features, 1 in_progress)`.
- Backend: `54 passed` (pytest) — backend hard gate still green.
- Frontend: `tsc -b && vite build` succeeded (51 modules); `vitest run` →
  `Test Files 3 passed (3)`, `Tests 12 passed (12)`.
- `==> init OK`. Frontend block is correctly guarded by
  `command -v npm && [ -d frontend ]` (non-fatal when npm absent), backend pytest
  remains the hard gate.

## Stack — matches the decided stack
- React 18 + TypeScript, Vite 5, Tailwind 3, `@vis.gl/react-google-maps ^1.5.0`,
  Vitest 2 + @testing-library/react (`frontend/package.json`). No deviations.

## FSD structure & dependency direction — clean
- Layers present: `app, pages, widgets, features, entities, shared`
  (`frontend/src/`). Each slice keeps ui/model/api together
  (e.g. `features/search-corridor/{api,model,ui}`).
- Dependency direction verified by grep: NO upward imports and no cycles.
  - `features/*` does not import from app/pages/widgets.
  - `entities/*` does not import from app/pages/widgets/features.
  - `shared/*` imports from nothing above it.
  - `widgets/*` does not import from app/pages; it imports the `Corridor`/
    `SearchStatus` *types* from `features/search-corridor/model/...` — downward,
    allowed.

## Business logic & isolation — compliant
- All search state/orchestration is in the hook
  `features/search-corridor/model/useSearchCorridor.ts` (explicit state machine
  idle→loading→loaded|error); components are presentational.
- Route computation is in the hook `widgets/route-map/model/useDirections.ts`,
  not in the component.
- `fetch` appears ONLY in `shared/api/httpClient.ts:27`; `import.meta.env`
  appears ONLY in `shared/config/env.ts:14`. No inline API calls or env reads
  in components.

## Behavior per spec 002 — satisfied
- Single page (`pages/portal/PortalPage.tsx`) with From/To inputs + Search
  button (`features/search-corridor/ui/SearchPanel.tsx`).
- City inputs use Google Places autocomplete via `useMapsLibrary('places')` +
  `new places.Autocomplete(..., { types: ['(cities)'] })`
  (`features/search-corridor/ui/CityInput.tsx`).
- On Search the corridor is published immediately and the map runs
  `DirectionsService.route({ provideRouteAlternatives: true, travelMode:
  DRIVING })`, sorts by total duration and keeps the top 3 fastest
  (`widgets/route-map/model/useDirections.ts`), drawn as polylines
  (`RoutePolylines.tsx`) on an embedded `<Map>` (`RouteMapWidget.tsx`).
- In parallel `POST /carriers` is called and the result is rendered by
  `widgets/carrier-list/ui/CarrierListWidget.tsx`. This matches flow §B.
- Loading/error/idle/empty states exist in both the carrier widget and the map
  widget; the Search button disables while loading.

## No hardcoded carriers / env-driven config — compliant
- Carriers come solely from the backend response; no carrier literals in any
  `src/` component (test fixtures only, which is correct).
- `VITE_GOOGLE_MAPS_API_KEY` and `VITE_API_BASE_URL` read only in
  `shared/config/env.ts`; `frontend/.env.example` present with placeholders.
- No secrets committed: `.env`, `node_modules/`, `dist/` are gitignored
  (verified via `git status --ignored`). `App.tsx` shows a clear
  "configuration required" message when the key is missing.

## Contract types match the backend
- Request `{from_city, to_city}` and response `{from_city, to_city,
  carriers:[{name, trucks_per_day}]}` in
  `features/search-corridor/api/carriersApi.ts` +
  `entities/carrier/model/types.ts` match backend `schemas.py`
  (`CarriersRequest`, `CarriersResponse`, `CarrierOut`) exactly. Endpoint path
  `/carriers` matches the router. CORS default allows `localhost:5173`.

## Tests — genuine unit tests with mocks (no real network/Maps)
- `tests/carriersApi.test.ts` — mocks global `fetch`; asserts URL
  `${base}/carriers`, POST, JSON content-type, exact `{from_city,to_city}` body,
  parsed response; `HttpError` on non-2xx and `HttpError(0)` on network failure.
- `tests/useSearchCorridor.test.ts` — injects a mocked `CarriersApi`; verifies
  idle→loading (corridor published)→loaded, error clears carriers, blank city
  short-circuits (no api call).
- `tests/CarrierListWidget.test.tsx` — presentational: loaded/loading/error/
  empty/idle. No real network or Maps in any test.

## Checkpoints
- C7 (single page From/To + Search): [x] — `SearchPanel.tsx` + `PortalPage.tsx`.
- C8 (Google autocomplete inputs): [x] — `CityInput.tsx` Places autocomplete.
- C9 (embedded map, 3 fastest routes): [x] — `useDirections.ts` (alternatives,
  sort, slice 3) + `RouteMapWidget.tsx`/`RoutePolylines.tsx`.
- C10 (carriers from backend, not hardcoded): [x] — `carriersApi` → hook →
  `CarrierListWidget`; no UI carrier literals.
- C11 (./init.sh exits 0): [x] — ran green (backend 54, frontend build + 12).
- C14 (repo clean; progress + feature_list reflect reality): [x] — feature 2 left
  `in_progress` for the leader to close; `progress/impl_2.md` + `current.md`
  accurate; build artifacts gitignored.

Spec-002 acceptance criteria: all four met (autocomplete, map+3 routes, backend
carriers, env vars).

## Non-blocking observations (optional polish, not required)
1. `tsconfig.app.json` `include` is `["src"]`, so `tests/` are not type-checked
   by `tsc -b` at build time (Vitest still runs them green). Optional: add a test
   tsconfig if you want type errors in tests to fail the build.
2. Minor DRY: the route color palette is duplicated between `RouteMapWidget.tsx`
   (legend) and `RoutePolylines.tsx`. Could share one constant.
3. `tsconfig.app.tsbuildinfo` / `tsconfig.node.tsbuildinfo` are incremental build
   artifacts; consider gitignoring them. (Currently inside the untracked
   `frontend/` tree, so not actually committed yet.)

None of the above affect correctness, the spec, conventions, or the gate.

## Required changes
None.
