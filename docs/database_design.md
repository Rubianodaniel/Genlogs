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
