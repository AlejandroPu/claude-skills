# Infrastructure — canonical inventory

**This is the single source of truth for every external-infrastructure fact.**
Other docs **link** here; they never restate. A paraphrase in a second doc is how
copies desync, and an agent eventually operates on the stale one.

> Real near-miss from the project this workflow came from: the domain registrar and
> the DNS host were two different companies. One doc said "DNS lives at the
> registrar". An agent almost edited records in the wrong dashboard.
>
> **Registrar ≠ DNS host ≠ mail host ≠ app host.** Write them as separate,
> explicit lines, even when they happen to be the same company today.

**Before you operate on any of this, re-verify it.** This doc tells you what was
true when it was written.

---

## Provider map

| Concern              | Provider | Notes / where to click |
| -------------------- | -------- | ---------------------- |
| Domain registrar     | —        |                        |
| DNS host             | —        | ← records are edited HERE |
| App hosting / deploy | —        |                        |
| Database             | —        |                        |
| Auth                 | —        |                        |
| Object storage       | —        |                        |
| Transactional email  | —        |                        |
| Mailbox (humans)     | —        |                        |
| Payments             | —        |                        |
| Error/analytics      | —        |                        |
| Backups              | —        |                        |

## Repository

- Host / org / visibility: —
- Default branch + protection: —
- Required CI check name: —

## Environments

| Env        | URL | Deploys from |
| ---------- | --- | ------------ |
| production | —   | —            |
| preview    | —   | —            |

## DNS snapshot

_(Record type, name, value, and what depends on it. Update after every change.)_

| Type | Name | Value | Purpose |
| ---- | ---- | ----- | ------- |
| —    | —    | —     | —       |

## Secrets and where they live

_(Names only — never values. Which vault/dashboard holds each, and which surfaces
need it: CI, the host's env vars, the local `.env.local`.)_

| Variable | Lives in | Needed by |
| -------- | -------- | --------- |
| —        | —        | —         |
