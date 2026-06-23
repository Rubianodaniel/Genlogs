# Point 2 — Genlogs Platform Architecture

> How I would architect/design the full Genlogs platform: components, and how
> information flows between them. (This is the whole platform, not just the
> point-4 portal simulation.)

## 2.1 Design drivers

- **High write volume**: many highway cameras producing HD images continuously.
- **Heavy async processing**: image → detection → enrichment is a pipeline, not a
  request/response. It must be decoupled and horizontally scalable.
- **External dependency**: the SAFER FMCSA API (rate limits, latency, downtime) —
  must be isolated behind an anti-corruption layer and cached.
- **Read side**: the portal needs fast aggregated reads (carriers per corridor),
  which is a different access pattern than the write/ingest side.

The natural fit is an **event-driven pipeline** for ingest/processing plus a
**read-optimized query side** for the portal (CQRS-style separation).

## 2.2 Components

| # | Component | Responsibility | Tech (suggested) |
|---|-----------|----------------|------------------|
| 1 | **Camera Ingestion Service** | Receives HD images from highway cameras, validates, stores raw image, emits `ImageCaptured` event | API gateway + object storage (S3/GCS) + message bus |
| 2 | **Object Storage** | Stores raw + processed images | S3 / GCS |
| 3 | **Message Bus** | Decouples stages; durable event log | Kafka / SQS+SNS / Pub/Sub |
| 4 | **Vision/Detection Service** | Consumes `ImageCaptured`, runs OCR (license plate, truck ID) + logo detection, emits `DetectionProduced` | Model serving (Triton/SageMaker), GPU workers |
| 5 | **USDOT Resolver** | From detections, identifies USDOT number; emits `UsdotIdentified` | Python service |
| 6 | **SAFER FMCSA Integration (anti-corruption layer)** | Calls SAFER API to enrich USDOT → carrier + vehicle records; caches responses | Python service + cache (Redis) |
| 7 | **Sightings Store (write model)** | Persists enriched sightings (carrier, vehicle, camera, location, timestamp) | PostgreSQL (+ PostGIS) |
| 8 | **Aggregation/Corridor Service** | Aggregates sightings into truck-volume per origin→destination corridor | Batch/stream job → read model |
| 9 | **Read Model / Query DB** | Pre-computed carrier volume per corridor for fast portal reads | PostgreSQL / materialized views |
| 10 | **Portal API (FastAPI)** | Serves the web portal: origin+destination → ranked carriers; routing via Google Maps | FastAPI |
| 11 | **Web Portal (React)** | UI: city inputs (Google autocomplete), map with 3 fastest routes, carrier list | React |
| 12 | **Cross-cutting** | API gateway, authN/Z, observability (logs/metrics/traces), CI/CD | — |

> **Point 4's simulation** is a thin vertical slice of components **10 + 11**, with
> the carrier data hardcoded instead of coming from the read model (8/9).

## 2.3 Information flow

```
[Highway camera]
      │ HD image
      ▼
(1) Camera Ingestion ──► (2) Object Storage (raw image)
      │ ImageCaptured event
      ▼
(3) Message Bus
      │
      ▼
(4) Vision/Detection ── OCR plate + truck ID + logo ──► DetectionProduced
      │
      ▼
(5) USDOT Resolver ── UsdotIdentified ──►
      │
      ▼
(6) SAFER FMCSA Integration ── enrich (carrier + vehicle), cache ──►
      │ enriched sighting
      ▼
(7) Sightings Store (write model, PostGIS)
      │
      ▼
(8) Aggregation/Corridor Service ──► (9) Read Model (carrier volume per corridor)
                                          ▲
                                          │ query: from_city, to_city
(11) React Portal ──► (10) Portal API (FastAPI) ──┘
        ▲                    │
        └── 3 fastest routes (Google Maps Directions) + carrier list ──┘
```

## 2.4 Why this shape

- **Decoupling via the bus**: a spike in captures, or a slow CV model, never blocks
  ingestion or the portal. Each stage scales independently.
- **Anti-corruption layer for SAFER**: external API changes/outages are contained;
  caching absorbs rate limits and repeated USDOT lookups.
- **CQRS split**: the write side (high-volume sightings) and the read side (portal
  queries) evolve and scale separately; the portal reads pre-aggregated data and
  stays fast.
- **Stateless services**: every service is horizontally scalable behind the gateway;
  state lives in storage, the bus, and the databases.

## 2.5 The Aggregation/Corridor Service (component 8) — implementation decision

The aggregation step (sightings → `carrier_corridor_volume`) is designed as a
**separate deployable job/service**, **not** a database trigger. This is a
deliberate choice driven by the write-volume risk.

### Options considered

| Option | What it is | Trade-off |
|--------|-----------|-----------|
| **A — Scheduled batch job** *(chosen)* | A process (cron/Airflow/scheduled container or function) that periodically re-aggregates `sightings` into the read model with an `INSERT ... ON CONFLICT DO UPDATE`. | Simplest; "trucks/day" doesn't need real-time freshness, so hourly/nightly is plenty. |
| **B — Streaming consumer** | A worker subscribed to the message bus that updates corridor counters incrementally per new sighting. | Near-real-time, but always-on and more operationally complex. Only if seconds-level freshness is required. |
| **C — Materialized view** | A Postgres `MATERIALIZED VIEW` with a scheduled `REFRESH`. | Least infra (logic lives in the DB), but less flexible to evolve than a dedicated service. |

### Why NOT a database trigger

A trigger (`AFTER INSERT ON sightings`) was explicitly rejected because of the
**high-write-volume risk**:

1. **Couples the write critical path** — with millions of sightings ingested, a
   trigger fires on every INSERT and would make ingestion wait on aggregation,
   throttling the pipeline.
2. **Breaks the CQRS separation** — the whole point is to decouple writes from
   reads; a trigger re-couples them inside the same transaction.
3. **Operability** — business logic buried in SQL triggers is hard to test,
   version and scale horizontally; a stateless Python service is not.

So aggregation runs **off** the write critical path: it reads `sightings` on its
own schedule and writes `carrier_corridor_volume`, keeping ingestion fast and the
read side independently scalable.

### Scope for this assessment (point 4)

**This service is designed but not deployed.** The point-4 simulation needs no DB
and no aggregation infrastructure: the in-memory repository
(`backend/app/infrastructure/in_memory_carrier_repo.py`) plays the role of
components **8 + 9 collapsed**, returning exactly what a
`SELECT ... FROM carrier_corridor_volume` would. The data shape it exposes matches
the read model 1:1, so it can later be swapped for the real query with **no API
contract change**. In other words, the aggregation service was **reasoned through
against the write-volume risk above**, but only its output (the pre-computed
result) is materialized for the test — the service itself is left as platform
design, not deployed code.
