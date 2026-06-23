# Backend — structure & schemas (for explaining the code)

FastAPI service in **Clean Architecture**: dependencies point **inward**
(interface → application → domain ← infrastructure). The domain knows nothing
about FastAPI; the framework lives only at the edge. (See also the request
sequence in `specs/flow-diagram.md`.)

## Module map (what each file does)

```mermaid
flowchart TB
    subgraph interface["interface/ — delivery edge (FastAPI)"]
        main["main.py<br/>create_app() factory<br/>mounts router + CORS"]
        api["api.py<br/>router: GET/POST /carriers, /health"]
        schemas["schemas.py<br/>DTOs: CarriersRequest / CarriersResponse<br/>CityField validation (len, charset, extra=forbid)"]
        deps["deps.py<br/>composition root (DI)<br/>builds UseCase + Repo (lru_cache singleton)"]
        settings["settings.py<br/>Settings singleton<br/>reads CORS_ORIGINS from env"]
    end
    subgraph application["application/ — use cases"]
        uc["get_carriers.py<br/>GetCarriersUseCase.execute(from, to)"]
    end
    subgraph domain["domain/ — framework-free core"]
        ent["entities.py<br/>Carrier, CityPair (frozen)"]
        port["ports.py<br/>CarrierRepository (abstract port)"]
    end
    subgraph infrastructure["infrastructure/ — adapters"]
        repo["in_memory_carrier_repo.py<br/>InMemoryCarrierRepo<br/>spec data + city alias normalization"]
    end

    api --> schemas
    api --> deps
    main --> api
    main --> settings
    deps --> uc
    deps --> repo
    uc --> port
    ent --- port
    repo -. implements .-> port

    classDef edge fill:#e8f0fe,stroke:#4285f4;
    classDef core fill:#e6f4ea,stroke:#34a853;
    class interface,application edge;
    class domain core;
```

## Request flow (POST /carriers)

```mermaid
sequenceDiagram
    participant C as Client (CloudFront origin)
    participant MW as CORS + security middleware
    participant R as Router (api.py)
    participant S as Schemas (Pydantic)
    participant UC as GetCarriersUseCase
    participant RP as InMemoryCarrierRepo

    C->>MW: POST /carriers {from_city,to_city}
    MW->>R: (origin checked against CORS_ORIGINS)
    R->>S: validate body → CarriersRequest
    S-->>R: ok (or 422 on bad input)
    R->>UC: execute(from_city, to_city)
    UC->>RP: find_by_city_pair(CityPair)
    RP->>RP: normalize cities (aliases) + lookup rules
    RP-->>UC: [Carrier...] (or default UPS/FedEx)
    UC-->>R: carriers
    R->>S: serialize → CarriersResponse
    R-->>C: 200 {from_city,to_city,carriers[]}
```

## Why this shape (talking points)

- **Testability / mocking seam:** the use case depends on the **port**
  `CarrierRepository`, not on the concrete repo. Unit tests inject a mock; the
  router test uses FastAPI `dependency_overrides`. No real I/O in tests.
- **Single source of truth for data:** the spec's city-pair → carriers mapping
  lives only in `InMemoryCarrierRepo`. Swapping it for a real DB (the
  `carrier_corridor_volume` read model) needs **no change to the API contract**.
- **Validation & security at the edge:** `schemas.py` enforces input shape
  (length, allowed chars, `extra="forbid"`); `settings.py` drives CORS from
  `CORS_ORIGINS` (no `*`), so the deployed frontend origin is explicit.
- **Patterns used:** Repository (port), Factory + Singleton (`create_app`,
  `lru_cache` in `deps.py`), Dependency Injection (composition root in `deps.py`).
