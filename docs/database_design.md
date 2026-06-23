# Point 3 — Database Design

> How I would design the database and its tables for the **full** Genlogs
> platform. (The point-4 simulation itself uses no DB; this is the platform design
> the test asks for in point 3.)

## 3.1 Engine choice

**PostgreSQL** with the **PostGIS** extension:
- Relational integrity for carriers/vehicles/sightings.
- Geospatial types/queries (camera locations, corridors) via PostGIS.
- `JSONB` to cache raw SAFER FMCSA payloads without rigid schema coupling.

Write side (ingest/sightings) and read side (portal aggregates) can live in the
same database initially and be split later (CQRS) if volume requires it.

## 3.2 Tables

### Ingest / vision side

```sql
-- Physical cameras along the highways
CREATE TABLE cameras (
    id            BIGSERIAL PRIMARY KEY,
    external_ref  TEXT UNIQUE NOT NULL,          -- vendor/device id
    highway       TEXT NOT NULL,                 -- e.g. "I-95"
    mile_marker   NUMERIC,
    direction     TEXT,                          -- N/S/E/W
    location      GEOGRAPHY(POINT, 4326) NOT NULL,
    status        TEXT NOT NULL DEFAULT 'active',
    installed_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Each captured HD image
CREATE TABLE images (
    id                BIGSERIAL PRIMARY KEY,
    camera_id         BIGINT NOT NULL REFERENCES cameras(id),
    captured_at       TIMESTAMPTZ NOT NULL,
    storage_uri       TEXT NOT NULL,             -- s3://... (raw image)
    width             INT,
    height            INT,
    processing_status TEXT NOT NULL DEFAULT 'pending'  -- pending/processed/failed
);
CREATE INDEX idx_images_camera_time ON images (camera_id, captured_at);

-- Raw detections produced by the vision models
CREATE TABLE detections (
    id          BIGSERIAL PRIMARY KEY,
    image_id    BIGINT NOT NULL REFERENCES images(id),
    kind        TEXT NOT NULL,                   -- 'license_plate' | 'truck_id' | 'logo'
    raw_value   TEXT,                            -- OCR text or logo label
    confidence  REAL,                            -- 0..1
    bbox        JSONB,                           -- bounding box {x,y,w,h}
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);
CREATE INDEX idx_detections_image ON detections (image_id);
```

### Carrier / vehicle reference data (enriched via SAFER FMCSA)

```sql
-- Carriers, keyed by USDOT number (enriched from SAFER FMCSA)
CREATE TABLE carriers (
    id            BIGSERIAL PRIMARY KEY,
    usdot_number  BIGINT UNIQUE NOT NULL,
    legal_name    TEXT,
    dba_name      TEXT,
    state         TEXT,
    safer_synced_at TIMESTAMPTZ
);

-- Vehicles linked to a carrier
CREATE TABLE vehicles (
    id            BIGSERIAL PRIMARY KEY,
    carrier_id    BIGINT REFERENCES carriers(id),
    vin           TEXT,
    plate         TEXT,
    plate_state   TEXT,
    unit_number   TEXT,
    UNIQUE (plate, plate_state)
);

-- Cache of raw SAFER FMCSA responses (anti-corruption + rate-limit absorption)
CREATE TABLE safer_cache (
    usdot_number  BIGINT PRIMARY KEY,
    payload       JSONB NOT NULL,
    fetched_at    TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

### The core fact: sightings

```sql
-- A confirmed sighting of a truck at a camera, enriched with carrier/vehicle
CREATE TABLE sightings (
    id          BIGSERIAL PRIMARY KEY,
    image_id    BIGINT NOT NULL REFERENCES images(id),
    camera_id   BIGINT NOT NULL REFERENCES cameras(id),
    carrier_id  BIGINT REFERENCES carriers(id),
    vehicle_id  BIGINT REFERENCES vehicles(id),
    usdot_number BIGINT,
    seen_at     TIMESTAMPTZ NOT NULL,
    location    GEOGRAPHY(POINT, 4326) NOT NULL
);
CREATE INDEX idx_sightings_carrier_time ON sightings (carrier_id, seen_at);
CREATE INDEX idx_sightings_location ON sightings USING GIST (location);
```

### Read model (powers the portal)

```sql
-- Pre-aggregated carrier volume per origin->destination corridor.
-- Refreshed by the Aggregation/Corridor service (batch or streaming).
CREATE TABLE carrier_corridor_volume (
    id              BIGSERIAL PRIMARY KEY,
    origin_city     TEXT NOT NULL,
    destination_city TEXT NOT NULL,
    carrier_id      BIGINT NOT NULL REFERENCES carriers(id),
    trucks_per_day  NUMERIC NOT NULL,
    window_start    DATE NOT NULL,
    window_end      DATE NOT NULL,
    UNIQUE (origin_city, destination_city, carrier_id, window_start, window_end)
);
CREATE INDEX idx_volume_corridor ON carrier_corridor_volume (origin_city, destination_city, trucks_per_day DESC);
```

## 3.3 How the portal query maps to this schema

The portal's "carriers between city A and B, ranked by trucks/day" becomes:

```sql
SELECT c.legal_name, v.trucks_per_day
FROM carrier_corridor_volume v
JOIN carriers c ON c.id = v.carrier_id
WHERE v.origin_city = :from_city
  AND v.destination_city = :to_city
ORDER BY v.trucks_per_day DESC
LIMIT 10;
```

In the **point-4 simulation** this exact result is hardcoded (no DB), but it maps
1:1 to `carrier_corridor_volume`, so the simulation can later be swapped for a
real query with no API contract change.

## 3.4 Relationships (summary)

```
cameras 1───* images 1───* detections
images  1───* sightings *───1 carriers 1───* vehicles
carriers 1───* carrier_corridor_volume   (read model)
carriers 1───1 safer_cache (by usdot_number)
```

## 3.5 Normalization (normal forms) — how to read this model

The **write/reference side is normalized to 3NF**; the **read side is
deliberately denormalized** for query speed. Rationale per table:

| Table | NF | Why |
|-------|----|-----|
| `cameras` | 3NF | Each attribute depends only on `id`; no repeating groups. |
| `images` | 3NF | `camera_id` is a FK (no camera data copied here). |
| `detections` | 3NF | `bbox` is `JSONB` — a single atomic value (a box), not a repeating group, so 1NF holds. |
| `carriers` | 3NF | `usdot_number` is a candidate key (UNIQUE); carrier attributes depend on it, not on each other. |
| `vehicles` | 3NF | Vehicle attributes depend on the vehicle; `carrier_id` is a FK. |
| `sightings` | 3NF (fact) | Only FKs + event attributes (`seen_at`, `location`). `usdot_number` is kept denormalized-on-purpose as an immutable snapshot of what was read at sighting time. |
| `safer_cache` | 1NF | Intentional raw `JSONB` payload — a cache, outside the normalized core (anti-corruption boundary). |
| `carrier_corridor_volume` | **denormalized (read model)** | Pre-aggregated for the portal. Duplicates city strings on purpose to answer the query with no joins/aggregation at request time (CQRS read side). |

### The normal forms, applied here

- **1NF** — atomic columns, no repeating groups. We avoid columns like
  `carrier1, carrier2, carrier3`; instead each carrier→corridor pair is its own
  row in `carrier_corridor_volume`.
- **2NF** — no partial dependency on part of a composite key. Our PKs are single
  surrogate `id`s, and the natural composite (origin, destination, carrier,
  window) is a UNIQUE constraint, with every non-key attribute depending on the
  **whole** key.
- **3NF** — no transitive dependencies. Carrier details live **only** in
  `carriers`; `sightings`/`volume` reference it by FK instead of copying
  `legal_name`, etc. (the one intentional exception is the immutable
  `usdot_number` snapshot in `sightings`).

### Why denormalize the read model

The portal asks "top carriers between A and B" constantly. Computing that by
joining `sightings → carriers` and aggregating per request would be expensive.
The Aggregation service pre-computes it into `carrier_corridor_volume` (a
controlled, refreshable duplication). This is the classic **normalized writes /
denormalized reads** trade-off (CQRS).

> **How that aggregation runs (and why it's not a DB trigger)** is documented in
> `docs/platform_architecture.md` §2.5: it is a **separate scheduled job/service**,
> kept off the write critical path because of the high sightings write volume — a
> trigger would couple ingestion to aggregation and break the CQRS split. For this
> assessment the service is **designed but not deployed**; the in-memory repository
> materializes its output instead.

> In the **point-4 simulation** there is no DB at all: the in-memory repository
> returns exactly what a `SELECT ... FROM carrier_corridor_volume` would, so the
> data shape the API exposes already matches this model 1:1.
