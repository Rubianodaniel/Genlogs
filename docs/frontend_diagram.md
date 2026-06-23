# Frontend — structure & schemas (for explaining the code)

React + TypeScript SPA organized with **Feature-Sliced Design (FSD)**. Imports
flow **one way, downward only**:

`app → pages → widgets → features → entities → shared`

A layer may only import from layers below it. This keeps business logic isolated
and the UI composable.

## Layer / module map (what each slice does)

```mermaid
flowchart TB
    subgraph app["app/ — composition root"]
        A["App.tsx<br/>APIProvider (Google Maps loader)"]
        M["main.tsx — React root"]
    end
    subgraph pages["pages/"]
        P["portal/PortalPage.tsx<br/>composes SearchPanel + widgets"]
    end
    subgraph widgets["widgets/ — self-contained UI blocks"]
        RM["route-map/<br/>RouteMapWidget + RoutePolylines<br/>useDirections (3 fastest routes)"]
        CL["carrier-list/<br/>CarrierListWidget (presentational)"]
    end
    subgraph features["features/ — user-facing business logic"]
        SC["search-corridor/<br/>api/carriersApi (POST /carriers)<br/>model/useSearchCorridor (state machine)<br/>ui/CityInput + SearchPanel"]
    end
    subgraph entities["entities/ — domain models"]
        CA["carrier/<br/>model/types (Carrier)<br/>ui/CarrierItem"]
    end
    subgraph shared["shared/ — reusable, no business logic"]
        H["api/httpClient (only place that fetch()es)"]
        E["config/env (VITE_API_BASE_URL, VITE_GOOGLE_MAPS_API_KEY)"]
        SP["ui/Spinner"]
    end

    A --> P
    P --> RM
    P --> SC
    P --> CL
    SC --> CA
    SC --> H
    CL --> CA
    H --> E

    classDef l fill:#e8f0fe,stroke:#4285f4;
    class app,pages,widgets,features,entities,shared l;
```

## Runtime data flow (a search)

```mermaid
sequenceDiagram
    actor U as User
    participant SP as SearchPanel (feature ui)
    participant H as useSearchCorridor (feature model)
    participant API as carriersApi (feature api)
    participant BE as Backend (FastAPI)
    participant RM as RouteMapWidget
    participant GM as Google Maps Directions
    participant CL as CarrierListWidget

    U->>SP: type From/To (Places autocomplete) + Search
    SP->>H: search(from, to)
    H->>API: POST /carriers (via shared httpClient)
    API->>BE: {from_city, to_city}
    BE-->>API: {carriers[]}
    API-->>H: Carrier[]
    H-->>CL: carriers → render list
    SP->>RM: from/to
    RM->>GM: request alternatives
    GM-->>RM: routes → draw 3 fastest (RoutePolylines)
    Note over H: state machine: idle → loading → loaded / error
```

## Why this shape (talking points)

- **Separation of concerns:** business logic (the search state machine) lives in
  `features/search-corridor/model`, UI is dumb/presentational, and the **only**
  place that performs `fetch` is `shared/api/httpClient`.
- **Testability:** `useSearchCorridor` takes the api via dependency injection, so
  unit tests pass a mock api; `CarrierListWidget` is purely presentational; tests
  use mocks only — no real network or Google Maps calls.
- **Config isolation:** environment access is centralized in `shared/config/env`;
  Vite inlines `VITE_*` vars at build time (that's how the deployed bundle knows
  the App Runner backend URL and the Maps key).
- **Widgets are swappable:** `route-map` and `carrier-list` are independent blocks
  the page composes; neither knows about the other.
