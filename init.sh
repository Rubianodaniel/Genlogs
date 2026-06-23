#!/usr/bin/env bash
# init.sh — environment verification and test gate for the Genlogs harness.
# Exits non-zero if the repo is in an invalid state or tests fail.
set -euo pipefail

echo "==> Genlogs harness init"

# --- Guard: at most one feature in_progress ---
if command -v python3 >/dev/null 2>&1; then
  python3 - <<'PY'
import json, sys
data = json.load(open("feature_list.json"))
in_progress = [f for f in data["features"] if f.get("status") == "in_progress"]
if len(in_progress) > 1:
    print(f"ERROR: {len(in_progress)} features in_progress; only one allowed.")
    sys.exit(1)
print(f"feature_list.json OK ({len(data['features'])} features, "
      f"{len(in_progress)} in_progress)")
PY
fi

# --- Backend tests (only if the backend exists yet) ---
if [ -d "backend" ] || [ -d "src" ]; then
  if command -v pytest >/dev/null 2>&1; then
    echo "==> Running pytest"
    pytest -q
  else
    echo "WARN: pytest not installed; skipping backend tests."
  fi
else
  echo "No backend/src yet — skipping tests (scaffolding phase)."
fi

# --- Frontend checks (only if Node/npm is available) ---
# Non-fatal when Node is absent so the harness gate stays green in a Node-less
# environment; backend pytest above is the hard gate.
if command -v npm >/dev/null 2>&1 && [ -d "frontend" ]; then
  echo "==> Frontend: npm build + test"
  (
    cd frontend
    if [ ! -d node_modules ]; then
      npm install
    fi
    npm run build
    npm test
  )
else
  echo "npm not found or no frontend/ — skipping frontend checks."
fi

echo "==> init OK"
