# The Colossus protocol — scaffold-time guide

**The rules are not here.** They live in the templates, which is what the scaffolded
project actually reads, together with the one-sentence reason that keeps each rule
alive. This file is for the agent running the skill: how to adapt each piece to the
project, when a piece may be dropped, and what must never be dropped.

| Doctrine | Home |
| --- | --- |
| Session-start checklist | `templates/CLAUDE.template.md` → "Session-start checklist" |
| Task levels | `templates/CLAUDE.template.md` → "Task levels" |
| Handoff cycle, stop signals, timestamp | `templates/CLAUDE.template.md` → "The standard handoff cycle" |
| Who merges, the two stages | `templates/CLAUDE.template.md` → "Who merges" |
| One fact one home; evidence; ask vs decide | `templates/private/WORKFLOW.md` §2.1–2.3 |
| Baton: pruning, feedback, specs born in `engineering/`/`product/` | `templates/private/WORKFLOW.md` §2.4 |
| Docs upkeep, doc-lint, auditor trigger, state vs narrative | `templates/private/WORKFLOW.md` §2.5 |
| Deferred items; close before opening a front | `templates/private/WORKFLOW.md` §2.6 |
| Baton fields | `templates/private/baton.md` |
| Escalation | `templates/claude/lanes/implementer.md` → "Escalating" |
| Visual approval | `templates/claude/lanes/planner.md` → "What you NEVER do" |

---

## 1. The core insight: split by context, not by capability

One terminal is the **planner**, one is the **implementer**. The role is
**declared by the human when starting the terminal** — it cannot be inferred from
the model, the branch, or the prompt.

The reason for the split is **context hygiene**, not cost. Planning fills a
context window with options, dead ends, discarded designs and long docs.
Implementing fills it with file contents, diffs, test output and CI logs. Mixed
together, both degrade: the builder re-litigates decisions that were already
closed, and the planner starts optimizing the code it just wrote instead of
questioning it.

When scaffolding, keep the three consequences agents get wrong intact in the lanes:
sensitive work goes to the implementer (never "I'd better do it myself"), the planner
never merges, and the terminals run serially.

---

## 2. The baton

Scaffold `templates/private/baton.md` as is: preamble, four fields, `## Pointers`.
Set `next:` to the first real task (Step 5). ⛔ Do not add a history field, an inline
spec section or a decisions cache — each one was a copy of something with a home, and
all three were removed for that reason.

---

## 3. Task levels

The level says **what the task is**, never which model or effort runs it. When
scaffolding: keep the three level names and both tests exactly as the template has
them, and ⛔ **do not write a level → model mapping anywhere**, even if the human
offers one. The template explains why; the short version is that the mapping is the
volatile half.

---

## 4. Who merges — when and how to graduate

Every project starts at **Stage 1** (the stages themselves → `templates/CLAUDE.template.md` →
"Who merges"). What the scaffolding agent needs to carry to the human:

**When to graduate** — the owner's call, not a rule. The signals: non-visual PRs have
been getting rubber-stamped with no findings for a while; CI and `pr-reviewer` have
demonstrably caught the things that mattered; and merging has become a bottleneck
rather than a checkpoint.

**How to graduate** — flip the **CURRENT MERGE STAGE** marker in `CLAUDE.md` → "Who
merges" (one place, so no doc can disagree with another), and record the change in
`backlog.md` → *Closed decisions* **with its date and its reason**. A policy whose
reason is unwritten is a policy that gets silently re-litigated.

**If the project has no UI**, Stage 2's visual gate has nothing to gate: delete it and
say so in the summary.

Merging is orthogonal to **applying database migrations** — those go through their
own deliberate workflow. If the project has a database, say which one in `CLAUDE.md`.

---

## 5. Stop signals

The emoji `🛑` / `✅` / `🕐` are fixed. The words are the human's interface, so they are
written in the chat language: fill `{{STOP_SIGNAL}}` and `{{DONE_SIGNAL}}` in
`{{CHAT_LANG}}` (Step 3). Set `{{TZ}}` from the machine's offset, confirmed by the
human.

---

## 6. The session-start checklist

Adapt two items to the project: the strategy doc (item 6 — delete it if the project
has none) and the framework-docs rule (item 9 — point it at where the installed
version's docs actually live). ⛔ Never copy the list into `INDEX.md` or anywhere
else.

---

## 7. The change cycle

Branch, commit, `verify` and review conventions → `templates/CLAUDE.template.md` →
"Development workflow". Fill `{{VERIFY_CMD}}` from Step 2.

---

## 8. Escalation

Keep the implementer lane's escalation section whole. 🔴 **If what a task needs is
more capability, the answer is to reopen the implementer at a stronger configuration —
never to move the work into the planning lane.** Escalation before writing code has
repeatedly turned out to be the highest-value move in this workflow: the implementer,
reading the actual code, is the first one positioned to discover that the spec's
premise was wrong.
