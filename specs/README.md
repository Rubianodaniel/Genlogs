# Specs — Spec-Driven Development (SDD)

This folder is the **source of truth** for behavior. Following SDD:

1. A spec is written/updated here **before** any code.
2. Code under `src/` is written to satisfy a spec.
3. Tests under `tests/` verify the spec.
4. The reviewer checks code against the spec.

No feature is implemented without a spec in this folder.

## Index

| Spec file              | Feature                                   |
|------------------------|-------------------------------------------|
| `001-carriers-api.md`  | Backend FastAPI endpoint + carrier rules  |
| `002-portal-ui.md`     | React single-page portal + Google Maps    |
