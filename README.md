# Genlogs — Technical Assessment

Simulation of the Genlogs portal: given an origin and destination city, show the
3 fastest routes on a map and the carriers moving the most trucks between them.

This repository is organized as an **AI agent harness** that combines three
techniques:

1. **Shared memory on disk** — session state, plans and subagent reports live in
   `progress/` (version-controlled files), not in chat. This is the
   anti–telephone-game rule; see `scripts/demo_orchestration.py`.
2. **Subagents orchestration** — a `leader` decomposes work and coordinates an
   `implementer` and a `reviewer` (see `.claude/agents/`). Workers write reports
   to disk and return only references.
3. **Spec-Driven Development (SDD)** — `specs/` is the source of truth; code is
   written to satisfy a spec and tests verify it.

## Start here

| If you are…           | Read…                          |
|-----------------------|--------------------------------|
| An AI agent           | `CLAUDE.md`, then `AGENTS.md`   |
| A human reviewer      | `specs/`, then `CHECKPOINTS.md` |
| Setting up            | run `./init.sh`                 |

## Layout

```
.claude/agents/   leader / implementer / reviewer definitions
specs/            Spec-Driven Development specs (source of truth)
progress/         shared memory: current.md, history.md, subagent reports
docs/             architecture, conventions, verification
scripts/          demo_orchestration.py (on-disk hand-off pattern)
feature_list.json one-feature-at-a-time work queue
CHECKPOINTS.md    objective "correct final state" criteria
init.sh           environment + test gate
```

## The test

The full parsed assessment requirements are in `docs/requirements.md`.
