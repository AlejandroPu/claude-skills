# How we work — the living layer

> **The foundation, and deliberately the shortest file in the brain.** Rules in
> force, nothing else.
>
> 🔴 **Pruned, never appended.** A rule that stops applying is **deleted** — not
> struck through, not marked resolved, not moved to a "closed" section. History is
> recoverable from the local backstop repo (`git --git-dir=.localgit log`); this
> file is only what is true now. **If it ever needs a table of contents,
> it has already failed.**
>
> Opened {{TODAY}} by {{OWNER}} + {{PLANNER}}.

---

## 1. Why this exists

> Replace this section with **your own measurement** the first time the brain feels
> heavy. Numbers are what make the rules below stick; inherited numbers are not.
> Measure: the word count of everything the session-start checklist mandates, the
> word count of the whole brain, and the biggest three files.
>
> The rules below were derived from an origin project where that mandatory preamble
> had reached **78,751 words**, 70% of it a single file that was specified as both
> append-forever and always-read.

🔴 **Load is not the disease; duplication is.** In the origin project the agent read
all of those words and still repeated a false claim — because the claim was *inside*
what it read. With a duplicated fact, reading **more** raises the odds of hitting the
stale copy. Volume is what makes duplication impossible to see.

---

## 2. The rules in force

### 2.1 One fact, one home

Each fact lives in exactly one canonical doc; everything else links. It earns its
keep hardest on facts an agent will **act** on — infrastructure, providers, the plan
you are on, credentials' whereabouts.

**What decides where a fact goes: is it stable or volatile?** A rule that does not
change earns its place in the doc where it is read. A fact that changes gets a home
and a pointer.

🔴 **The tell is a stable rule justified by a volatile fact.** In the origin project
the root instructions file broke twice that way: it justified "nothing reaches the
default branch without a PR" (stable) with which billing plan the org was on
(volatile).

⚠️ **A spec that edits doctrine must first grep for every copy of it.** In the origin
project the planner listed the two places it had read and missed two more in the
auto-loaded file — both of which then contradicted the new rule from the file that
loads every session.

**An index is the sharp case: it points, it does not summarise.** Paths and when to
read them — never status, never as-built detail, never a decision. When one
summarised, it stopped being maintained *as an index*: 70 verbose rows about shipped
work, 2 dead references, and **27 real docs listed nowhere**.

### 2.2 What counts as evidence

**An absence is a question, not a finding.** A zero, a null column, an empty table
means *nothing happened here*. It does not say why. Never build a causal story on
one — check whether the mechanism even existed yet, and if the answer lives outside
the repo, ask.

**A track record is evidence only when the failure would have been visible.** Ask
the base rate before proposing any guard — then ask what that answer is worth:

- **A direct push to the default branch:** git records it instantly. Months of zero
  is real evidence, and "no mechanism needed" is a sound conclusion.
- **A leaked secret:** no log says "this left". "It has not happened to us" cannot be
  told apart from "it happened and we never knew."

⚠️ So a deny-list on secret files is a guard against an agent's slip, **not a
boundary**. Permission rules are probabilistic; the boundary is the environment:
production values live in the deployment platform and the human's password manager
and **never enter the workspace the agent runs in**.

### 2.3 Ask what lives in the human's head; decide what is technical

- **Technical calls are the agent's to make and to defend** — which file to split
  first, how to structure a fix, what to measure. Handing them back as questions
  makes the human a bottleneck on the work they brought you in for.
- **Facts about intent, history and the world outside the repo are theirs** and must
  be asked for, not inferred.
- The agent **argues** with a decision it believes is wrong, once, with reasons —
  then executes the human's call in full.

⚠️ **Deference and invention are the same bug, mirrored**, and they show up in the
same session: asking permission for your own calls while asserting facts that were
never yours.

### 2.4 The handoff is where this system leaks

In the origin project, every failure of one review happened at a handoff, in both
directions: the implementer closed a cycle with "everything is clean, want to start
something else?", and the planner closed a session by repeating the implementer's
queue and dropping the human's. The implementer was **obeying its lane**, which said
"update the baton to a clean state" and ended on the signal that means *the human
acts next*.

**The baton is a channel, not an archive and not a manual.** It carries in-flight
state and the implementer's feedback. ⛔ The protocol (lanes, levels, signals, who
merges) is never restated inside it — it lives in `CLAUDE.md` and the lane files.

**Specs are born in `engineering/` (technical) or `product/` (UX), never in the
baton**, and stay there as the reference once shipped. The baton carries a pointer
and the next action. A spec drafted in the baton has to be promoted later, and a
promotion step is a step that gets skipped.

**The cycle, and the cadence of pruning inside it:**

> Human opens the implementer → **it implements and leaves feedback in the baton** →
> human returns to the planner → **the planner consumes it and only then prunes.**

- **The implementer writes feedback before ending**: what the spec left open and how
  it decided, what it found that the spec did not anticipate, what it deliberately
  did **not** do and why.
- **It hands back to the planner** (🛑), not to the human. The done signal (✅) is
  only for when the human genuinely acts next — typically merging a PR the current
  merge stage assigns to them.
- ⛔ **It never picks the next front.** That is planning.
- ⛔ **It never prunes.** The planner prunes on pickup, every pickup, as the first act
  of the session: promote what is durable (status doc, backlog, the spec), then move
  the entry verbatim to `operations/baton-archive.md`. ⚠️ **Nothing leaves until it
  has been read.** Periodic cleanup has been measured and it fails: in the origin
  project a baton pruned 745 → 140 lines was back to 744 in 25 days.
- **A stale channel costs work, not tidiness.** In the origin project an inbound note
  sat in the baton announcing a feature as an opportunity; it had shipped five weeks
  earlier, and a session offered the human work already done.
- **After a merge there is nothing to wait for** — say so explicitly in the lane, or
  the implementer will sit waiting on a non-blocking check.
- **What waits on the human is not in the baton** → `operations/owner-queue.md`, and
  it is never reconstructed from the implementer's list at closing time.

### 2.5 The planner updates the docs on pickup; the tools only help

📌 **The duty is the planner's and it comes first.** The subagent finds drift; it is
not the duty, and treating it as the ritual is how "I didn't run the auditor" becomes
the excuse for docs nobody updated.

**Run the lint first — it is free.** `tools/doc-lint.py` checks in seconds what needs
no judgement; its docstring lists the checks. In the origin project it caught three
of the four findings of the first auditor pass. **A constraint turned into code that
fails beats a rule an agent must remember.**

**Then the auditor, on a marker, when the trigger fires.** {{PLANNER}} launches it;
the trigger is change, not the calendar:

- commits since `operations/last-audit.md`, **and** the last pass was not today;
- **or**, ignoring that floor, a doctrine file changed (root instructions, lanes,
  agent definitions, this file, the index).

⛔ Never with zero commits since the marker. **{{PLANNER}} updates the marker in the
same turn the pass ends**, from the commits the report names, whatever it found.

**No file is both append-forever and mandatory reading** — the file always wins. The
status doc holds **state**, edited in place; the **story** goes to the shipped log,
never appended to a file read every session. In the origin project the status file
was specified as both and reached 55,300 words, 70% of the startup cost.

### 2.6 Close what you are doing before opening another front

1. **A deferred item is written to `operations/backlog.md` the same turn it is
   deferred.** "Later / non-blocking / minor" said in chat and written nowhere is a
   lost loose end.
2. **Writing a loose end down is not closing it.** When one of those phrases shows
   up, the question is not *where do I file this* but *which kind is it*:
   - **a loose end of the task in hand → closed now**, in the same cycle;
   - **a new front found in passing → filed**, with the trigger that reopens it.

   📌 What makes this non-obvious is that **filing feels like closing** — a
   well-written ticket reads as a settled matter, and a backlog cannot tell the two
   apart. ⚠️ A trigger that never arrives is a dead item: in the origin project a
   security advisory was filed for "the next PR that touches the lockfile" when the
   plan of record never touched dependencies, so "next PR" meant never. And closing
   finds what filing does not — going to close that advisory revealed it was two.
3. **Rule 2 does not repeal rule 1.** Filing makes it safe to defer **the item**,
   never **the work** of the task in hand.

---

## 3. Plan in force

> Checkboxes. Delete what is done — this file is pruned, not archived.

- [ ] Measure the mandatory preamble and write §1 with real numbers.
- [ ] Seed `tools/doc-lint.py`'s canonical-facts list with the facts this project
      will actually act on.
