# `.private/` — Index

> Curated reading order for agent sessions and for humans navigating the docs.
> **Sparse by design: paths + when to read them, not summaries** (`WORKFLOW.md` §2.1).
> Its job is to let a session load only the docs its task needs.

---

## Session start

⛔ **The session-start checklist is NOT here.** It lives in `CLAUDE.md` and only
there. Follow that list; this file is the map you consult *after* it.

The rules of how we work → `WORKFLOW.md`. They are not restated here.

---

## If you touch…

| Topic                                                          | Doc                                    |
| -------------------------------------------------------------- | -------------------------------------- |
| **The rules in force** — how we work, who prunes, what counts as evidence | **`WORKFLOW.md`** (read first, every session) |
| What is actually LIVE vs only designed                          | `operations/implementation-status.md`  |
| **External infra** (registrar, DNS host, mail, hosting, DB, payments) | **`operations/infrastructure.md`** (single source) |
| Next tasks, deferred items, closed decisions                    | `operations/backlog.md`                |
| The work in flight and the implementer's feedback               | `baton.md`                             |
| What is waiting on the human                                    | `operations/owner-queue.md`            |
| How a past cycle shipped, why something is the way it is        | `operations/shipped-log.md` ⛔ not session-start reading |
| A closed handoff, verbatim                                      | `operations/baton-archive.md` ⛔ not session-start reading |
| Where the last docs audit stopped                               | `operations/last-audit.md`             |
| Checking the docs mechanically before an audit                  | `tools/doc-lint.py`                    |
| _Example — business model, pricing, roadmap_                   | _`product/strategy.md`_                |
| _Example — UX, flows, screens, roles, glossary_                | _`product/specs.md`_                   |
| _Example — data model, access rules, state machines_           | _`engineering/datamodel.md`_           |

⚠️ **The three italic rows are examples.** Delete them and add one row per doc that
actually exists — a row pointing at a file nobody created is the first dead link in
a brand-new brain, and `tools/doc-lint.py` will report it.

---

## Folder structure

`.private/` is **entirely gitignored** — never commit these files.

| Folder          | Role                                                                                              |
| --------------- | -------------------------------------------------------------------------------------------------- |
| `operations/`   | Active day-to-day docs. Snapshots that change cycle to cycle (status, backlog, infra, runbooks).   |
| `product/`      | The **WHAT** and **WHY**. Slow-changing. Strategy and user-facing specs.                           |
| `engineering/`  | The technical **HOW**. Schema, flows, per-feature specs. Comprehensive references.                 |
| `tools/`        | Scripts that check the brain mechanically (`doc-lint.py`).                                        |
| `archive/`      | Cold history. Not deleted, but not consulted except for a targeted search.                         |
| `for-owner/`    | **The owner's own space. Agents never touch it.**                                                  |

Top level: `WORKFLOW.md` (the rules), `baton.md` (active handoff) and this `INDEX.md`.

---

## Convention for new docs

| Situation                                           | Goes to                                  |
| --------------------------------------------------- | ---------------------------------------- |
| A spec, from the moment it is written               | `engineering/` (technical) or `product/` (UX/flow) |
| Operational doc (runbook, policy)                   | `operations/`                            |
| Snapshot that changes every cycle                   | `operations/`                            |
| Inter-session handoff                               | top level (only `baton.md` lives there)  |
| History no longer consulted                         | `archive/`                               |

When a spec finishes shipping it **stays** in `engineering/` / `product/` — it becomes
the reference. It does not move to `archive/` just because it shipped.

## Cross-reference convention

Docs reference each other by **path relative to `.private/`** (`operations/backlog.md`)
or, when unambiguous, by **simple filename** (`strategy.md`). Filenames are unique <!-- lint:ok -->
within `.private/` — `tools/doc-lint.py` enforces it.
