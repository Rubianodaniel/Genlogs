# Architecture — what "a good job" means here

This is the simulation app required by point 4 of the Genlogs technical test. It
has two layers, kept strictly separated.

## Layers

```
frontend/   React JS single-page client
  └─ captures From (city) and To (city) with Google Maps autocomplete
  └─ on "Search": shows an embedded Google Map with the 3 fastest routes
  └─ renders the carriers list returned by the backend

backend/    FastAPI service
  └─ exposes an endpoint that receives { from_city, to_city }
  └─ returns the carriers for that origin/destination pair
  └─ no database — carrier data is in-memory / hardcoded per the spec
```

## Information flow

1. User types origin and destination in the React client.
2. Client calls the FastAPI endpoint with the two cities.
3. Backend matches the pair against its rules and returns the carrier list.
4. Client renders the embedded map (3 fastest routes) and the carrier list.

## Boundaries (dependencies)

- The frontend never hardcodes carrier data — it always asks the backend.
- The backend never knows about React — it speaks plain JSON.
- No persistence layer. Data lives in code, as the spec allows.

## What "good" looks like

- The carrier rules in `specs/` are reproduced **exactly** (names, trucks/day).
- The map shows the **3 fastest** routes between the two cities.
- Clean separation: swapping the frontend or backend should not require touching
  the other beyond the JSON contract.
