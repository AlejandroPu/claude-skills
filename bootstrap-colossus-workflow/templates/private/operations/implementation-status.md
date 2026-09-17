# Implementation status

**Source of truth for what is LIVE vs what is only DESIGNED.** The specs
(under `product/` and `engineering/`) describe the *target* system; this file
tracks the gap between target and reality.

🔴 **State, edited in place — never a log.** One line per capability that runs now,
rewritten when it changes. How it shipped, PR numbers and dates go to
`shipped-log.md` (`WORKFLOW.md` §2.5). Write it **as built**, not as designed: when the
two diverge, reality wins and the spec gets corrected.

It is the doc that answers "is this already done?" — and the reason a spec can be
trusted, or must be re-checked, before it is handed off.

---

## Live

_(What actually runs, one line per capability, pointing at its spec. Nothing ordered
by date.)_

- — (workflow scaffolded; no product code shipped yet)

---

## Designed, not built

_(Specs that exist but have not shipped. Point at the doc; do not restate it.)_

- —

---

## Known gaps

_(Things that are live but incomplete, plus bugs accepted for now. Each one should
also have a backlog entry with a trigger for revisiting it.)_

- —
