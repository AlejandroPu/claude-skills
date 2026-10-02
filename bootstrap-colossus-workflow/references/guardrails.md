# Guardrails

The workflow's rules are only as good as the machinery that makes breaking them
loud. This is that machinery. Everything here is stack-agnostic in principle; the
Node/TS commands are examples to translate.

---

## 1. The local CI mirror (`verify`)

One named command that runs **only the deterministic, fast checks**:

```
verify = format:check + lint + typecheck + unit tests
```

The implementer runs it **before every push of a code PR**. Docs-only PRs skip it.

**What must NOT go in it: build, and integration tests that need a database.**
They are slow, and they are not faithfully reproducible on every dev machine
(a case-insensitive filesystem will happily build something that fails on the CI
runner; integration tests need a real DB). Those stay CI-only.

The invariant that makes `verify` worth running:

> **CI is a superset of `verify`, and on the checks they share, they never
> disagree.**

A local check that can disagree with CI is worse than no local check — it teaches
the agent to distrust green.

| Stack   | `verify`                                                                    |
| ------- | --------------------------------------------------------------------------- |
| Node/TS | `prettier --check . && eslint && tsc --noEmit && vitest run`                 |
| Python  | `ruff format --check . && ruff check . && mypy . && pytest -q`               |
| Go      | `test -z "$(gofmt -l .)" && go vet ./... && go test ./...`                   |
| Rust    | `cargo fmt --check && cargo clippy -- -D warnings && cargo test`             |

---

## 2. CI

Gates every merge into the default branch. Runs on `pull_request` and on `push`
to the default branch. It runs the `verify` checks **plus** the ones that can only
live on a runner:

```
install → (dependency audit) → format:check → lint → typecheck → test → build
                                                        (+ integration job, if any)
```

Two things worth copying:

- **A supply-chain gate**: fail the build on high/critical advisories in
  *production* dependencies (`npm audit --audit-level=high --omit=dev`). Dev-only
  tooling advisories do not block, and CI does not report them either — `--omit=dev`
  leaves them out. GitHub's security alerts are what surface them, so those stay on
  — and `templates/github/dependabot.yml` turns on version updates too, grouped.
  They never reach the runtime, and blocking on them trains people to ignore the gate.
- **A separate integration job** running in parallel against a *faithful* database
  (the real engine, real migrations, real constraints and triggers), not a mocked
  one. Mocked unit tests are the blind spot where constraint/trigger bugs ship
  green. If the project has a DB, it needs this job.

Name the required check explicitly (e.g. `Check, test & build`) — branch
protection references it by name.

---

## 3. Pre-commit

`husky` + `lint-staged` (Node), or `pre-commit` (Python): run the formatter and
linter over **staged files only**, and abort the commit on failure. Cheap, fast,
and it keeps CI from failing on things a formatter could have fixed.

```
.husky/pre-commit  →  npx lint-staged
```

---

## 4. Branch protection

On the default branch:

- No direct pushes — changes come through PRs.
- The CI check must pass before merge.
- Linear history required (so squash-merge produces one commit per feature and the
  log reads as a timeline).
- Force-push and branch deletion blocked.

This is what makes "never push to the default branch" an enforced fact rather than a
hope. If the owner chose protection in the interview (`SKILL.md` Step 1), run this
call (use the job names actually in the project's `ci.yml` — the Colossus template
or, on a Hostinger project, the one the `hostinger-static-hosting` skill wrote):

```bash
gh api -X PUT repos/:owner/:repo/branches/<default-branch>/protection \
  -F 'required_status_checks[strict]=true' \
  -f 'required_status_checks[contexts][]=Check, test & build' \
  -f 'required_status_checks[contexts][]=Audit production dependencies' \
  -F 'enforce_admins=true' -F 'required_linear_history=true' \
  -F 'allow_force_pushes=false' -F 'allow_deletions=false' \
  -F 'required_pull_request_reviews=null' -F 'restrictions=null'
```

`-F` sends a typed value (`true`, `null`); `-f` sends a string, so it is only for the
check names.

**How to tell the plan does not have it:** the call fails with a **403** asking to
upgrade or make the repo public. **Do not retry.** Fill `{{BRANCH_RULES}}` with the
convention wording (`SKILL.md` Step 3).

⚠️ **On plans where it is unavailable, do NOT write that it exists.** A safety net
that lives only in prose is worse than none: nobody looks for it until the day it was
supposed to catch something. Write it as a convention with a track record instead,
and say plainly that nothing enforces it.

Before proposing any guard, ask the base rate and whether the failure would have been
visible → `templates/private/WORKFLOW.md` §2.2.

---

## 5. Secret handling

**Never let an agent read real `.env` files.** The deny rules → `templates/claude/settings.json`;
scaffold it as is. Rules are written as `Edit(…)` only, never `Write(…)`: Claude Code
evaluates file permissions as `Edit(path)`, which covers every file-editing tool, so a
`Write(…)` rule is never evaluated and only prints a startup warning. That deny-list is
a guard against an agent's slip, not a security boundary →
`templates/private/WORKFLOW.md` §2.2. If the project has real env files beyond the
template's, add them to both `Read` and `Edit`.

**`.env.example` stays fully readable and editable** — it holds placeholders only,
and agents must be able to add a variable to it when they add a feature that needs
one. Denying it just means new env vars go undocumented.

Pair it with `.gitignore`: `.env*` ignored, `!.env.example` un-ignored.

---

## 6. The two subagents

### `pr-reviewer` — fresh eyes before every merge

Invoked by the implementer **after CI is green** and **before the PR is merged or
handed off**. Loops until PASS. Skipped only for trivial docs-only typo PRs.

Who merges is decided by the current merge stage, not by this verdict →
`templates/CLAUDE.template.md` → "Who merges".

It exists to catch what a linter structurally cannot: leftover `TODO`s and
`console.log`s, secrets in the diff, competitor brand names in public copy,
framework boilerplate left in place, accessibility regressions, scope creep (a PR
doing three unrelated things), a schema change with no migration, a destructive
migration with no reversibility note, a client-side file bypassing the data-access
rules, CI steps quietly weakened, a toolchain major bump with no build-output
comparison.

Verdict mapping is what makes it usable:
- any **BLOCK** → `BLOCK`
- any **MAJOR**, no BLOCK → `CHANGES REQUESTED`
- only **MINOR** or nothing → `PASS`

And, importantly, what it must **not** do: re-check what CI already checked, block
on aesthetics of deliberately-placeholder copy, or suggest "while you're here"
refactors. A reviewer that flags everything gets ignored.

Run it on a cheaper/faster model than the main agents — the checklist is
mechanical, and the value is the *fresh context*, not the reasoning depth.

### `doc-auditor` and `doc-lint`

Scaffold both as is. The duty they serve, the order (lint first, it is free), the
auditor's trigger and its marker → `templates/private/WORKFLOW.md` §2.5. What the
auditor hunts → `templates/claude/agents/doc-auditor.md`. What the lint checks → the
docstring of `templates/private/tools/doc-lint.py`.

⛔ Archives are exempt from the lint's reference checks — they record what was true
when written, and chasing their pointers means rewriting the past. A line that
*describes* a broken pointer keeps it broken with the `<!-- lint:ok -->` suppression.

---

## 7. Framework-docs-first

A rule for the agents, enforced by the CLAUDE.md checklist rather than by
tooling, but a guardrail nonetheless:

> **Read the installed version's own docs before writing framework code — not your
> training data.**

Frameworks ship breaking changes between majors, and an agent's training data is
frozen. Writing a pattern that was correct two majors ago produces code that
*silently* does the wrong thing — the worst failure class, because it passes
review and CI. Point the rule at where the docs actually live for the project
(e.g. `node_modules/<framework>/dist/docs/`, or the pinned version's site).
