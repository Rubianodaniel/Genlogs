# Verification — how to know the work actually works

A feature is only `done` when all of the below pass.

## Automated

- `./init.sh` finishes with exit code 0.
- Backend: `pytest` is green; the carriers endpoint returns the exact lists in
  `specs/` for each of the three city-pair cases.
- Frontend: the build compiles and unit tests (if present) pass.

## Manual smoke (per feature spec)

- "From New York City to Washington DC" returns Knight-Swift (10), J.B. Hunt (7),
  YRC Worldwide (5).
- "From San Francisco to Los Angeles" returns XPO Logistics (9), Schneider (6),
  Landstar Systems (2).
- Any other city pair returns UPS Inc. (11), FedEx Corp (9).
- The UI shows an embedded Google Map with the 3 fastest routes and the carrier
  list below it.

## Definition of done

- Spec satisfied, tests green, `./init.sh` green, docs/progress updated, repo clean.
