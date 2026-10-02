# Last `doc-auditor` pass

> **The marker the auditor scopes against.** It reads the commits below, diffs the
> brain and the repo from there to HEAD, and audits what changed. Without it every
> pass is a full sweep — which is what makes passes too expensive to actually run.
>
> **Update this in the same turn a pass finishes** — {{PLANNER}} does, from the
> auditor's report — whatever it found.

---

**Last pass:** _never run._

**Baseline commit (brain, `.localgit`):** —
**Baseline commit (repo):** —

_(Two different histories: never copy one value into the other. {{PLANNER}} writes
both from the first report.)_

## What it found

_(one line per finding, and what was done about it — deleted once acted on)_

## What the next pass should know

_(work that is known and pending, so it is not re-reported as drift)_
