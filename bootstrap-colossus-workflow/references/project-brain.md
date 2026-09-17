# The project brain — `.private/`

A gitignored folder that holds everything the repo itself cannot record: intent,
strategy, what is actually live, what was decided and why, what is deferred. The
code and git history record *what happened*. The brain records *what we meant and
what is next* — the part that is otherwise lost when a session's context ends.

It is gitignored on purpose: it holds strategy, private roadmap, infra notes and
operational detail that has no business in a repo that may be shared, open-sourced
or handed to a contractor.

**The rules for running it are not here** — they are in
`templates/private/WORKFLOW.md`, which the project reads every session. This file is
scaffold-time guidance: what each file is for, how to seed it, and the model of memory
behind the layout.

---

## The two axes of memory

Knowing *which tier* a fact belongs to is what keeps the brain from becoming
either bloated (loading cold history every session) or lossy (facts living only in
a volatile file). The project does not need this table; the scaffolding agent does,
to decide where things go.

**Axis 1 — project docs, by volatility:**

| Tier                | What it is                                        | Where                        | Read              |
| ------------------- | -------------------------------------------------- | ---------------------------- | ----------------- |
| Rules (constitution) | how we work; changes rarely, read always          | `WORKFLOW.md`                | every session     |
| Short (working)     | in-flight state, discarded when the task closes    | `baton.md`                   | every session     |
| Medium (active ref) | truth of the current era, changes cycle to cycle   | `operations/`                | on demand         |
| Long (slow ref)     | the stable technical HOW / product WHAT            | `engineering/`, `product/`   | on demand         |
| Cold (archive)      | history, almost never consulted                    | `archive/`, `*-archive.md`   | targeted search   |

**Axis 2 — the agent's own memory** (the harness's `MEMORY.md` / memory files):
this does **not** hold project state. It holds *how to work / who the human is /
environment gotchas*. It must stay small and high-signal, because unlike the docs
it is loaded on **every** session — weight hurts more there.

Weight rules:

- When an active doc stops being consulted, **move it to `archive/`** instead of
  letting it fatten `operations/`.
- When a stable fact lives in a volatile doc, **extract it to its reference doc and
  leave a pointer.**
- No file is both append-forever and mandatory reading → `WORKFLOW.md` §2.5.

---

## The files that must exist

### `WORKFLOW.md` — the living rules layer

Scaffold it whole. Its §1 carries the origin project's numbers as a placeholder; tell
the human to replace them with their own measurement the first time the brain feels
heavy. It is pruned, never appended, and that is only safe because the local backstop
repo exists (`SKILL.md` Step 4) — create the backstop before handing back.

Why it earns a file of its own: a rules layer scattered across `CLAUDE.md`, lane files
and a baton preamble ends up paraphrased in several places, and a targeted edit
always leaves a contradicting copy behind. **This skill had exactly that defect until
its own copies were collapsed into the templates.**

### `baton.md` — the handoff channel

Scaffold the template; seed `next:` (Step 5). Rules → `WORKFLOW.md` §2.4.

### `operations/implementation-status.md` and `operations/shipped-log.md`

State and narrative, split from day one (`WORKFLOW.md` §2.5). For a greenfield
project the status says "nothing yet" explicitly.

### `operations/backlog.md` — the tracker

Seed *Closed decisions* with the workflow itself and the merge stage with its reason.
*Next up* gets the real first tasks.

### `operations/owner-queue.md` — what waits on the human

The one list of things only the human can move. The baton knows nothing about it, and
the backlog does not keep a second copy.

### `operations/last-audit.md` — the audit marker

Both baselines start as `—`; the auditor's first pass writes them. The brain commit
(`.localgit`) and the repo commit are different histories and never share a value.

### `tools/doc-lint.py` — the mechanical half of the audit

Its docstring lists the checks. Seed `CANONICAL` with the facts this project will act
on, and `FOREIGN_PREFIXES` with any vendored doc tree it links into. Run it once after
scaffolding; it must come back clean.

---

## `INDEX.md` — the map

Paths and when to read them, not summaries (`WORKFLOW.md` §2.1). Delete the example
rows and list the docs that actually exist. It does not keep a session-start list.

---

## Folder roles

| Folder          | Role                                                                              |
| --------------- | --------------------------------------------------------------------------------- |
| `operations/`   | Day-to-day active docs: status, backlog, infra, runbooks, owner queue, audit marker. |
| `product/`      | The **WHAT** and **WHY**. Slow-changing. Strategy, user-facing specs, glossary.    |
| `engineering/`  | The **HOW**. Data model, auth flows, payment architecture, per-feature specs.      |
| `tools/`        | Scripts that check the brain mechanically.                                         |
| `archive/`      | Cold. Not deleted, not consulted.                                                   |
| `for-owner/`    | **The human's own space. Agents do not touch it.** Worth creating: it gives the human a place inside the brain that is theirs. |

---

## Seeding single-source homes

The rule → `WORKFLOW.md` §2.1. At scaffold time it means: fill
`operations/infrastructure.md` with the providers the project already uses (registrar,
DNS host, mail, hosting, DB, payments — as separate lines even when they are the same
company), and add each of those facts to `doc-lint.py`'s `CANONICAL` list so a second
copy fails loudly.

## Keeping it honest

The duty, the lint, the auditor's trigger and marker → `WORKFLOW.md` §2.5. What the
auditor hunts → `templates/claude/agents/doc-auditor.md`. It reports and never edits:
an auditor that fixes things is an auditor whose findings nobody reads.
