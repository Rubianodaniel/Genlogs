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
