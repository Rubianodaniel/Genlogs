# Spec 001 — Carriers API (FastAPI backend)

## Goal

Expose an HTTP endpoint that, given an origin city and a destination city,
returns the carriers moving the highest volume of trucks between them. No
database: carrier data is in-memory / hardcoded.

## Endpoint

`POST /carriers` (or `GET /carriers?from_city=...&to_city=...`)

### Request

```json
{ "from_city": "New York City", "to_city": "Washington DC" }
```

### Response

```json
{
  "from_city": "New York City",
  "to_city": "Washington DC",
  "carriers": [
    { "name": "Knight-Swift Transport Services", "trucks_per_day": 10 },
    { "name": "J.B. Hunt Transport Services Inc", "trucks_per_day": 7 },
    { "name": "YRC Worldwide", "trucks_per_day": 5 }
  ]
}
```

## Rules (exact data — reproduce verbatim)

1. **New York City → Washington DC**
   - Knight-Swift Transport Services — 10 trucks/day
   - J.B. Hunt Transport Services Inc — 7 trucks/day
   - YRC Worldwide — 5 trucks/day

2. **San Francisco → Los Angeles**
   - XPO Logistics — 9 trucks/day
   - Schneider — 6 trucks/day
   - Landstar Systems — 2 trucks/day

3. **Any other pair** (origin not NYC/SF or destination not Washington DC / LA)
   - UPS Inc. — 11 trucks/day
   - FedEx Corp — 9 trucks/day

## Acceptance criteria

- [ ] The three cases above return exactly the listed carriers and counts.
- [ ] City matching is case-insensitive and tolerant of common variants
      (e.g. "NYC", "New York").
- [ ] CORS is enabled so the React client can call the API.
- [ ] Covered by `pytest` tests, one per case.
