#!/usr/bin/env python3
"""doc-lint — the mechanical half of the doc audit.

Rationale (`WORKFLOW.md` §2.5): a constraint that can be turned into code that *fails*
is worth more than a rule an agent is supposed to remember. In the origin project,
three of the four findings of the first `doc-auditor` pass were mechanically checkable
and are checked here — in seconds, with no subagent and no tokens.

The checks:

1. section anchors resolve — every `<doc>.md §N` points at a numbered heading that
   exists. Scans the brain, the root doctrine files and this script's own messages.
2. every brain doc is listed in `INDEX.md`.
3. no dead doc links — backticked `path.md` and markdown `[text](path.md)` links, in
   the brain and the root doctrine files.
4. canonical facts are asserted once — in the brain and the root doctrine files.
5. brain filenames are unique — the bare-name fallback in checks 1 and 3 is only
   sound if they are.

"Root doctrine files" = `CLAUDE.md`, `AGENTS.md`, `.claude/lanes/*.md`,
`.claude/agents/*.md`. Any of them that does not exist is skipped silently.

What stays with `doc-auditor`: everything needing judgement — contradictions between
docs, a closed decision that quietly went false, deferred work living only in prose.

⛔ Archives are exempt from the reference checks. `baton-archive.md` and
`shipped-log.md` record what was true when written; a pointer that has since moved is
correct history, not drift. Chasing those would mean rewriting the past, which is the
opposite of what an archive is for. Add this project's own archives to ARCHIVES below.

To silence one line deliberately, end it with `<!-- lint:ok -->` — and only when the
line *describes* a fact rather than asserting it.

Run:  python .private/tools/doc-lint.py
Exit code 1 if anything failed.
"""

import glob
import io
import os
import re
import sys

# Windows consoles default to cp1252 and this script prints arrows: without this the
# run dies on its FIRST finding with a UnicodeEncodeError, which reads as a broken
# linter rather than as a found problem.
try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # .private/
REPO = os.path.dirname(ROOT)
BRAIN = os.path.relpath(ROOT, REPO).replace('\\', '/')  # '.private'

# 🔴 Identifier scheme, used by every check: a file is identified by its path
# RELATIVE TO THE REPO ROOT, with forward slashes (`.private/operations/backlog.md`,
# `CLAUDE.md`, `.claude/agents/doc-auditor.md`). Paths written inside docs and in
# CANONICAL are turned into that form by `resolve()`; nothing is ever compared by
# basename, except a bare filename, which resolves against the brain only.

SKIP_DIRS = {'.git', 'for-owner', 'archive', 'tools'}
ARCHIVES = {BRAIN + '/operations/baton-archive.md', BRAIN + '/operations/shipped-log.md'}
ROOT_DOCTRINE = ['CLAUDE.md', 'AGENTS.md', '.claude/lanes/*.md', '.claude/agents/*.md']
SELF = os.path.relpath(os.path.abspath(__file__), REPO).replace('\\', '/')
# Doc trees that are not ours; a link into them is not a dead link. SEED THIS with the
# vendored/framework doc trees this project actually links into (e.g. a framework's own
# docs under node_modules/), or the linter will report every such link as dead.
FOREIGN_PREFIXES = ('node_modules/',)
# Links that resolve to something real OUTSIDE the repo, or that are written as a bare
# filename that is not a brain doc. Keep this NARROW and explicit — one line per entry,
# each one a deliberate exemption. ⚠️ Never replace it with a sweep that matches any
# file by basename anywhere on the machine: that makes the dead-link check pass on
# anything as long as a file by that name exists somewhere.
ALLOW_LINKS = set()
SUPPRESS = '<!-- lint:ok -->'

# Facts with exactly one home. Anything else asserting them violates single-source
# (`WORKFLOW.md` §2.1). The home is written relative to `.private/` for a brain doc
# (`operations/infrastructure.md`) or relative to the repo root for anything else
# (`CLAUDE.md`).
# SEED THIS with the facts your project will actually act on — the ones where a stale
# paraphrase makes an agent operate on the wrong system. Two examples:
#
#   (re.compile(r'on the (?:Team|free) plan', re.I),
#    'which billing plan the org is on', 'operations/infrastructure.md'),
#   (re.compile(r'45\s*(?:of the last|de)\s*45', re.I),
#    'the "45 of 45 merged green" measurement', 'CLAUDE.md'),
#
# Keep the patterns narrow: match assertions of current state, not narration about
# the past, or the linter will fight every doc that explains its own history.
CANONICAL = [
]


def brain_docs():
    out = []
    for base, dirs, files in os.walk(ROOT):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for f in files:
            if f.endswith('.md'):
                out.append(os.path.relpath(os.path.join(base, f), REPO).replace('\\', '/'))
    return sorted(out)


def root_doctrine():
    out = []
    for pattern in ROOT_DOCTRINE:
        for path in glob.glob(os.path.join(REPO, pattern)):
            out.append(os.path.relpath(path, REPO).replace('\\', '/'))
    return sorted(out)


def read(ident):
    with io.open(os.path.join(REPO, ident), encoding='utf-8') as fh:
        return fh.read()


def lines(ident):
    for n, line in enumerate(read(ident).splitlines(), 1):
        if SUPPRESS not in line:
            yield n, line


def by_basename():
    names = {}
    for ident in brain_docs():
        names.setdefault(os.path.basename(ident), []).append(ident)
    return names


def resolve(path, source=None):
    """Return the repo-relative identifier `path` points at, or None.

    Tried in order: relative to the linking file's directory (markdown semantics,
    only when `source` is given), relative to `.private/`, relative to the repo root,
    and — for a bare filename only — the one brain doc with that name.
    """
    path = path.split('#', 1)[0]
    candidates = []
    if source:
        candidates.append(os.path.join(os.path.dirname(os.path.join(REPO, source)), path))
    candidates += [os.path.join(ROOT, path), os.path.join(REPO, path)]
    for c in candidates:
        if os.path.isfile(c):
            return os.path.relpath(os.path.normpath(c), REPO).replace('\\', '/')
    if '/' not in path:
        hits = by_basename().get(path, [])
        if len(hits) == 1:
            return hits[0]
    return None


def check_section_anchors(problems):
    targets = {}
    for ident in brain_docs() + root_doctrine():
        nums = set()
        # The optional letter matters: `## 1.4b` is a real section, and without it the
        # trailing \b never matches and every `§1.4b` reads as missing.
        for m in re.finditer(r'^#{2,4}\s+§?([0-9]+(?:\.[0-9]+)?[a-z]?)\b', read(ident), re.M):
            nums.add(m.group(1))
            nums.add(m.group(1).split('.')[0])
        targets[ident] = nums

    ref = re.compile(r'`?([A-Za-z0-9_./-]+\.md)`?\s*(?:→\s*)?§\s*([0-9]+(?:\.[0-9]+)?[a-z]?)')
    sources = [d for d in brain_docs() if d not in ARCHIVES] + root_doctrine() + [SELF]
    for ident in sources:
        for n, line in lines(ident):
            for m in ref.finditer(line):
                target, sec = resolve(m.group(1)), m.group(2)
                if target in targets and targets[target] and sec not in targets[target]:
                    problems.append(f'{ident}:{n} → `{m.group(1)} §{sec}` does not exist')


def check_index_complete(problems):
    index = read(BRAIN + '/INDEX.md')
    for ident in brain_docs():
        rel = ident[len(BRAIN) + 1:]
        if rel != 'INDEX.md' and rel not in index:
            problems.append(f'INDEX.md → does not list `{rel}` (WORKFLOW.md §2.1)')


def check_dead_links(problems):
    """Backticked `path.md` and markdown `[text](path.md)` links must resolve.

    Never by basename across the machine: a doc in the wrong folder must be
    distinguishable from a correct one, which is precisely the drift this check exists
    to catch. The one basename fallback is for a link written with NO path at all,
    resolved against the brain only (see `resolve`).
    """
    tick = re.compile(r'`([A-Za-z0-9_./-]+\.md)`')
    md = re.compile(r'\]\(([^)\s]+?\.md)(?:#[^)]*)?\)')
    sources = [d for d in brain_docs() if d not in ARCHIVES] + root_doctrine()
    for ident in sources:
        for n, line in lines(ident):
            found = [(m.group(1), None) for m in tick.finditer(line)]
            found += [(m.group(1), ident) for m in md.finditer(line)]
            for p, rel_to in found:
                if '://' in p or p.startswith(FOREIGN_PREFIXES) or p in ALLOW_LINKS:
                    continue
                if resolve(p, rel_to) is None:
                    problems.append(f'{ident}:{n} → references `{p}`, which does not exist')


def check_canonical_facts(problems):
    sources = [d for d in brain_docs() if d not in ARCHIVES] + root_doctrine()
    for pat, name, home in CANONICAL:
        home_id = resolve(home) or home
        for ident in sources:
            if ident == home_id:
                continue
            for n, line in lines(ident):
                if pat.search(line):
                    problems.append(
                        f'{ident}:{n} → asserts {name}; its only home is `{home}` (WORKFLOW.md §2.1)')


def check_unique_names(problems):
    for name, idents in sorted(by_basename().items()):
        if len(idents) > 1:
            problems.append(f'`{name}` names {len(idents)} docs: {", ".join(idents)} '
                            f'— a bare `{name}` link cannot tell them apart')


def main():
    checks = [('section anchors resolve', check_section_anchors),
              ('every doc is in INDEX.md', check_index_complete),
              ('no dead doc links', check_dead_links),
              ('canonical facts asserted once', check_canonical_facts),
              ('brain filenames are unique', check_unique_names)]
    failed = 0
    for label, fn in checks:
        problems = []
        fn(problems)
        if problems:
            failed += len(problems)
            print(f'\n[FAIL] {label} — {len(problems)}')
            for p in problems:
                print(f'  {p}')
        else:
            print(f'[ok]   {label}')
    print()
    if failed:
        print(f'{failed} problem(s). Mechanical only — `doc-auditor` still owns '
              f'contradictions, stale decisions and untracked loose ends.')
        return 1
    print("Clean. Judgement-level drift is still doc-auditor's job.")
    return 0


if __name__ == '__main__':
    sys.exit(main())
