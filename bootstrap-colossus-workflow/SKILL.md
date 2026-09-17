---
name: bootstrap-colossus-workflow
description: Scaffolds the two-terminal "Colossus" workflow into a project — a planner terminal and an implementer terminal that hand work to each other through a gitignored baton file, plus a .private/ project brain (a short WORKFLOW rules layer, INDEX, backlog, implementation-status split from a shipped log, owner queue, infrastructure), pr-reviewer and doc-auditor subagents, a mechanical doc-lint, and the guardrails that make it work (CI, pre-commit hooks, a local `verify` mirror, and branch protection where the plan allows it). Use when starting a new project, or when adopting a disciplined multi-session agent workflow — triggers on "set up the Colossus workflow", "two-terminal workflow", "planner/implementer lanes", "baton handoff", "project brain", "scaffold the workflow we use in <other project>".
---

# Bootstrap the Colossus workflow

## What this is

A workflow for building a real project with coding agents across many sessions,
where context is lost every session and the human is the only continuous thread.
It rests on four ideas:

1. **Two terminals, split by role, never by capability.** A **planner** designs
   and specs; an **implementer** builds and ships. The split exists to keep
   planning context and build context from contaminating each other — not because
   one is cheaper. **The two may or may not run the same model; that is the
   human's configuration call and it never decides which terminal is which.**
2. **A written handoff channel** (the *baton*) that survives context loss, so any
   session can be resumed cold by reading three files.
3. **A merge gate that starts closed and opens as trust is earned** — at first the
   owner merges everything; once the project has proven the machinery catches what
   matters, the implementer self-merges what a machine can fully judge and the
   owner keeps only what the end-user will see. See "The merge stages" below.
4. **Guardrails that fail loudly** — a local mirror of CI, a fresh-eyes review
   subagent before every merge, and a docs auditor that hunts drift.

## When NOT to use this

- The project **already** has a `.private/` brain and lane files — edit those,
  don't scaffold a second, drift-prone copy of the same process.
- The user only wants to record one fact or one task — put it in the relevant doc
  or the backlog directly.
- A throwaway script or a one-session spike. This workflow's whole value is
  surviving *across* sessions; below that horizon it is pure overhead.

## The merge stages

Merging is what puts code in production, so the gate is the one place where trust
has to be earned rather than assumed. **A new project always starts at Stage 1.**

| Stage | Who merges |
| --- | --- |
| **1 — Owner merges all** (default) | The owner, every PR. |
| **2 — Owner merges visual** (after graduation) | The owner for what the end-user sees; the implementer for the rest. |

The rules → `templates/CLAUDE.template.md` → "Who merges". When and how to graduate →
`references/protocol.md` §4.

## Where the doctrine lives

The **templates** carry the rules and the short reason that keeps each one alive in
the scaffolded project — that is what the project reads every session.
`references/` carries scaffold-time guidance (how to adapt a piece, when it may be
dropped) and points at the templates for the rules. This file carries the procedure.
⛔ Do not copy a rule into a reference or into this file: the skill already paid for
that once, with copies that contradicted each other.

Read `references/protocol.md` before scaffolding: it maps every rule to its home.

## What gets scaffolded

```
CLAUDE.md                      session-start checklist + workflow + conventions
AGENTS.md                      8-line pointer to CLAUDE.md (other agent tools)
.claude/
  settings.json                permission denies (.env secrets), shared allows
  lanes/<planner>.md           what the planning terminal may and may not do
  lanes/<implementer>.md       what the building terminal may and may not do
  agents/pr-reviewer.md        fresh-eyes pre-merge review subagent
  agents/doc-auditor.md        read-only docs drift auditor subagent
.private/                      GITIGNORED — the project brain
  WORKFLOW.md                  🔴 the rules in force. Read first, pruned not appended
  baton.md                     the handoff channel: in-flight state + feedback
  INDEX.md                     curated map: which doc to read for which task
  operations/
    backlog.md                 In progress / Done / Next up + closed decisions
    implementation-status.md   what is LIVE vs only designed — STATE ONLY
    shipped-log.md             how each cycle shipped — NOT session-start reading
    baton-archive.md           closed handoffs, verbatim — NOT session-start reading
    owner-queue.md             what waits on the human (never lives in the baton)
    infrastructure.md          single canonical home for external-infra facts
    last-audit.md              marker: the commit the next doc audit scopes from
  engineering/                 the technical HOW (specs, data model, flows)
  product/                     the WHAT and WHY (strategy, user-facing specs)
  tools/doc-lint.py            mechanical doc checks — run before the auditor
  archive/                     cold storage
  for-owner/                   the human's own space — agents never touch it
.localgit/                     GITIGNORED — the undo backstop for everything above
                               that the host never sees. See Step 4.
.github/workflows/ci.yml       the checks that gate every merge
.husky/pre-commit              DERIVED from the stack, not copied — see Step 2/4
package.json → "verify"        DERIVED from the stack, not copied — see Step 2
```

Everything above has a template behind it except the two rows marked **DERIVED**:
the pre-commit hook and the `verify` command are built from the stack you detect,
because no single file could fit every stack. Step 2 says how to build them.

## Procedure

### Step 0 — Preflight

```bash
git rev-parse --is-inside-work-tree     # must be a git repo; offer `git init` if not
ls CLAUDE.md AGENTS.md .claude .private 2>/dev/null
```

**Never clobber.** If `CLAUDE.md`, `.claude/`, or `.private/` already exist, read
them first and *merge* — add the missing workflow sections, keep whatever the
project already says. Announce what you found before writing anything. A project
that already has a CLAUDE.md has conventions in it that the human wrote on
purpose.

### Step 1 — Interview (one turn, two parts)

Do not guess these from the repo — the answers are policy, not facts. Ask everything
in **one message**: `AskUserQuestion` for the four choices (it takes at most four
questions, each with 2–4 options), and plain text in the same message for the three
free-text answers.

**`AskUserQuestion`, four questions:**

1. **Role names** — `Max Opus` / `Opus Jr.` (slugs `max-opus` / `opus-jr`) vs the
   model-agnostic `Max` / `Jr.`. The protocol is identical either way; only the labels
   move.
2. **Code + docs language** — English (recommended: docs in English travel) vs the
   human's language.
3. **Chat language** — the human's choice. It is separate from (2) on purpose, and it
   is the language of the stop signals.
4. **Merge stage** — **Stage 1** (recommended for a new project: the owner merges
   every PR) vs Stage 2. Record the choice **and its reason** in `backlog.md` →
   *Closed decisions*.

**Plain text, same message:**

- **Project name** and one line on what it is (`{{PROJECT}}`, `{{PITCH}}`).
- **The owner's name** (`{{OWNER}}`) — the brain addresses them by it.
- **Timezone** — read the machine's offset first (`date '+%z'` / `Get-Date -Format
  'zzz'`) and ask them to confirm it, rather than asking cold.

### Step 2 — Detect the stack, derive `verify` and CI

Read the manifest (`package.json`, `pyproject.toml`, `go.mod`, `Cargo.toml`…) and
build the **verify** command out of the checks that are *deterministic and fast*:
format-check, lint, typecheck, unit tests. **Leave build and integration tests out
of `verify`** — they belong in CI only, because they are slow and (on Windows, or
without a DB) not reproducible locally, and a local check that disagrees with CI
is worse than no local check.

The per-stack commands → `references/guardrails.md` §1.

Wire it as a single named command (`npm run verify`, `make verify`, `just verify`)
— the lane file will reference it by that name.

CI (`.github/workflows/ci.yml`) runs **the same checks plus build** (plus any
integration job the project needs). The invariant: *CI is a superset of `verify`,
and `verify` never disagrees with CI on the checks they share.*

⚠️ **Define the individual checks as named commands too, not only `verify`.** CI
invokes them one by one (`format:check`, `lint`, `typecheck`, `test`, `build`) on
purpose, so a red run says *which* check fell instead of just "verify failed". A
project that wires only the aggregate command has a red CI from its first commit.

⚠️ **If this project deploys to shared hosting, `ci.yml` is not yours to create.**
The `hostinger-static-hosting` skill scaffolds a single `CI & Deploy` workflow at
that same path, and it must stay single: `needs:` only works between jobs of the
**same** workflow, so a second workflow triggered by `push` on the default branch is
an independent run — a merge with failing checks would still deploy. When that skill
has already run (or is going to), **merge the Colossus checks into its `quality` job**
and leave its `audit` and `deploy` jobs alone. Never add a second workflow file.

### Step 3 — Write the files

Copy each file from `templates/` and substitute:

| Placeholder           | Value                                                     |
| --------------------- | --------------------------------------------------------- |
| `{{PROJECT}}`         | project name                                              |
| `{{PITCH}}`           | one-line description                                       |
| `{{PLANNER}}`         | planner display name (e.g. `Max Opus`)                    |
| `{{IMPLEMENTER}}`     | implementer display name (e.g. `Opus Jr.`)                |
| `{{planner-slug}}`    | e.g. `max-opus` — filename + baton `to:` value            |
| `{{implementer-slug}}`| e.g. `opus-jr`                                            |
| `{{VERIFY_CMD}}`      | e.g. `npm run verify`                                     |
| `{{CODE_LANG}}`       | e.g. `English`                                            |
| `{{CHAT_LANG}}`       | e.g. `Spanish`                                            |
| `{{TZ}}`              | e.g. `Chile (GMT-4)`                                      |
| `{{STOP_SIGNAL}}`     | the stop line's words in `{{CHAT_LANG}}`, ending where the role name goes — e.g. `PARADA — cambia a la terminal de` / `STOP — switch to the terminal of` |
| `{{DONE_SIGNAL}}`     | the done word in `{{CHAT_LANG}}` — e.g. `LISTO` / `DONE`. The emoji (🛑 ✅ 🕐) stay fixed |
| `{{DEFAULT_BRANCH}}`  | usually `main`                                            |
| `{{NODE_MAJOR}}`      | the Node major version the project builds on — read it from `.nvmrc` or `package.json` → `engines` |
| `{{STACK_TABLE}}`     | the detected stack, as a small table                       |
| `{{TODAY}}`           | `date '+%Y-%m-%d'` — read it, don't assume                |
| `{{OWNER}}`           | the human's name — the brain addresses them by it          |
| `{{MERGE_STAGE}}`     | `Stage 1 — the owner merges everything` (default for a new project) |
| `{{MERGE_STAGE_WHY}}` | the reason, in the owner's words — it goes in *Closed decisions* |
| `{{BRANCH_RULES}}`    | the `CLAUDE.md` section on the default branch — one of the two blocks below |

`{{BRANCH_RULES}}` depends on whether Step 4.5 could protect the branch — fill it once that step has run:

- **protected** — a ``### `{{DEFAULT_BRANCH}}` is protected`` heading, then what is
  enforced: no direct pushes, changes via PR only, CI must pass, force-push and
  branch deletion blocked, linear history required.
- **not available** — a ``### `{{DEFAULT_BRANCH}}` — the rules are a convention``
  heading, then the same rules, **saying plainly that nothing enforces them**
  (`references/guardrails.md` §4).

`last-audit.md` ships with both baselines as `—`; the auditor's first pass writes them.

Template → destination:

| Template                                        | Destination                              |
| ----------------------------------------------- | ---------------------------------------- |
| `templates/CLAUDE.template.md`                  | `CLAUDE.md`                              |
| `templates/AGENTS.template.md`                  | `AGENTS.md`                              |
| `templates/claude/settings.json`                | `.claude/settings.json`                  |
| `templates/claude/lanes/planner.md`             | `.claude/lanes/{{planner-slug}}.md`      |
| `templates/claude/lanes/implementer.md`         | `.claude/lanes/{{implementer-slug}}.md`  |
| `templates/claude/agents/pr-reviewer.md`        | `.claude/agents/pr-reviewer.md`          |
| `templates/claude/agents/doc-auditor.md`        | `.claude/agents/doc-auditor.md`          |
| `templates/private/WORKFLOW.md`                 | `.private/WORKFLOW.md`                   |
| `templates/private/baton.md`                    | `.private/baton.md`                      |
| `templates/private/INDEX.md`                    | `.private/INDEX.md`                      |
| `templates/private/operations/*.md`             | `.private/operations/*.md`               |
| `templates/private/tools/doc-lint.py`           | `.private/tools/doc-lint.py`             |
| `templates/github/ci.yml`                       | `.github/workflows/ci.yml`               |
| `templates/gitignore-snippet.txt`               | appended to `.gitignore`                 |

Also create the empty brain folders the INDEX promises: `.private/engineering/`,
`.private/product/`, `.private/archive/`, `.private/for-owner/`.

Fill the templates; do not paraphrase them. If a template rule genuinely does not
apply (e.g. no UI ⇒ no visual-merge gate), **delete the rule and say so in the
summary** — don't leave a rule in place that the project will silently violate.

**Last, run the project's own formatter in write mode** over the scaffolded files the
repo tracks (`CLAUDE.md`, `AGENTS.md`, `.claude/`, `.github/workflows/ci.yml`). The
templates are deliberately not pre-formatted: a format that passes one formatter's
defaults is not one that passes this project's config, and a formatter run before
substitution can rewrite a `{{…}}` inside YAML. Skip it and Step 6's `verify` fails.

⚠️ **If you renumber or drop a section of `WORKFLOW.md`, re-point the references to
it.** `CLAUDE.md`, the lanes, `doc-auditor.md`, several brain docs and `doc-lint.py`
cite it by number (`WORKFLOW.md §2.1`–`§2.6`), and some of `doc-lint.py`'s are inside
the *error messages it prints*. This has already broken once: the template was trimmed, every `§3.x`
became `§2.x`, and six pointers were left aiming at nothing — the linter's own
check #1, failing on the linter. **After scaffolding, run `doc-lint.py` once; it
must come back clean.**

### Step 4 — Guardrails

1. **`.gitignore`** — append `templates/gitignore-snippet.txt` (Step 3 already did).
   `.claude/settings.json`, `.claude/lanes/` and `.claude/agents/` **stay tracked**
   — they are shared config, and an agent that can't read its own lane is not in
   the workflow.
2. **The local backstop repo.** `.private/` is gitignored, so by default nothing in
   the brain is under version control at all: an overwritten `WORKFLOW.md`, or a
   baton truncated by a stray shell redirection, is simply gone. Two templates
   already tell the agent that pruning is safe because the history is recoverable —
   this is the step that makes that true.

   **Why not a nested `.git/` inside `.private/`.** It works — for `.private/` only.
   Git treats a nested repository as an embedded repo and silently skips its contents
   from the parent, so a nested repo can never cover `CLAUDE.md` or `.claude/`, which
   are exactly the files the pull incident below deleted. That is why the default is
   one separate git dir at the repo root whose worktree *is* the root:

   ```bash
   GIT_DIR=.localgit GIT_WORK_TREE=. git init
   GIT_DIR=.localgit GIT_WORK_TREE=. git add -f CLAUDE.md .claude .private
   GIT_DIR=.localgit GIT_WORK_TREE=. git commit -m "chore: scaffold the workflow"
   ```

   `-f` is **required and permanent**, not a one-off: this repo reads the worktree's
   `.gitignore`, the same file that keeps these paths off the host. Expected, not a
   misconfiguration. Recovery is one command:

   ```bash
   GIT_DIR=.localgit GIT_WORK_TREE=. git checkout -- <path>
   ```

   **Nothing commits automatically.** Tell the human where the commit belongs: at the
   close of each cycle, in the same breath as pruning the baton.

   ⚠️ **It earns its place immediately.** On a real project, a merge that untracked six
   workflow files deleted all six from disk on the next `git pull` — correct git
   behaviour, since they had been tracked in the old default branch. Only the local
   repo brought them back.
3. **`.claude/settings.json`** — the secret-file deny rules (Step 3 wrote them from
   `templates/claude/settings.json`). Keep `.env.example` readable.
4. **Pre-commit** — husky + lint-staged (Node) or pre-commit (Python): format and
   lint the *staged* files, abort the commit on failure.
5. **Branch protection** on `{{DEFAULT_BRANCH}}`, where the plan allows it → the
   command, and what to do when it fails, in `references/guardrails.md` §4.

### Step 5 — Seed the brain with reality

An empty brain is a dead brain. Before finishing:

- **`implementation-status.md`** — write today's honest snapshot: what actually
  runs, what is only designed. For a greenfield project that is "nothing yet";
  say so explicitly rather than leaving the template prose.
- **`backlog.md`** — put the real next tasks under *Next up*, and seed *Closed
  decisions* with the two calls just made: the workflow itself, and **the merge
  stage with its reason and its graduation trigger**.
- **`INDEX.md`** — list the docs that actually exist. Delete rows for folders you
  didn't create.
- **`baton.md`** — set `to: {{planner-slug}}` and `next:` = the first real task.

### Step 6 — Hand back

Run `{{VERIFY_CMD}}` (it passes on a fresh scaffold once Step 3's formatter run is done), confirm `git status` shows
neither `.private/` nor `.localgit/`, confirm the backstop holds the scaffold
(`GIT_DIR=.localgit GIT_WORK_TREE=. git log --oneline`), then print the kickoff:

> The workflow is live. Open a terminal and say **"you are {{PLANNER}}"** to plan,
> or **"you are {{IMPLEMENTER}}"** to build. One at a time, never
> both. Each terminal reads its lane file at session start.

## Non-negotiables

These are the load-bearing walls. A scaffold that drops one of them looks like the
workflow but does not behave like it. One line each; the rule and its reason live at
the pointer.

- **The role is declared by the human, never inferred** → `templates/CLAUDE.template.md` →
  "Multi-terminal workflow".
- **Serial, never parallel** → `templates/CLAUDE.template.md` → "Multi-terminal workflow".
  📌 Do not adopt worktree-per-task parallelism for a solo human: the bottleneck is one
  person's attention, not the working copy.
- **Every handoff turn ends with a stop signal, and every turn with the timestamp** →
  `templates/CLAUDE.template.md` → "The standard handoff cycle".
- **The planner never implements and never merges** →
  `templates/claude/lanes/planner.md`.
- **No unapproved visual change reaches a spec** → `templates/claude/lanes/planner.md`.
- **The baton is a channel; the implementer leaves feedback and never prunes; the
  planner prunes on pickup** → `templates/private/WORKFLOW.md` §2.4.
- **The done signal only when the human genuinely acts next** →
  `templates/CLAUDE.template.md` → "The standard handoff cycle".
- **Specs are born in `engineering/` / `product/`, never in the baton** →
  `templates/private/WORKFLOW.md` §2.4.
- **No file is both append-forever and mandatory reading** →
  `templates/private/WORKFLOW.md` §2.5.
- **Ask what lives in the human's head; decide what is technical** →
  `templates/private/WORKFLOW.md` §2.3.
- **An absence is a question, not a finding** → `templates/private/WORKFLOW.md` §2.2.
- **Deferred items go to the backlog the same turn; close before opening a front** →
  `templates/private/WORKFLOW.md` §2.6.

## Common failure modes (warn the human about these)

- **Docs drift during build phases** → `templates/private/WORKFLOW.md` §2.5.
- **The same fact restated in three docs** → `templates/private/WORKFLOW.md` §2.1.
- **Level drift mid-task** → `templates/CLAUDE.template.md` → "Task levels".

## Reference files

- `references/protocol.md` — the full workflow: roles, baton, task levels, merge
  ownership, stop signals, escalation, and the incidents each rule came from.
- `references/project-brain.md` — the `.private/` doc system: volatility tiers,
  what goes where, the single-source-of-truth rule, how to keep it small.
- `references/guardrails.md` — CI, `verify`, hooks, branch protection, the
  subagents, and the secret-handling permission denies.
