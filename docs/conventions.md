# Conventions

## General

- All repository files, code, comments and identifiers are written in **English**.
- One feature per commit where practical; commit messages are imperative
  ("Add carriers endpoint", not "Added").

## Backend (FastAPI / Python)

- Python 3.11+, type hints on public functions.
- Use `pydantic` models for request/response bodies.
- Keep the carrier rules in a single, well-named module so the spec mapping is
  obvious and testable.
- Tests with `pytest`, one test module per source module.

## Frontend (React JS)

- Function components and hooks; no class components.
- Keep API calls in a dedicated module/service, not inline in components.
- Environment-specific values (API base URL, Google Maps key) come from env vars,
  never hardcoded.

## Errors

- Backend returns explicit HTTP status codes and a JSON error body.
- Never swallow exceptions silently; fail loud in tests.
