# {{PROJECT}} — Backlog

Persistent task tracker across agent sessions. Gitignored (lives under
`.private/`). Format:

- **In progress** — the current cycle, with sub-tasks as checkboxes.
- **Closed decisions** — settled questions, one line each and where the detail lives.
- **Next up** — unscoped ideas and deferred items, roughly ordered by priority.
- **Done** — append-only, `YYYY-MM-DD — summary`.

What waits on the owner is not here → `owner-queue.md`.

Deferred items land here the same turn they are deferred → `WORKFLOW.md` §2.6.

---

## In progress

_(The current cycle. One heading, sub-tasks as checkboxes, with who owns each.)_

- [ ] —

---

## Closed decisions (do not re-litigate)

_(An **index**: one line per decision, its reason, and where the detail lives — never
a restatement. It is what stops each new session from reopening what was already
decided.)_

⚠️ **A closed decision can go false with nobody re-litigating it** — the world moves.
In the origin project "we are staying on the free plan — do not ask again" survived
eleven days past the upgrade. If the fact supporting a decision has a canonical home,
the decision **points** at it instead of restating it.

- **Workflow = two-terminal Colossus** ({{PLANNER}} plans / {{IMPLEMENTER}} builds),
  serial, handoff via the baton. ({{TODAY}})
- **Merge stage = {{MERGE_STAGE}}.** Why: {{MERGE_STAGE_WHY}}. Graduation trigger:
  _(the signals the owner confirmed at scaffold time)_. The stages → `CLAUDE.md` →
  "Who merges"; a flip is recorded here with its date and reason. ({{TODAY}})

---

## Next up

_(Unscoped ideas and deferred items, roughly ordered. Each entry: what it is, why
it was deferred, and what would unblock it — a deferred item with no trigger is a
forgotten item.)_

- —

---

## Done

_(Append-only. `YYYY-MM-DD — summary`. How each cycle shipped lives in
`shipped-log.md`; this is just the timeline.)_

- {{TODAY}} — Colossus workflow scaffolded (lanes, subagents, project brain, guardrails).
