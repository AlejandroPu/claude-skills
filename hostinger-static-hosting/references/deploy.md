# The deploy — GitHub Actions → rsync over SSH

The goal is a deploy that **cannot misfire**, not one that usually works. Everything below exists
because of a specific way this goes wrong. `templates/ci-deploy.yml` is the working version of it.

## Shape: ONE workflow, not two

Checks and deploy live in the **same workflow file**, with the deploy job declaring
`needs: [<check jobs>]`.

🔴 **This is not tidiness, it is the only thing that makes the race impossible.** `needs:` only works
between jobs of one workflow. Two separate workflows both triggered by `push: main` are independent
runs: a merge with failing lint, types or tests still ships, because the deploy does its own build
and if it compiles, it goes live. Discipline is then the only thing in the way.

⚠️ **Do not reach for `workflow_run:` to link two workflows.** It runs the workflow file from the
default branch, checks out the wrong ref by default, and its conclusion handling is a known footgun.

⚠️ **Trigger `pull_request` with NO branch filter.** `pull_request: branches: [main]` fires only for
PRs whose *base* is `main`, so a PR stacked on another PR's branch gets **no CI at all** — and nothing
says so; the PR simply shows no checks. The deploy job keeps its own `if: … refs/heads/main`, so
widening the trigger cannot widen what deploys.

📌 **The deploy job rebuilds instead of downloading the checked build.** Deliberate: same commit, same
lockfile, and the deploy job stays self-contained. If the build is ever non-deterministic, switch to
uploading the output as an artifact from the check job.

## The guard step — the one thing not to ship without

`rsync --delete` makes the destination an **exact mirror** of the source. Two things turn that into a
disaster, and **neither requires a bad merge**:

1. **A wrong DESTINATION** wipes the neighbours. In a shared document root, the deploy path secret is
   the only thing keeping the mirror off other people's folders — including files that exist in no
   repo and have no git copy.
2. **An empty SOURCE** wipes *you*. A build that silently produced an empty or half-empty output
   directory mirrors that emptiness over the live site and deletes it. No secret touched, no human
   error — just a bad build.

So the workflow **refuses to run** in either case:

- assert the deploy path still ends in **your own folder** (a document root that is entirely yours is
  pinned as an exact path, never a wildcard);
- assert the build output has its entry file, non-empty;
- assert the output has a plausible number of files.

🔴 **The guard runs BEFORE the deploy key is loaded.** The checks are cheap and secret-free, so a
doomed job never even receives the private key. Keep that ordering if you touch the file.

## The host key is PINNED, not scanned

Use a `SSH_KNOWN_HOSTS` secret holding the server's host key. **Do not use `ssh-keyscan` in the
workflow.**

Scanning asks the server for its own key on every run, believes whatever comes back, and then uses
that answer to "verify" that same server — **trust-on-first-use on every deploy**, which makes the
check decorative. It is also a network call that fails **safe but silent**: a scan that exhausts its
retries skips the rsync, so a fix can sit merged and green on `main` while production keeps serving
the bug.

Pinning removes the call and makes the check real: if anything ever answers on that host and port
with a different key, the deploy **refuses** instead of shrugging.

### How to obtain the key you pin — from a trusted network, twice

A CI runner is **not** a trusted channel for this; the point is to get the key somewhere the runner
cannot influence. Use the owner's own machine:

1. **Two independent observations must agree:** the entry already in the owner's `~/.ssh/known_hosts`
   from their first SSH login, and a fresh `ssh-keyscan -p <port> <host>` on a different day. Same
   key both times ⇒ pin it. One observation is a guess.
2. **Pin only the `ssh-ed25519` line** — the strongest type, and what the client negotiates by default.
3. ⚠️ **The port is part of the line.** On a non-22 port the entry must read
   `[<host>]:<port> ssh-ed25519 AAAA…`. A plain `<host> ssh-ed25519 …` line does not match a
   connection on another port, and the deploy fails with `Host key verification failed` — which looks
   exactly like a rotated key. `ssh-keyscan -p` already emits the bracketed form.
4. **Record how it was verified** (both dates) in the infrastructure doc. A key whose provenance is
   unknown is the one someone "fixes" by going back to scanning.

**When the host key legitimately rotates**, the deploy fails loudly — that is the feature. Repeat the
procedure and update the secret in **every** repo that deploys to that host.

## Secrets

| Secret | What it is |
|---|---|
| `SSH_HOST` | the server hostname or IP, from hPanel |
| `SSH_PORT` | ⚠️ **not 22.** Hostinger shared hosting uses a non-standard port (commonly 65002) — **read it from hPanel, do not copy this number** |
| `SSH_USER` | the SSH account, typically `u…` |
| `SSH_PRIVATE_KEY` | a **deploy key generated for this repo**, not a personal key |
| `SSH_KNOWN_HOSTS` | the pinned host key (see above) |
| `DEPLOY_PATH` | the **absolute** path of the folder that belongs entirely to this repo |

**One key per repo.** If two repos deploy to two folders of the same account, give each its own key
and its own `DEPLOY_PATH`, so a mistake in one cannot reach the other's folder.

## Pin the action that receives the private key — by commit, not by tag

`webfactory/ssh-agent` is handed `SSH_PRIVATE_KEY`. A tag like `@v0.10.0` is a movable pointer: whoever
controls that repository can repoint it, and the next deploy runs their code with your key. Pin the
full commit SHA and keep the version in a comment:

```yaml
uses: webfactory/ssh-agent@<40-char commit sha> # v0.10.0
```

Resolve the SHA yourself, never copy it from a doc (including this one):
`gh api repos/webfactory/ssh-agent/git/ref/tags/<tag> --jq '.object.type+" "+.object.sha'`. If the
type is `tag` (annotated) rather than `commit`, dereference once more:
`gh api repos/webfactory/ssh-agent/git/tags/<sha> --jq .object.sha`.

The same applies to any third-party action that sees a secret. The first-party `actions/*` steps in
the template see none.

## rsync

```
rsync -rlptvz --delete -e "ssh -p $PORT -o ConnectTimeout=15" ./<build-output>/ user@host:$DEPLOY_PATH
```

- **The trailing slash on the source matters.** `./dist/` copies the *contents*; `./dist` would copy
  the directory itself into the target, one level too deep.
- `-rlptvz` preserves permissions and times but **not owner/group** — shared hosting cannot `chown`,
  and asking it to (`-a`) produces noise or failures.
- `--delete` only ever appears when the target belongs entirely to this repo. Everywhere else, drop
  it and accept that removed files linger.
- `-o ConnectTimeout=15`: without it a silent host burns about two minutes per attempt.

### Retry the CONNECTION, never the credentials

Shared-hosting SSH occasionally times out, and a red deploy right after a merge **looks like the PR's
fault**. So the step retries — narrowly:

- **Retry only a recognised connection failure** (`Connection timed out`, `Connection refused`,
  `Connection reset by peer`, `Network is unreachable`, `No route to host`, `Broken pipe`). It is an
  allow-list: anything not on it fails immediately.
- **Never retry an authentication or host-key failure** (`Permission denied`,
  `Host key verification failed`, `REMOTE HOST IDENTIFICATION HAS CHANGED`). A broken deploy key or a
  rotated host key must stay red on the **first** attempt — that is exactly what a blind retry hides.
- **Decide by the message, not the exit code:** `ssh` returns 255 for a timeout *and* for
  `Permission denied`.
- **Bounded and loud:** 3 attempts (backoff 10 s, 30 s), every attempt announced, and exhausting them
  fails with the count in the log, so a persistent outage never looks transient.

Test the loop before shipping it: a fake `rsync` early on `PATH` that prints each message and exits
non-zero covers every branch without touching a server.

### During a normal run the live site is half-written — test before narrowing that window

By default rsync deletes and replaces files **while** it transfers. For a site with hashed assets, a
visitor can for a few seconds load an old HTML page whose old JS/CSS was just deleted, or a new page
whose assets have not arrived yet.

`--delay-updates --delete-delay` narrows that to the final rename pass: updated files are staged in
`.~tmp~` directories and moved into place at the end, and deletions are computed during the transfer
but applied after it.

⚠️ **Do not adopt it untested.** The staging directories live inside the public document root while
the transfer runs. Before switching the production step, run a throwaway job **on the CI runner** (it
has rsync; a developer machine may not, and should not need a container for this) that mirrors one
local directory into another and asserts that the final tree matches the source exactly, removed
files are gone, and no `.~tmp~` directory is left behind — **including after a transfer killed midway
and then re-run.** Only then change the deploy step.

## Concurrency

Give the deploy job a `concurrency` group with `cancel-in-progress: false`.

Without it, two merges in quick succession are two whole-tree rsyncs into one folder, and **the one
that finishes last wins** — if the earlier merge's transfer finishes second, production holds the
older tree with both runs green. With the group, the running deploy finishes and only the **newest**
queued run goes next (an older queued run is cancelled, which is correct: the newest tree contains
it). Never `cancel-in-progress: true` here — cancelling mid-transfer leaves the site half-written.

## After the rsync — ask production, not GitHub

🔴 **A green merge is not a deploy, and from outside a failed deploy is indistinguishable from one you
have not reloaded yet.** The site keeps serving the previous version with no error, and whoever
notices is usually the owner, late.

So the workflow proves the deploy landed:

1. Before the guard, stamp the build: `printf '%s\n' "$GITHUB_SHA" > <BUILD_DIR>/version.txt`. A
   commit SHA is safe to publish.
2. After the rsync, fetch `<SITE_URL>version.txt` with a cache-busting query and **require it to equal
   `$GITHUB_SHA`**, retrying a few times for server-side caches; also require `<SITE_URL>` itself to
   answer 200.
3. A mismatch fails the job. Green now means live.

When reconciling a ship by hand the same rule holds: read the **deploy job's** conclusion (not the
check jobs'), and confirm the change is actually visible on the live URL.

## After a failed deploy

A red deploy is not automatically a bad diff. If the check jobs are green and the log shows the retry
loop exhausted on connection failures, **the code was fine and the transfer was not**: re-run the
failed job (`gh run rerun <id> --failed`) before looking at the diff. If it keeps recurring it is
infrastructure, not the PR — and the attempt counts in the logs are the evidence to show the host.

📌 **Before building a failure alert, check the one you may already have.** GitHub can email the
account that triggered a run when it fails (*Settings → Notifications → Actions*). If merges are made
from that account, confirm whether those emails arrive before adding another channel.
