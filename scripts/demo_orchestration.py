#!/usr/bin/env python3
"""Demo of the Leader-Worker pattern with on-disk hand-off.

This illustrates the harness's anti-telephone-game rule: workers do NOT return
their results through the conversation. They WRITE results to files under
progress/ and return only a lightweight reference. The leader then reads the
file. State lives on disk (shared memory), so it survives context resets and is
auditable.

Run: python scripts/demo_orchestration.py
"""
from __future__ import annotations

from pathlib import Path

PROGRESS = Path(__file__).resolve().parent.parent / "progress"


def worker(feature_id: str, finding: str) -> str:
    """A subagent: writes its full output to disk, returns only a reference."""
    PROGRESS.mkdir(exist_ok=True)
    report = PROGRESS / f"impl_{feature_id}.md"
    report.write_text(
        f"# Implementation report — feature {feature_id}\n\n{finding}\n",
        encoding="utf-8",
    )
    return f"see {report.relative_to(PROGRESS.parent)}"  # lightweight reference


def leader() -> None:
    """The leader launches workers and only handles references, never payloads."""
    refs = [
        worker("demo-1", "Touched src/api.py; added /carriers; 3 tests green."),
        worker("demo-2", "Touched frontend/App.jsx; added map + carrier list."),
    ]
    print("Leader received references (not content):")
    for r in refs:
        print(f"  - {r}")
    print("\nLeader now reads each file from disk to learn what happened.")


if __name__ == "__main__":
    leader()
