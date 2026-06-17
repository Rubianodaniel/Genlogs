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

echo "==> init OK"
