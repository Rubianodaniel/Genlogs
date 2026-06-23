# Prompts & rules used to build this solution

> Point 4d of the test: "Push the prompts and the rules used to the repository."
> This file documents **how the solution was prompted** and points to the actual
> prompt/rule artifacts committed in the repo.

This project was built with an **AI-agent harness**: a `leader` decomposes the
work and delegates to `implementer` and `reviewer` subagents, with all state kept
on disk (Spec-Driven Development). The "prompts" therefore live at two levels:
the **standing system prompts** (committed, below) and the **per-task prompts**
(representative examples below).

## 1. Standing prompts & rules (committed artifacts)

These files ARE the operational prompts/rules the agents run under:

| File                            | Role                                                                                                                                                                      |
| ------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `CLAUDE.md`                     | Harness entry prompt — mandates the `leader` role, the hard rules (never edit `src/`/`tests/` directly, never self-mark `done`), the on-disk shared-memory rule, and SDD. |
| `AGENTS.md`                     | Navigation map / operating rules for any agent: startup protocol, repo map, one-feature-at-a-time, session lifecycle.                                                     |
| `.claude/agents/leader.md`      | System prompt for the **leader** (orchestrator/decomposer).                                                                                                               |
| `.claude/agents/implementer.md` | System prompt for the **implementer** (writes code+tests for one feature).                                                                                                |
| `.claude/agents/reviewer.md`    | System prompt for the **reviewer** (validates against spec/docs, never edits).                                                                                            |
| `docs/conventions.md`           | Engineering rules the prompts enforce (Clean Arch, TDD, DI/mocks, SOLID, FSD).                                                                                            |
| `docs/architecture.md`          | What "a good job" means here — quality bar referenced by prompts.                                                                                                         |
| `specs/*.md`                    | The spec each feature was prompted to satisfy (SDD source of truth).                                                                                                      |

## 2. Prompting method (the pattern every feature followed)

1. **Spec first.** Write/confirm a spec in `specs/` before any code.
2. **Leader decomposes.** Picks one `pending` feature, sets it `in_progress`,
   writes a short plan into `progress/current.md`.
3. **Delegate to implementer** with a bounded prompt: the spec, the conventions,
   "one feature only", "write tests", "report to a `progress/impl_*.md` file and
   return only the reference" (anti–telephone-game).
4. **Delegate to reviewer** with a prompt to check the work against the spec +
   `docs/` + `CHECKPOINTS.md`, and emit APPROVED/REJECTED to `progress/review_*.md`.
5. **Close** only on green tests + reviewer approval; update `progress/`.

## 3. Representative task prompts (by feature)

> Reconstructed to match the prompts actually used; the exact wording varied, but
> the structure and constraints are faithful to how each was delegated.

**Feature 1 — backend (spec 001):**

> "As implementer: build the FastAPI carriers endpoint to satisfy `specs/001-carriers-api.md`,
> in Clean Architecture (domain/application/infrastructure/interface), TDD with the
> repository behind a port so the use case is unit-testable with a mock. Hardcode
> the three city-pair cases verbatim from the spec. Write tests; report to
> `progress/impl_1.md`."

**Feature 4 — validation/security (spec 003):**

> "As implementer: add strict Pydantic validation (length, charset, `extra=forbid`)
> and security hardening to satisfy `specs/003-...`; drive CORS from a `CORS_ORIGINS`
> env var (no `*`); no domain changes; TDD; report to a progress file."

**Feature 2 — frontend (spec 002):**

> "As implementer: build the React+TS single-page portal per `specs/002-portal-ui.md`
> using Feature-Sliced Design — From/To inputs with Google Maps autocomplete, a
> Search button, an embedded map with the 3 fastest routes, and the carrier list
> from the backend. Business logic in a hook, fetch only in shared/api, tests with
> mocks only."

**Feature 3 — deploy (spec 004):**

> "As implementer: produce the deploy artifacts to satisfy `specs/004-deploy.md` —
> backend Dockerfile for App Runner (non-root, `$PORT`), frontend S3+CloudFront
> deploy docs/scripts (SPA 403/404 → index.html). Don't run the real AWS apply."

**Conceptual deliverables (points 2 & 3):** the platform architecture and DB
design were prompted as design docs (`docs/platform_architecture.md`,
`docs/database_design.md`) — components/data flow and a PostgreSQL+PostGIS schema
with a CQRS read model.
