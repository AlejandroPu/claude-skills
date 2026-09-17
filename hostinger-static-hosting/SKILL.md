---
name: hostinger-static-hosting
description: Decides and sets up where a static site lives on Hostinger shared hosting, and ships a guarded GitHub Actions deploy (rsync over SSH with a pinned host key). Covers the three hosting shapes — a document root that is entirely yours, a subfolder of a shared root, and a domain or subdomain whose document root IS a subfolder — plus the traps that are silent and expensive: rsync --delete against a shared folder, the .well-known exemption that breaks TLS renewal weeks later, and http downgrades in redirect chains. Use when starting a project that will be hosted on Hostinger (or any cPanel shared host), when wiring its deploy, or when adding a second project to a domain that already serves something. Triggers on "deploy to Hostinger", "public_html", "shared hosting", "rsync deploy", "where does this site live", "set up the Hostinger deploy".
---

# Hostinger static hosting

## What this is, and what it is not

This is the **platform** half of starting a project: *where the built site lands, and how it gets
there*. It is the complement to `bootstrap-colossus-workflow`, which is the **process** half — how
terminals hand work to each other, how the brain is structured, how PRs flow.

**The seam, stated once so nothing is written twice:**

| Question | Owner |
|---|---|
| How do we work across sessions? Who merges? What goes in the brain? | `bootstrap-colossus-workflow` |
| Where does the built site live? How does it get there? What can destroy it? | **this skill** |

⚠️ **Neither skill depends on the other to be useful.** Load both at the start of a Hostinger
project; load this one alone if you only need the hosting decision.

**Out of scope on purpose:** how to build a static site (that is the framework's job), and
walkthroughs of the hPanel UI (they rot faster than anything else here).

---

## Invariants — true of Hostinger shared hosting, decide around them

1. 🔴 **This skill assumes NO Node.js at runtime.** Node exists on your machine at build time and in
   CI, and nowhere else. **Everything must build to static files** that are uploaded. A framework that
   needs a running server (SSR, API routes, middleware) is not deployable this way.
   ⚠️ **That is a property of the plan, not of Hostinger.** Hostinger's Business and Cloud plans can
   run managed Node.js web apps; Premium and the entry shared plans cannot. **Read the plan in hPanel
   before deciding** — and if the project genuinely needs a server, that is a plan decision for the
   owner, not something to route around.
2. **PHP and MySQL are available.** That is the escape hatch when something genuinely needs a
   server: private validation, keys, a database, anything that must not be in the browser. Do not
   add a backend before a feature actually requires one.
3. **hPanel takes automatic backups.** They are the restore path for anything that is not in a repo.
   They are *not* a reason to be careless: a restore is slow, manual, and often of someone else's
   files.
4. **Anything shipped to the browser is public.** No secrets in the repo, no secrets in the bundle.

---

## The decision that comes first — and it is two questions, not one

🔴 **Determine these SEPARATELY, and never infer one from the other:**

- **A. The document root on disk** — the absolute path Apache serves this domain from.
- **B. The URL prefix** — the path your app is served at, as a visitor types it.

They look like the same fact and they are not. Getting them confused is how a project ends up with a
wrong `base` (every asset URL broken) or a `--delete` aimed at a folder it does not own.

**How to answer them, without guessing:**

- **A** comes from hPanel (the domain's document root) or from `pwd` over SSH. Typical shape:
  `/home/<user>/domains/<domain>/public_html`. **Read it; do not assume `public_html` is the root of
  everything** — on Hostinger a domain's root is often *itself* a subfolder.
- **B** comes from the live URL. Load the site (or the folder you intend to use) in a browser.
- Then list the document root over SSH (`ls -la`) and **write down what else is in there.** That list
  is the answer to "is `--delete` safe?", and it is the single most important thing to know before
  the first deploy.

---

## The three shapes

| | **1. Sole owner** | **2. Subfolder of a shared root** | **3. Root that IS a subfolder** |
|---|---|---|---|
| **On disk** | `…/public_html/` is all yours | `…/public_html/<app>/` is yours; siblings are not | `…/public_html/<app>/` is the domain's document root |
| **Served at** | `https://site.com/` | `https://site.com/<app>/` | `https://app-site.com/` |
| **Framework `base`** | `/` | **`/<app>/`** | **`/`** |
| **`rsync --delete` target** | the document root — safe | **only `…/<app>/`** — never the root | its document root — safe |
| **Owns `.htaccess`?** | yes | **no** — the root one is shared, edited by hand | yes |
| **Canonical URLs** | `https://site.com/…` | `https://site.com/<app>/…` | `https://app-site.com/…` |

🔴 **Shape 3 is the one that catches people, and it is the normal case on Hostinger for an addon
domain or subdomain.** On disk it looks exactly like shape 2 — a folder inside `public_html` — but on
the web it behaves like shape 1. **If you read only the disk path you will set `base` to `/<app>/`
and break every URL on the site.** This is why A and B are two questions.

**Choosing between 1 and 2 when you have the option:** prefer a shape where **the deploy target
belongs entirely to one repo**. That single property is what makes `--delete` safe, makes rollbacks
trivial, and means a mistake can only damage your own project. A shared root is workable, but
every deploy then depends on a guard being correct.

---

## Then, in order

1. **Set the framework's `base`** to the answer from the table, and make links and assets base-aware.
   Get this right before writing pages: it is baked into every URL.
2. **Write the coordinates down first**, from `templates/infrastructure.md` — including the
   **inventory of neighbours in the document root**, which is what makes `--delete` a decision
   instead of a gamble. If using `bootstrap-colossus-workflow`, that file belongs at
   `.private/operations/infrastructure.md` — **and that skill scaffolds its own template for the same
   file. Keep ONE file:** its provider map stays on top, and this template's sections go under it
   (the provider map's "App hosting" row then just points down to them). Two infrastructure docs is
   the single-source violation both skills warn about.
3. **Wire the deploy** → `references/deploy.md`, and copy `templates/ci-deploy.yml`. Two steps are
   the ones not to ship without: the **guard** before the rsync, and the **production check** after
   it. Resolve the `ssh-agent` commit SHA yourself; the reference says how.
4. **Read the traps** → `references/traps.md`. They are short, and none of them is derivable.
   Anything touching the document root's `.htaccess` starts from `templates/htaccess-root.txt`.

## Files

| | |
|---|---|
| `references/deploy.md` | the deploy machinery and why each guard exists: guard, pinned host key and how to obtain it, SHA-pinned key action, connection-only retry, concurrency, the production check |
| `references/traps.md` | the seven things that fail silently |
| `templates/ci-deploy.yml` | a working guarded workflow — replace the `<…>` placeholders |
| `templates/htaccess-root.txt` | host canonicalisation, with the `.well-known` exemption |
| `templates/infrastructure.md` | the coordinates + the neighbour inventory |

⚠️ **Coordinates rot; invariants do not.** Ports, panel menus and paths must be **verified on the
server**, never copied from memory or from another project. The reasoning in this skill keeps; the
numbers in it are examples.
