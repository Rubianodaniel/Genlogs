# Checkpoints — correct final state

Objective, checkable criteria. The reviewer marks each `[x]` or `[ ]`.

## Backend (spec 001)

- C1: `POST /carriers` exists and accepts `from_city` / `to_city`.
- C2: NYC → Washington DC returns Knight-Swift (10), J.B. Hunt (7), YRC (5).
- C3: SF → LA returns XPO (9), Schneider (6), Landstar (2).
- C4: Any other pair returns UPS Inc. (11), FedEx Corp (9).
- C5: `pytest` is green for all three cases.
- C6: CORS enabled for the frontend origin.

## Frontend (spec 002)

- C7: Single page with From, To and a Search button.
- C8: City inputs use Google Maps autocomplete.
- C9: Embedded map shows the 3 fastest routes.
- C10: Carrier list comes from the backend, not hardcoded in the UI.

## Project / process

- C11: `./init.sh` exits 0.
- C12: Prompts and rules used are committed to the repo.
- C13: Both apps are deployed and the URLs are shared.
- C14: Repo is clean; `progress/` and `feature_list.json` reflect reality.
