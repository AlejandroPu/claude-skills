# Infrastructure — <PROJECT>

> **The coordinates, in one place.** Everything here is **measured**, never assumed. When a line
> here disagrees with the server, the server is right and this file is stale — fix it the same day.
>
> ⚠️ **No private keys, no passwords, no tokens in this file.** Public keys and paths only; secrets
> live in the CI secret store and nowhere else.

## Hosting

| | |
|---|---|
| Provider / plan | Hostinger <plan> |
| Domain | `<domain>` |
| **Document root (on disk)** | `<absolute path>` |
| **URL prefix (as served)** | `<https://…/>` |
| **Shape** | sole owner · subfolder of a shared root · root that IS a subfolder |
| **Deploy target** | `<absolute path that belongs ENTIRELY to this repo>` |
| SSH host / port / user | `<host>` · `<port — read from hPanel, NOT 22>` · `<user>` |
| Runtime available | static files + PHP <version> + MySQL. **No Node.js at runtime.** |

📌 **Record how each of these was OBTAINED**, not just its value — panel screen, `pwd` over SSH, a
browser request. A coordinate whose provenance is unknown is a coordinate nobody dares to change.

## ⚠️ Neighbours in the document root — what a bad `--delete` would destroy

> Fill this in **before the first deploy**, by listing the document root over SSH. This table is the
> answer to "is `--delete` safe?", and it is the reason the guard step in CI is written the way it is.

| Folder | Owner | Notes |
|---|---|---|
| `<…/ours>` | **US** | rsync `--delete` target. |
| `<…/other>` | ⚠️ someone else | What it is, who depends on it, **and whether it exists in any repo.** If it does not, git cannot restore it — only the panel's backup can. **Do not touch, do not "clean up".** |

## Backups — the restore path

hPanel takes them automatically. **A backup is a way back, not a permission:** the deploy guards are
prevention and stay the first line. Anything of ours regenerates from a build; anything outside our
folder is someone else's project restored by hand.

## CI secrets (names only — values live in GitHub)

`SSH_HOST` · `SSH_PORT` · `SSH_USER` · `SSH_PRIVATE_KEY` (deploy key, this repo only) ·
`SSH_KNOWN_HOSTS` (**pinned** host key) · `DEPLOY_PATH`

**Deploy public key** (safe to record here): `<ssh-ed25519 …>`

**Pinned host key** (public by nature): `[<host>]:<port> ssh-ed25519 <AAAA…>` — the port is part of
the line. **How it was verified:** `<date 1>`, the owner's `~/.ssh/known_hosts` from their first login;
`<date 2>`, a fresh `ssh-keyscan -p <port> <host>` from the owner's machine. Same key both times.
**Set in:** `<every repo that deploys to this host>`.

**Host key rotation:** the pinned-key step fails loudly. Repeat the two-observation check from a
trusted network, update the secret in every repo above. **Never** replace it with `ssh-keyscan`.

**Deploy action pin:** `webfactory/ssh-agent@<sha>` = `<tag>`, resolved `<date>` with `gh api`.

## `.htaccess` — who owns which

| File | Owner | Applied how |
|---|---|---|
| `<document root>/.htaccess` | <us / the owner, by hand> | <deploy / by hand, with the rollback written first> |
| `<our folder>/.htaccess` | us | ships with the deploy; keep it minimal |

**Rollback for any hand-applied rule:** write it down *before* applying — normally "delete these N
lines". No deploy, no CI, immediate.

## Verified behaviour (re-measure after any redirect change)

- Bare domain → `<n>` hop(s) to the canonical host, **all `https://`**.
- `/.well-known/<anything>` answers **404, not 301**, on every host the domain answers on.
- `<the URL prefix>` serves the built site.
- `<the URL prefix>version.txt` equals the commit of the last green deploy (the deploy job checks this
  itself; this line is for a hand check).
