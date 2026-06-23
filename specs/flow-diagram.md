# Flow Diagrams (review these first)

> Added to `specs/` as agreed: see the flow before implementing, so it's clear
> what to review. Rendered with Mermaid (GitHub renders these natively).

## A. Platform data flow (point 2 — the full Genlogs platform)

```mermaid
flowchart TD
    CAM[Highway camera<br/>HD image] --> ING[1. Ingestion Service]
    ING --> OBJ[(2. Object Storage<br/>raw images)]
    ING -->|ImageCaptured| BUS{{3. Message Bus}}
    BUS --> CV[4. Vision/Detection<br/>OCR plate + truck id + logo]
    CV -->|DetectionProduced| USD[5. USDOT Resolver]
    USD -->|UsdotIdentified| SAFER[6. SAFER FMCSA<br/>anti-corruption + cache]
    SAFER --> SIGHT[(7. Sightings Store<br/>PostgreSQL + PostGIS)]
    SIGHT --> AGG[8. Aggregation / Corridor]
    AGG --> READ[(9. Read Model<br/>carrier volume per corridor)]
    READ --> API[10. Portal API<br/>FastAPI]
    API --> UI[11. React Portal]
    UI -->|from_city, to_city| API
```

## B. Simulation request flow (point 4 — what we are building now)

```mermaid
sequenceDiagram
    actor User
    participant UI as React Portal (FSD)
    participant GM as Google Maps
    participant API as FastAPI (Clean Arch)
    participant UC as GetCarriers UseCase
    participant REPO as CarrierRepository (in-memory)

    User->>UI: type From / To (Maps autocomplete)
    User->>UI: click "Search"
    UI->>GM: Directions (alternatives) → 3 fastest routes
    GM-->>UI: routes
    UI->>API: POST /carriers {from_city, to_city}
    API->>UC: execute(from, to)  (DI: repo injected)
    UC->>REPO: find(city_pair)
    REPO-->>UC: carriers
    UC-->>API: carriers
    API-->>UI: {from, to, carriers[]}
    UI-->>User: embedded map (3 routes) + carrier list
```

## C. Backend Clean Architecture layers (dependencies point inward)

```mermaid
flowchart LR
    subgraph Interface[interface — FastAPI]
        R[router + schemas + deps]
    end
    subgraph Application[application]
        U[GetCarriersUseCase]
    end
    subgraph Domain[domain]
        E[Entities: Carrier, CityPair]
        P[Port: CarrierRepository]
    end
    subgraph Infra[infrastructure]
        A[InMemoryCarrierRepo]
    end

    R --> U
    U --> P
    E --- P
    A -. implements .-> P
    R -. injects .-> A
```

> Mocking seam for unit tests: the use case depends on the **port** `CarrierRepository`.
> Tests inject a **mock repo**; the router test uses FastAPI `dependency_overrides`.
