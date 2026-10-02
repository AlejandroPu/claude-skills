# {{PROJECT}} — AI Agent Guide

This file is loaded at the start of every Claude Code session. It is the single
source of truth for how to work in this repo: workflow, architecture, conventions.
(If the repo has a `README.md`, it carries the product pitch and local setup.) <!-- lint:ok -->

---

## Session-start checklist

Do these at the top of every session — in order, before writing any code:

1. 🔴 **Read `.private/WORKFLOW.md` — first.** The rules in force: single source of
   truth, what counts as evidence, how a handoff closes, who prunes and when. Short
   on purpose, and pruned rather than appended, so it stays cheap to read.
2. **Read `.private/baton.md`** — handoff notes from the previous session:
   current state, next step, and {{IMPLEMENTER}}'s feedback.
3. **Read `.private/INDEX.md`** — curated map of `.private/`. Tells you which doc
   to load for each kind of work without loading everything by default.
4. **Read `.private/operations/implementation-status.md`** — snapshot of live vs
   designed. What is actually shipped vs only planned.
5. **Read `.private/operations/owner-queue.md`** — what is waiting on the human.
   It does not live in the baton, and it must never be reconstructed from
   {{IMPLEMENTER}}'s list at closing time.
6. **Read the strategy/product doc** (e.g. `.private/product/strategy.md`) **if the <!-- lint:ok -->
   project has one and** your task touches the business model or anything
   user-facing-strategic. Private roadmap context — never quote it verbatim in
   commits, PRs or README.
7. **Read your lane file** at `.claude/lanes/<your-role>.md`, role ∈
   {`{{planner-slug}}`, `{{implementer-slug}}`} — **the user declares which role
   this terminal is** when starting it. If unsure, ask before picking up work. The
   lane file defines what you may and may not do this session; read it every
   time, not from memory.
8. **Run `git status`** — confirm branch state and any uncommitted work.
9. **Read the installed framework's own docs before writing framework code** —
   not your training data. APIs and conventions differ between major versions, and
   a stale pattern fails *silently*.

⛔ **This list lives here and only here.** `INDEX.md` must not keep a second copy —
a competing session-start list desynchronises, and has.

---

## What the project is

{{PITCH}}

---

## Language conventions

- **Code and docs (including `.private/`)**: {{CODE_LANG}} — variable/function
  names, comments, commit messages, branch names, PR titles and bodies.
- **Chat with the user**: {{CHAT_LANG}}.
- **User-facing copy**: if the product has user-facing copy, it lives in the i18n
  message files — never hardcoded in components.

---

## Multi-terminal workflow — the Colossus

Two terminals split by role: **{{PLANNER}}**
(planning / architecture / process design) and **{{IMPLEMENTER}}** (implementation /
full PR lifecycle). **Only one is active at a time.** The role is **declared by the
user when starting the terminal**, never inferred from the model. Hand off via
`.private/baton.md` (gitignored). Each terminal reads its lane file
(`.claude/lanes/<role>.md`) at session start.

Why split by role: it keeps planning and implementation in separate context
windows so each stays focused. The cost is re-syncing file/git state on each
pickup — which is exactly what the baton encodes.

### Task levels

{{PLANNER}} tags every handoff with **what the task is**, in three levels. **The
human picks the model and the effort from that** when they open the
{{IMPLEMENTER}} terminal.

| Level | The task is | Typical |
| --- | --- | --- |
| `easy` | **Transcription.** The spec says what to type; no judgement calls, no branching. | copy strings, deleting dead config, renames |
| `normal` | **Real implementation — normal _through difficult_.** Multiple files, logic, edge cases, judgement inside the spec's frame. **The everyday default.** | features, refactors, auth surfaces, payments internals |
| `sensitive` | **It cannot be fixed forward.** | destructive database work above all |

**The test, and it is the only thing that moves a task up to `sensitive`:**
_"if this goes wrong, can I fix it forward?"_ Yes → `normal`. No → `sensitive`.

🔴 **`sensitive` is irreversibility, not difficulty.** Intricate logic, many
branches, a wide blast radius, even auth and security surfaces are all
**specifiable**, and once specified they are transcription. **The difficulty is
carried by the spec, not the level** — the answer to a hard task is a better
spec. However hard it is, it is still `normal`.

**And the test for the bottom of the scale:** _"can the spec be verified without
leaving the spec?"_ Yes → `easy`. No → `normal`.

🔴 **A spec that hands over finished text is not automatically transcription.**
Written-out ≠ verifiable in place. **When correctness depends on something
outside the spec, it is `normal` however finished the text looks.**

⚠️ **When in doubt about difficulty, write more spec — do not go up a level.**
The go-up reflex applies only to irreversibility.

🔴 **The mapping from level to model and effort is deliberately NOT recorded
here.** It is the human's call when they open the terminal, and keeping it out is
what stops this section churning: a task's nature is stable, the right model for
it is not. (In the origin project this section was rewritten three times in nine
days, and every time it was the model mapping that moved, never the tasks.)

The baton carries the level in one field (`level:`) and the stop line echoes it, so the human knows what they are opening a terminal for. **One task = one
level, start → finish** — scope each handoff as one coherent unit; if part is
trivial and part is irreversible, split it or size the whole thing at the higher
level.

**{{PLANNER}} carries no level tag** — planning is planning, and the human starts
that terminal wherever they want it.

### Lane summary

| Role              | Does                                                                                                  | Never does                                                          |
| ----------------- | ------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------- |
| **{{PLANNER}}**     | architecture, hard debugging, process design, fine specs with `file:line`                            | mechanical implementation; merging (the PR lifecycle is the other lane) |
| **{{IMPLEMENTER}}** | implementation, full PR lifecycle, `pr-reviewer`, post-merge cleanup, and whatever merging the **current merge stage** grants it | merge anything the current merge stage does not grant it (see "Who merges") |

### The standard handoff cycle

```
{{PLANNER}}     → designs the approach, writes the fine spec → hands off via baton
{{IMPLEMENTER}} → codes, opens PR, waits for CI green
                → runs pr-reviewer, fixes, loops to PASS
                → then, per the CURRENT MERGE STAGE (see "Who merges"):
                    Stage 1 → ✅ hands EVERY PR to the owner for merge
                    Stage 2 → non-visual: squash-merges it directly → cleanup
                                          → feedback in the baton → 🛑 to {{PLANNER}}
                              visual:     ✅ hands off to the owner for merge
User            → squash-merges in the UI → back to {{IMPLEMENTER}}
{{IMPLEMENTER}} → git checkout {{DEFAULT_BRANCH}} && git pull && git branch -d <branch>
                → feedback in the baton → 🛑 to {{PLANNER}}
{{PLANNER}}     → pickup: reads the feedback, updates the docs, prunes the baton
                  (`.private/WORKFLOW.md` §2.4–2.5)
```

Each STOP is a hard stop: update `baton.md` (`to:`, `next:`, `stop_reason:`) and
end the turn with one of these signals so the user sees which terminal to open
next — **never end a handoff turn with prose narration alone**:

- `🛑 {{STOP_SIGNAL}} <{{PLANNER}}|{{IMPLEMENTER}}>.` — work remains in another lane.
  **After {{IMPLEMENTER}} merges and cleans up, this is the signal**: the next actor is
  {{PLANNER}}.
- `✅ {{DONE_SIGNAL}} — <one-line summary>.` — **only when the user genuinely acts
  next** (a PR the current merge stage assigns to them). Never to close a cycle
  {{IMPLEMENTER}} merged itself.

**Every turn ends with the timestamp line — handoff or not:**

```
🕐 260904, 15:54 hrs {{TZ}}
```

Read it from the machine — `date '+%y%m%d, %H:%M'` (POSIX shells) or
`Get-Date -Format 'yyMMdd, HH:mm'` (PowerShell); the machine is set to {{TZ}} — never
estimated. The user is the scheduler and that stamp is how they tell which
terminal they touched last, and how stale it is. It carries the date because these
terminals are left open overnight, and yesterday's `15:50` reads exactly like a
fresh one.

---

## Stack

{{STACK_TABLE}}

---

## Architecture

<!-- Replace with the real architecture once there is one. Keep it to the shape a
     newcomer needs: entry points, data flow, where the auth boundary is. -->

---

## Development workflow

{{BRANCH_RULES}}

### Change cycle

```bash
git checkout {{DEFAULT_BRANCH}} && git pull   # sync
git checkout -b <type>/<kebab-name>           # branch
# ... edit, commit ...
{{VERIFY_CMD}}                                # local CI mirror — must be green
git push -u origin <branch>
gh pr create --title "..." --body "..."
# wait for green CI, run pr-reviewer
# → then merge per the CURRENT MERGE STAGE (see "Who merges")
```

### Automated pre-merge review

After CI is green and before merging, invoke the **`pr-reviewer`** subagent
(`.claude/agents/pr-reviewer.md`). It reads the diff with fresh eyes and returns
`PASS` / `CHANGES REQUESTED` / `BLOCK` against a checklist beyond CI (leftover
`TODO`s, secrets, boilerplate, accessibility, scope creep, missing or unsafe
migrations).

- Only invoke it **after CI is green**. Skip only for trivial docs-only typo PRs.
- On `BLOCK` / `CHANGES REQUESTED`: fix as new commits, re-invoke. Loop to `PASS`.
- Only once `PASS`: the PR is mergeable (see "Who merges").

### Who merges

> ## ⚠️ CURRENT MERGE STAGE: **{{MERGE_STAGE}}**
>
> This one line governs every merge decision in the repo. It is flipped
> deliberately by the owner, and the flip is recorded in `backlog.md` → *Closed
> decisions* with its date and reason.

Merging to `{{DEFAULT_BRANCH}}` marks code entering production. The gate starts
closed and opens as the project earns trust:

**Stage 1 — the owner merges everything.** (Where a new project starts.)
{{IMPLEMENTER}}'s job **ends at PR open + CI green + `pr-reviewer` PASS** → hand
off to the owner and stop. No exceptions, not even for a one-line docs fix. Early
on, every merge is the owner's chance to catch drift in taste, architecture or
scope that no checklist encodes — and PR volume is low enough that it costs little.

**Stage 2 — the owner merges anything visual.** (After graduation.)

- **The owner merges any PR with visual / UI changes** — anything the end-user sees
  or interacts with (landing, public pages, dashboard UI, user-facing copy,
  layout). **When in doubt whether a PR is "visual", treat it as visual and hand it
  off.** A PR is **reclassified mid-flight** if a fix pulls a user-facing file into
  the diff.
- **{{IMPLEMENTER}} may squash-merge a non-visual PR itself** once CI is green and
  `pr-reviewer` is `PASS` — back-end logic, API routes, crons, lib refactors, tests,
  tooling/CI, docs, dependency bumps. There is nothing for the owner to eyeball.
  Use `gh pr merge --squash --delete-branch`, then
  `git checkout {{DEFAULT_BRANCH}} && git pull`.

**PRs no lane opened** (Dependabot, other bots). {{PLANNER}} triages them on pickup,
like any other input.

- **Green** goes to whoever the current stage says merges it. In Stage 1 that is the
  owner. In Stage 2 it is {{IMPLEMENTER}}, handed over on the baton as an `easy` task:
  `pr-reviewer`, then merge.
- **Red** becomes a spec for {{IMPLEMENTER}}, like any other task.

⚠️ A human commit on a bot's branch stops the bot from rebasing it. When a fix has to
land on one, let the bot rebase first, then commit.

**In both stages, {{PLANNER}} never merges** — merging is part of the PR lifecycle,
which is the other lane.

**The subagents are quality gates, not merge gates.** A `pr-reviewer` PASS never
authorizes a merge on its own; it only means the PR is *ready* for whoever the
current stage says merges it.

Merging a PR **never applies database migrations** — those go through their own
deliberate workflow, so the merge decision is independent of any schema change a
PR carries.

### Branch & commit conventions

Branches: `<prefix>/<kebab-name>`, prefix ∈ `feat` `fix` `chore` `docs` `test`.
Commits: **Conventional Commits**. The squash merge of each PR leaves one commit
per feature on `{{DEFAULT_BRANCH}}`, so `git log` reads as a feature timeline.

### Pre-commit & CI

- **Pre-commit**: lint + format over staged files. The commit aborts on failure.
- **CI**: all checks must pass before merge.
- **Before pushing a code PR, run `{{VERIFY_CMD}}` locally** — the deterministic CI
  mirror; it gives the same verdict as CI on the checks they share. Build and
  integration tests stay CI-only.

---

## Code conventions

<!-- Project-specific. Fill as the codebase grows. Keep this section short and
     about *decisions*, not about what the code obviously does. -->

---

## What NOT to do

- ❌ **Do not read, open, or quote `.env*` secret files.** They hold production
  secrets. Use `.env.example` (placeholders, safe to read and edit).
- ❌ **Do not commit secrets.** If one reaches history, rotate it immediately.
- ❌ **Do not push to `{{DEFAULT_BRANCH}}`** — always branch + PR.
- ❌ **Do not merge with CI red.**
- ❌ **Do not apply production migrations out-of-band** — they go through the
  deliberate deploy workflow, never a local `migrate deploy`.
- ❌ **Do not leave a deferred item only in chat** → `.private/WORKFLOW.md` §2.6.
