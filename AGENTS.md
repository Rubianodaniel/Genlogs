# AGENTS.md — Navigation map for AI agents

> This file is the **entry point** for any agent working in this repository. It
> is NOT a rulebook bible: it is a **map**. Read only what you need, when you
> need it (progressive disclosure).

---

## 1. Before you start (mandatory)

1. Run `./init.sh` and verify it finishes without errors. If it fails, **stop**
   and fix the environment before touching code.
2. Read `progress/current.md` to understand the state the last session left.
3. Read `feature_list.json` and pick **one** task with status `pending`. Do not
   work on more than one at a time.

## 2. Repository map

| File / folder                  | What it holds                                              | When to read it |
|--------------------------------|-----------------------------------------------------------|-----------------|
| `feature_list.json`            | Task list with status (pending / in_progress / done)      | Always, at start |
| `specs/`                       | Spec-Driven Development specs — the source of truth        | Before implementing anything |
| `progress/current.md`          | Current session state                                     | Always, at start |
| `progress/history.md`          | Append-only log of previous sessions                      | If you need historical context |
| `docs/architecture.md`         | What "doing a good job" means in this project             | Before implementing |
| `docs/conventions.md`          | Style, naming and structure rules                         | Before writing code |
| `docs/verification.md`         | How to verify your work actually works                    | Before declaring a task `done` |
| `CHECKPOINTS.md`               | Objective criteria for "correct final state"              | To self-evaluate |
| `.claude/agents/`              | Subagent definitions (leader, implementer, reviewer)      | If you orchestrate work |
| `scripts/demo_orchestration.py`| Leader-Worker demo with on-disk hand-off                  | To understand the anti–telephone-game rule |
| `src/`                         | Application code                                          | To implement |
| `tests/`                       | Automated tests                                           | To verify |

## 3. Hard rules (non-negotiable)

- **One feature at a time.** Do not mix changes from several tasks in one session.
- **Spec first.** No code without a matching spec in `specs/`.
- **Do not mark a task `done` without green tests.** Run `./init.sh` and make
  sure the test block passes 100%.
- **Document as you go** in `progress/current.md`, not at the end.
- **Leave the repo clean** before closing the session (see §5).
- **If you don't know something, look in `docs/`** before inventing it.

## 4. How to pick a task

```
1. Open feature_list.json
2. Filter by status == "pending"
3. Take the lowest "id"
4. Set its status to "in_progress" and save
5. Note in progress/current.md: feature, start time, brief plan
```

## 5. Session close (lifecycle)

Before you finish:

1. Run `./init.sh` — all green.
2. If the task is finished: set `status: "done"` in `feature_list.json`.
3. Move the `progress/current.md` summary to the end of `progress/history.md`.
4. Empty `progress/current.md`, leaving only the template.
5. Leave no temp files, no debug `print()`, no context-less TODOs.

## 6. If you get blocked

- Re-read the relevant section of `docs/`.
- If a tool doesn't do what you expect, **do not invent a workaround**:
  document the blocker in `progress/current.md` and stop the session.
