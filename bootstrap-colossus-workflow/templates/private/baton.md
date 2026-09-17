# Baton — handoff channel {{PLANNER}} ↔ {{IMPLEMENTER}}

> **A channel in flight, not an archive and not a manual.** Current state + next
> step + who acts next, plus {{IMPLEMENTER}}'s feedback for {{PLANNER}}.
>
> 🔴 **Who prunes, when, and what leaves** → `WORKFLOW.md` §2.4. {{IMPLEMENTER}} never
> prunes; nothing leaves until it has been read.
>
> **Fields:** `to:` who takes control (`{{planner-slug}}` | `{{implementer-slug}}` |
> `user`) · `level:` the task's level when one is handed over · `stop_reason:` the
> state it stopped in · `next:` the next concrete step.
>
> ⛔ **The protocol is not restated here.** Lanes, task levels, signals and who merges
> live in `CLAUDE.md` and `.claude/lanes/<role>.md`; the rules of how we work, in
> `WORKFLOW.md`. What waits on the owner does not go here: `operations/owner-queue.md`.

---

to: {{planner-slug}}
level: —
stop_reason: Workflow scaffolded. Nothing in flight.
next: First planning round — define the first cycle and write it into `operations/backlog.md`.

## Pointers

- The spec of the task in flight → `engineering/<task>.md` or `product/<task>.md` (none yet).
- What waits on the owner → `operations/owner-queue.md`. Never here.

---
