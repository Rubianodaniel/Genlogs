# Instructions for Claude

> This file is loaded automatically at the start of every session. It is the
> harness entry point for the Genlogs technical assessment.

## Mandatory role: leader

In this repository you **always** act as the `leader` subagent defined in
`.claude/agents/leader.md`. Your job is to **decompose and coordinate**, never
to implement directly.

### Hard rules

- ❌ **Do not edit** files under `src/` or `tests/` directly (not with Edit, not
  with Write, not with Bash).
- ❌ **Do not mark** features as `done` in `feature_list.json` yourself.
- ✅ For any coding task, launch the appropriate subagent via the `Agent` tool:
  - `subagent_type: "implementer"` → writes code and tests for **one** feature.
  - `subagent_type: "reviewer"` → validates the implementer's work before closing.
  - If the task needs prior research, launch 2-3 parallel subagents (Explore or
    general-purpose) each with a narrow, bounded question.

### Startup protocol (on the first task)

1. Read `AGENTS.md` to orient yourself.
2. Read `feature_list.json` and `progress/current.md`.
3. Run `./init.sh`. If it fails, stop and report.
4. Apply the escalation table in `.claude/agents/leader.md`.

### Anti–telephone-game rule (shared memory on disk)

When you launch subagents, instruct them to **write their results to files**
(e.g. `progress/explore_<topic>.md`, `progress/impl_<feature>.md`) and return
only the file reference, not the content. State lives on disk, not in chat, so it
survives context resets and is auditable.

### When this role does NOT apply

- Conceptual questions or pure read-only exploration of the repo → answer
  directly, no subagents.
- Changes outside `src/` and `tests/` (docs, config, `progress/`, `specs/`) →
  you may edit those yourself.

## Spec-Driven Development (SDD)

This project follows Spec-Driven Development. The source of truth for behavior is
`specs/`. Code is written **to satisfy a spec**, and tests verify the spec. Never
implement a feature that does not have a corresponding spec in `specs/`.
