# Spec 002 — Portal UI (React single-page client)

## Stack (decided)

- **React + TypeScript**, built with **Vite**.
- **Tailwind CSS** for styling.
- **@vis.gl/react-google-maps** (official Google library) for the embedded map,
  Places autocomplete, and Directions with alternative routes.
- **Feature-Sliced Design** structure per `docs/conventions.md` §3
  (`app → pages → widgets → features → entities → shared`, unidirectional imports).
- Backend base URL and Google Maps API key via Vite env vars (`VITE_*`).

## Goal

A single-page React client that captures origin/destination cities, shows the 3
fastest driving routes on an embedded Google Map, and lists the carriers returned
by the backend.

## Fields (single page)

1. **From (city)** — text input with Google Maps Places autocomplete.
2. **To (city)** — text input with Google Maps Places autocomplete.
3. **"Search"** button.

## Behavior

- On "Search":
  1. Show an **embedded Google Map** displaying the **3 fastest routes** between
     the two cities (Directions API with alternatives).
  2. Call the backend `/carriers` endpoint with the two cities.
  3. Render the returned carriers as a list (name + trucks/day).

## Acceptance criteria

- [ ] City inputs use Google Maps autocomplete.
- [ ] Map embeds and shows up to 3 alternative routes.
- [ ] Carrier list reflects the backend response (no hardcoded carriers in the UI).
- [ ] Google Maps API key and backend URL come from env vars.
