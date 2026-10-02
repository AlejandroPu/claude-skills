# Claude Code skills

Two [Claude Code](https://code.claude.com/docs) skills, extracted from real
production projects built with coding agents across many sessions. Most of their rules
come from something that went wrong at least once, and say so.

**How this was made, in full transparency.** Since around May 2026 I have built almost
everything on my GitHub with Claude Code, complemented with Codex/ChatGPT or
Antigravity/Gemini — this README included. These skills are the process that came out of
it. The Colossus workflow was born on [LookThis.One](https://www.lookthis.one), which runs
on Vercel and Supabase among other tools — Hostinger only hosts its mailboxes. It grew
later with [cerebritos.cl/games](https://www.cerebritos.cl/games/). The Hostinger skill
was created for that project and others like it that are hosted on Hostinger.

| Skill | What it sets up |
| --- | --- |
| [`bootstrap-colossus-workflow`](bootstrap-colossus-workflow/SKILL.md) | **The process.** A two-terminal planner/implementer workflow, a private project brain, review subagents and the guardrails that keep it honest. |
| [`hostinger-static-hosting`](hostinger-static-hosting/SKILL.md) | **The platform.** Where a static site lives on Hostinger (or any cPanel shared host), and a GitHub Actions deploy that cannot misfire. |

They complement each other and neither depends on the other.

---

## Install

A skill is a folder with a `SKILL.md`. Copy the one you want to either place:

```bash
# for you, in every project
cp -r bootstrap-colossus-workflow ~/.claude/skills/

# for one project only (commit it and the whole team gets it)
cp -r bootstrap-colossus-workflow <your-project>/.claude/skills/
```

Claude picks a skill up on its own when the request matches its description ("set up the
Colossus workflow", "deploy to Hostinger"), or you can call it directly:
`/bootstrap-colossus-workflow`, `/hostinger-static-hosting`.

---

## `bootstrap-colossus-workflow`

Coding agents lose their context at the end of every session; the human is the only
continuous thread. This workflow is built so that any session can be resumed cold.

**The ideas it rests on:**

- **Two terminals, split by role, never by capability.** A *planner* designs and writes
  specs; an *implementer* builds and ships. The split keeps planning context and build
  context from contaminating each other. Only one runs at a time, and the human declares
  which one each terminal is.
- **A written handoff channel** (the *baton*): a gitignored file that carries what is in
  flight and the implementer's feedback, and is pruned by the planner on every pickup.
- **A project brain** (`.private/`, gitignored): a short rules layer, an index, the
  backlog, what is live vs only designed, what waits on the owner, and one canonical home
  for every infrastructure fact.
- **Task levels that describe the task, not the model.** `easy`, `normal`, `sensitive` —
  and only irreversibility makes something `sensitive`. Which model runs each level is
  deliberately left to the human.
- **A merge gate that opens as trust is earned.** Stage 1: the owner merges every PR.
  Stage 2: the implementer merges what a machine can fully judge; the owner keeps what the
  end user sees.
- **Guardrails that fail loudly:** a local `verify` that mirrors CI, a `pr-reviewer`
  subagent before every merge, a `doc-auditor` subagent that hunts drift, and a
  `doc-lint.py` that checks the mechanical half in seconds.

**What it scaffolds:** `CLAUDE.md`, `AGENTS.md`, `.claude/` (settings, two lane files, two
subagents), `.private/` (the brain), `.github/workflows/ci.yml`, `.github/dependabot.yml`,
and a local git backstop for everything the host never sees. It comes in two profiles:
**core** (the lanes, the baton, the backlog, `pr-reviewer` and the guardrails — for a page
or a tool) and **full** (core plus the index, the status doc and shipped log, the
`doc-auditor` and `doc-lint.py` — for a product whose brain has enough docs to drift). It
interviews you first (role names, languages, profile, merge stage and branch protection,
timezone), and merges into an existing `CLAUDE.md`, `.claude/` or `.private/` instead of
overwriting it.

**Needs:** git, a GitHub repo with the `gh` CLI, and Python 3 for `doc-lint.py`. The CI
template is Node/TypeScript; the skill says how to translate it to other stacks.

**Not for:** a one-session spike or a throwaway script. The workflow's whole value is
surviving across sessions; below that horizon it is overhead.

**How it stays current.** Every so often I research new recommendations for working with
Claude Code, running the findings back and forth between ChatGPT and Claude Code, and
update the skill with what holds up — adapted to my current project and resources. Right
now that is a laptop and Claude Code inside Cursor, using two terminals.

---

## `hostinger-static-hosting`

The platform half of starting a project: where the built site lands and how it gets there.

**What it covers:**

- **The decision that comes first:** the document root on disk and the URL prefix are two
  separate questions, and the three hosting shapes that follow from them — including the
  one that looks like a subfolder on disk but behaves like a root on the web.
- **A guarded deploy** (GitHub Actions → `rsync` over SSH): checks and deploy in one
  workflow, a guard that refuses a wrong destination or an empty build before the key is
  even loaded, a pinned host key instead of `ssh-keyscan`, a retry for connection failures
  only, and a final step that asks production which commit it is serving.
- **The traps that fail silently:** `.well-known` redirected (TLS breaks weeks later),
  `rsync --delete` against a shared folder, redirect loops and `http://` downgrades.

**Needs:** a site that builds to static files (the skill assumes no Node.js at runtime),
SSH access to the host, and GitHub Actions.

---

## Using both

On a new project deployed to Hostinger, load both. They meet in two places, and each skill
says how to handle them so nothing is written twice: **one** `ci.yml` (the Colossus checks
merge into the deploy workflow's `quality` job) and **one** infrastructure doc.

## License

[MIT](LICENSE)
